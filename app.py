import streamlit as st
import cv2
import numpy as np
from PIL import Image
from keras.models import load_model
import paho.mqtt.client as mqtt
import json
from streamlit_drawable_canvas import st_canvas

# -------------------------------
# CONFIGURACIÓN MQTT
# -------------------------------
broker = "broker.mqttdashboard.com"
port = 1883
topic = "santiagoV/cmqtt_a"

client = mqtt.Client("streamlit_access")
client.connect(broker, port, 60)

def enviar_mqtt(act, analog):
    """Envía mensaje MQTT al ESP32"""
    message = {"Act1": act, "Analog": analog}
    client.publish(topic, json.dumps(message))
    print("📤 Enviado al broker:", message)

# -------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------
st.set_page_config(page_title="Sistema de acceso inteligente", layout="centered")

st.markdown("""
    <style>
    body {
        background-color: #002b4f;
        color: white;
        font-family: 'Helvetica', sans-serif;
    }
    .title {
        text-align: center;
        color: #00c6ff;
        font-size: 36px;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #9adfff;
        margin-bottom: 30px;
    }
    .welcome {
        text-align: center;
        color: #00ffcc;
        font-size: 30px;
        margin-top: 30px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# MODELO DE RECONOCIMIENTO FACIAL
# -------------------------------
st.markdown("<div class='title'>Reconocimiento Facial</div>", unsafe_allow_html=True)
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

img_file_buffer = st.camera_input("📸 Toma una foto para ingresar")

if img_file_buffer is not None:
    img = Image.open(img_file_buffer).resize((224, 224))
    img_array = np.array(img)
    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    prediction = model.predict(data)
    if prediction[0][0] > 0.7:
        st.markdown("<div class='welcome'>Bienvenida Isabel 👩<br>Ya puedes pasar</div>", unsafe_allow_html=True)
        enviar_mqtt("ON", 100)
    elif prediction[0][1] > 0.7:
        st.markdown("<div class='welcome'>Bienvenido Santiago 👨<br>Ya puedes pasar</div>", unsafe_allow_html=True)
        enviar_mqtt("ON", 100)
    else:
        st.markdown("<div class='welcome' style='color:#ff6666;'>No reconocido ❌<br>Intenta de nuevo</div>", unsafe_allow_html=True)
        enviar_mqtt("OFF", 0)

st.markdown("---")

# -------------------------------
# APARTADO DE ACCESO POR CÉDULA
# -------------------------------
st.markdown("<div class='title'>Acceso Alternativo por Cédula</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>También puedes ingresar escribiendo tu número de cédula de forma táctil.</div>", unsafe_allow_html=True)

# 🎨 Canvas táctil (para dibujar números de cédula)
canvas_result = st_canvas(
    fill_color="rgba(255,255,255,0)",
    stroke_width=4,  # línea más delgada
    stroke_color="#FFFFFF",
    background_color="#003764",
    height=200,
    width=300,
    drawing_mode="freedraw",
    key="canvas_cedula",
)

# 📋 Lista de cédulas autorizadas (modifícala tú)
cedulas_autorizadas = ["1234567890", "9876543210", "1122334455"]

# ✏️ Campo de texto para escribir la cédula
cedula_ingresada = st.text_input("O escribe tu cédula manualmente:")

if st.button("Verificar cédula"):
    if cedula_ingresada in cedulas_autorizadas:
        st.success(f"✅ Cédula {cedula_ingresada} reconocida. Acceso permitido.")
        enviar_mqtt("ON", 100)
    else:
        st.error("🚫 Cédula no registrada. Acceso denegado.")
        enviar_mqtt("OFF", 0)

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#9adfff;'>Sistema de acceso inteligente v2.0 — Reconocimiento facial y táctil.<br>Desarrollado por Santiago Velásquez.</p>",
    unsafe_allow_html=True,
)
