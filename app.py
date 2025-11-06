import paho.mqtt.client as mqtt
import json
import platform
import time

# -------------------------------
# CONFIGURACIÓN MQTT
@@ -25,16 +24,54 @@ def enviar_mqtt(act, analog):
    print("📤 Enviado al broker:", message)

# -------------------------------
# CONFIGURACIÓN STREAMLIT
# CONFIGURACIÓN DE INTERFAZ
# -------------------------------
st.set_page_config(page_title="Reconocimiento Facial", layout="centered")
st.set_page_config(page_title="Acceso Facial Inteligente", layout="centered")

st.title("🔍 Sistema de Reconocimiento Facial")
st.caption("Control automático de acceso mediante MQTT")
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

st.write(f"🧠 Versión de Python: `{platform.python_version()}`")
st.write(f"📡 Broker activo: `{broker}:{port}`")
st.markdown("---")
# -------------------------------
# ENCABEZADO
# -------------------------------
st.markdown("<div class='title'>🔒 Sistema de Acceso Facial</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Reconocimiento de rostro con control IoT</div>", unsafe_allow_html=True)

# -------------------------------
# CARGA DEL MODELO
@@ -43,56 +80,57 @@ def enviar_mqtt(act, analog):
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# -------------------------------
# INTERFAZ DE CAPTURA
# CAPTURA DE ROSTRO
# -------------------------------
st.subheader("📷 Captura tu rostro")
img_file_buffer = st.camera_input("Usa la cámara para tomar una foto")
st.subheader("📷 Escanear Rostro")
img_file_buffer = st.camera_input("Usa la cámara para validar tu identidad")

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
    st.write(f"**Isabel:** {prob_isabel:.2%}")
    st.write(f"**Santiago:** {prob_santiago:.2%}")
    st.write(f"**No reconocido:** {prob_desconocido:.2%}")

    # -------------------------------
    # LÓGICA DE DECISIÓN Y MQTT
    # -------------------------------
    if prob_santiago > 0.7:
        st.success(f"✅ Bienvenido Santiago ({prob_santiago:.2%})")
        enviar_mqtt("ON", 100)  # abrir completamente
        st.markdown("<div class='welcome'>👋 Bienvenido Santiago</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtext'>Ya puedes pasar</div>", unsafe_allow_html=True)
        enviar_mqtt("ON", 100)
    elif prob_isabel > 0.7:
        st.success(f"✅ Bienvenida Isabel ({prob_isabel:.2%})")
        enviar_mqtt("ON", 50)   # abrir parcialmente
        st.markdown("<div class='welcome'>👋 Bienvenida Isabel</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtext'>Ya puedes pasar</div>", unsafe_allow_html=True)
        enviar_mqtt("ON", 50)
    else:
        st.error(f"🚫 No reconocido ({prob_desconocido:.2%})")
        enviar_mqtt("OFF", 0)   # cerrar
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

    st.markdown("---")
    st.caption("El sistema envió la orden al torniquete en Wokwi automáticamente.")
# Espacio visual (aún no funcional)
canvas_placeholder = st.empty()
canvas_placeholder.write("🟦 (Zona de escritura — próximamente interactiva)")

# -------------------------------
# PIE DE PÁGINA
# -------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray; font-size:13px;'>"
    "Desarrollado por Santiago Velásquez — Integración Facial + IoT"
    "<p style='text-align:center; color:#64ffda; font-size:13px;'>"
    "Sistema desarrollado por <b>Santiago Velásquez</b> — Integración Facial + IoT"
    "</p>",
    unsafe_allow_html=True
)
