
        print("✅ Conectado al broker MQTT.")
        return client
    except Exception as e:
        print(f"Error al conectar a MQTT: {e}")
        return None

client = conectar_mqtt()

def enviar_mqtt(act, analog):
    """Envía mensaje MQTT al ESP32 usando el cliente cacheado."""
    if client:
        message = {"Act1": act, "Analog": analog}
        client.publish(topic, json.dumps(message))
        print("📤 Enviado al broker:", message)
    else:
        st.error("No se pudo conectar al broker MQTT. El mensaje no fue enviado.")
        print("Error: Cliente MQTT no disponible.")

# --- MEJORA 2: Cachear el modelo de Keras ---
@st.cache_resource
def cargar_modelo():
    """Carga el modelo Keras desde el disco y lo cachea."""
    print("🧠 Cargando modelo Keras...")
    try:
        model = load_model('keras_model.h5', compile=False) 
        print("✅ Modelo cargado exitosamente.")
        return model
    except Exception as e:
        print(f"Error al cargar 'keras_model.h5': {e}")
        return None

model = cargar_modelo()
if model is None:
    st.error("Error crítico: No se pudo cargar el modelo de reconocimiento facial.")

# -------------------------------
# CONFIGURACIÓN DE INTERFAZ
# -------------------------------
st.set_page_config(page_title="Acceso Facial Inteligente", layout="centered")

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
    .num-btn { /* Tu CSS de botones es perfecto, no se toca */
        background-color: #64ffda;
        color: #0a192f;
        border-radius: 12px;
        font-size: 1.5em;
        font-weight: bold;
        height: 70px;
        width: 100%;
        border: none;
        cursor: pointer;
        transition: 0.2s;
    }
    .num-btn:hover {
        background-color: #52e0c4;
        transform: scale(1.05);
    }
    .display-box {
        background-color: #112240;
        color: #64ffda;
        text-align: center;
        font-size: 1.5em;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        letter-spacing: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# ENCABEZADO
# -------------------------------
st.markdown("<div class='title'>🔒 Sistema de Acceso Facial</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Reconocimiento de rostro y acceso con cédula</div>", unsafe_allow_html=True)

# -------------------------------
# FLUJO 1: RECONOCIMIENTO FACIAL (Corregido con session_state)
# -------------------------------
if "camara_activa" not in st.session_state:
    st.session_state.camara_activa = False

if st.button("📸 Entrar con reconocimiento facial"):
    st.session_state.camara_activa = True

if st.session_state.camara_activa and model is not None:
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    st.subheader("📷 Escanear Rostro")
    img_file_buffer = st.camera_input("Usa la cámara para validar tu identidad", key="camera_widget")

    if img_file_buffer is not None:
        img = Image.open(img_file_buffer)
        img = img.resize((224, 224))
        img_array = np.array(img)
        
        if img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]
            
        normalized_image_array = (img_array.astype(np.float32) / 127.5) - 1
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

        st.session_state.camara_activa = False
        st.rerun()

# -------------------------------
# 🔢 PANEL DE CÉDULA CON BOTONES (FLUJO 2 CORREGIDO)
# -------------------------------
st.markdown("---")
st.subheader("💳 Ingreso por Cédula (teclado táctil)")

# Base de datos de cédulas (numéricas)
base_datos_cedulas = {
    1025761205: "Santiago Velásquez",
    1007654321: "Isabel Gómez",
    10: "Invitado"
}

# --- SOLUCIÓN: Inicializar estados para el mensaje ---
if "cedula_actual" not in st.session_state:
    st.session_state.cedula_actual = ""
if "auth_message" not in st.session_state:
    st.session_state.auth_message = ""
if "auth_success" not in st.session_state:
    st.session_state.auth_success = False

# Mostrar lo digitado
display_text = st.session_state.cedula_actual or '----'
st.markdown(f"<div class='display-box'>{display_text}</div>", unsafe_allow_html=True)

# Teclado numérico
numeros = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["Borrar", "0", "Verificar"]
]

for fila in numeros:
    cols = st.columns(3)
    for i, num in enumerate(fila):
        if cols[i].button(num, key=num, use_container_width=True):
            
            if num == "Borrar":
                st.session_state.cedula_actual = st.session_state.cedula_actual[:-1]
                st.session_state.auth_message = "" # Limpiar mensaje
            
            elif num == "Verificar":
                cedula_str = st.session_state.cedula_actual
                
                # Comprobar que no esté vacío ANTES de isdigit()
                if cedula_str.isdigit() and cedula_str: 
                    cedula_num = int(cedula_str)
                    
                    if cedula_num in base_datos_cedulas:
                        nombre = base_datos_cedulas[cedula_num]
                        # Guardar mensaje en el estado
                        st.session_state.auth_message = f"👋 Bienvenido {nombre}"
                        st.session_state.auth_success = True
                        enviar_mqtt("ON", 80)
                    else:
                        # Guardar mensaje en el estado
                        st.session_state.auth_message = "🚫 Cédula no registrada"
                        st.session_state.auth_success = False
                        enviar_mqtt("OFF", 0)
                else:
                    # Guardar mensaje en el estado
                    st.session_state.auth_message = "⚠️ La cédula solo debe contener números."
                    st.session_state.auth_success = False
                
                st.session_state.cedula_actual = "" # Limpiar solo el input

            else: # Es un botón de número
                st.session_state.auth_message = "" # Limpiar mensaje al teclear
                if len(st.session_state.cedula_actual) < 10:
                    st.session_state.cedula_actual += num
            
            # Forzar rerun para mostrar cambios
            st.rerun()

# --- SOLUCIÓN: Mostrar el mensaje de estado persistente ---
# Este bloque está FUERA del bucle de botones
if st.session_state.auth_message:
    if st.session_state.auth_success:
        st.markdown(
            f"<div class='welcome'>{st.session_state.auth_message}</div>"
            "<div class='subtext'>Acceso autorizado</div>",
            unsafe_allow_html=True
        )
    else:
        # Reutiliza tus clases CSS para mensajes de error
        st.markdown(
            f"<div class='welcome' style='color:#ff6b6b;'>{st.session_state.auth_message}</div>"
            "<div class='subtext'>Por favor, intenta nuevamente.</div>",
            unsafe_allow_html=True
        )

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
