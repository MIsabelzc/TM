import streamlit as st
import cv2
import numpy as np
from PIL import Image
from keras.models import load_model
import paho.mqtt.client as mqtt
import json
import platform
import time

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
# CONFIGURACIÓN STREAMLIT
# -------------------------------
st.set_page_config(page_title="Reconocimiento Facial", layout="centered")

st.title("🔍 Sistema de Reconocimiento Facial")
st.caption("Control automático de acceso mediante MQTT")

st.write(f"🧠 Versión de Python: {platform.python_version()}")
st.write(f"📡 Broker activo: {broker}:{port}")
st.markdown("---")

# -------------------------------
# CARGA DEL MODELO
# -------------------------------
model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# -------------------------------
# INTERFAZ DE CAPTURA
# -------------------------------
st.subheader("📷 Captura tu rostro")
img_file_buffer = st.camera_input("Usa la cámara para tomar una foto")

if img_file_buffer is not None:
    # Leer imagen
    img = Image.open(img_file_buffer)
    img = img.resize((224, 224))
    img_array = np.array(img)

    # Normalizar imagen
    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    # Predicción
    prediction = model.predict(data)
    prob_isabel = float(prediction[0][0])
    prob_santiago = float(prediction[0][1])
    prob_desconocido = float(prediction[0][2])

    st.markdown("---")
    st.subheader("📊 Probabilidades de reconocimiento")
    st.write(f"*Isabel:* {prob_isabel:.2%}")
    st.write(f"*Santiago:* {prob_santiago:.2%}")
    st.write(f"*No reconocido:* {prob_desconocido:.2%}")

    # -------------------------------
    # LÓGICA DE DECISIÓN Y MQTT
    # -------------------------------
    if prob_santiago > 0.7:
        st.success(f"✅ Bienvenido Santiago ({prob_santiago:.2%})")
        enviar_mqtt("ON", 100)  # abrir completamente
    elif prob_isabel > 0.7:
        st.success(f"✅ Bienvenida Isabel ({prob_isabel:.2%})")
        enviar_mqtt("ON", 50)   # abrir parcialmente
    else:
        st.error(f"🚫 No reconocido ({prob_desconocido:.2%})")
        enviar_mqtt("OFF", 0)   # cerrar

    st.markdown("---")
    st.caption("El sistema envió la orden al torniquete en Wokwi automáticamente.")

# -------------------------------
# PIE DE PÁGINA
# -------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray; font-size:13px;'>"
    "Desarrollado por Santiago Velásquez — Integración Facial + IoT"
    "</p>",
    unsafe_allow_html=True
)
