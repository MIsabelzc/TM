import streamlit as st
import cv2
import numpy as np
from PIL import Image
from keras.models import load_model
import paho.mqtt.client as mqtt
import json
import platform

# -------------------------------
# CONFIGURACIÓN MQTT
# -------------------------------
broker = "broker.mqttdashboard.com"
port = 1883
topic = "santiagoV/cmqtt_a"

client = mqtt.Client("streamlit_face_access")
client.connect(broker, port, 60)

def enviar_mqtt(act, analog):
    """Envía mensaje MQTT al ESP32"""
    message = {"Act1": act, "Analog": analog}
    client.publish(topic, json.dumps(message))
    print("📤 Enviado al broker:", message)

# -------------------------------
# CONFIGURACIÓN DE INTERFAZ
# -------------------------------
st.set_page_config(page_title="Acceso Facial Inteligente", layout="centered")

# Fondo azul suave y estilo del texto
st.markdown("""
    <style>
    body {
        background-color: #0a192f;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .title {
        text-align: center;
        color: #64ffda;
        font-size: 2.5em;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: 700;
    }
    .subtitle {
        text-align: center;
        color: #ccd6f6;
        font-size: 1.1em;
        margin-bottom: 40px;
    }
    .welcome {
        text-align: center;
        font-size: 2em;
        color: #64ffda;
        font-weight: bold;
        margin-top: 30px;
    }
    .subtext {
        text-align: center;
        font-size: 1.2em;
        color: #a8b2d1;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# ENCABEZADO
# -------------------------------
st.markdown("<div class='title'>🔒 Sistema de Acceso Facial</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Reconocimiento de rostro con control IoT</div>", unsafe_allow_html=True)

# -------------------------------
# CARGA DEL MODELO
# -------------------------------
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# -------------------------------
# CAPTURA DE ROSTRO
# -------------------------------
st.subheader("📷 Escanear Rostro")
img_file_buffer = st.camera_input("Usa la cámara para validar tu identidad")

if img_file_buffer is not None:
    img = Image.open(img_file_buffer)
    img = img.resize((224, 224))
    img_array = np.array(img)
    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    prediction = model.predict(data)
    prob_isabel = float(prediction[0][0])
    prob_santiago = float(prediction[0][1])
    prob_desconocido = float(prediction[0][2])

    if prob_santiago > 0.7:
        st.markdown("<div class='welcome'>👋 Bienvenido Santiago</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtext'>Ya puedes pasar</div>", unsafe_allow_html=True)
        enviar_mqtt("ON", 100)
    elif prob_isabel > 0.7:
        st.markdown("<div class='welcome'>👋 Bienvenida Isabel</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtext'>Ya puedes pasar</div>", unsafe_allow_html=True)
        enviar_mqtt("ON", 50)
    else:
        st.markdown("<div class='welcome' style='color:#ff6b6b;'>🚫 No reconocido</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtext'>Intenta nuevamente</div>", unsafe_allow_html=True)
        enviar_mqtt("OFF", 0)

# -------------------------------
# ESPACIO PARA ENTRADA MANUAL (futura cédula)
# -------------------------------
st.markdown("---")
st.subheader("🖊️ Entrada Manual (Cédula o Firma)")
st.markdown(
    "<p style='color:#a8b2d1;'>Aquí podrás escribir o firmar para ingresar manualmente.</p>",
    unsafe_allow_html=True
)

# Espacio visual (aún no funcional)
canvas_placeholder = st.empty()
canvas_placeholder.write("🟦 (Zona de escritura — próximamente interactiva)")

# -------------------------------
# PIE DE PÁGINA
# -------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#64ffda; font-size:13px;'>"
    "Sistema desarrollado por <b>Santiago Velásquez</b> — Integración Facial + IoT"
    "</p>",
    unsafe_allow_html=True
)
