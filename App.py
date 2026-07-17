import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Cargar las variables de entorno (API Key)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Asegurarse de que la API Key exista
if not api_key:
    st.error("🔑 No se encontró la GEMINI_API_KEY en el archivo .env. Por favor, agrégala.")
    st.stop()

# Inicializar el cliente oficial de Gemini
client = genai.Client(api_key=api_key)

# 2. Configurar el diseño visual de la página web
st.set_page_config(page_title="Tutor Socrático Educativo", page_icon="🎓")
st.title("🎓 Tutor Socrático Educativo")

# === BARRA LATERAL ===
with st.sidebar:
    st.header("⚙️ Panel del Estudiante")
    st.write("Configura tu entorno de aprendizaje antes de empezar.")
    
    nivel = st.selectbox(
        "Elige tu nivel educativo:",
        ["Educación Primaria", "Educación Secundaria", "Educación Superior"]
    )
    
    st.markdown("---")
    
    if st.button("¡Logré resolver mi duda! 🎉"):
        st.balloons()
        st.success("¡Excelente trabajo! Sigue esforzándote.")
# =======================================

# Mensaje de bienvenida adaptado al nivel
bienvenida = f"¡Hola! Soy tu tutor para el nivel de **{nivel}**. No te daré las respuestas directas, pero te guiaré paso a paso con preguntas para que las descubras tú mismo. ¿En qué estás trabajando hoy?"

# 3. Inicializar el historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": bienvenida}]

# Mostrar el historial de chat en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 4. Entrada del usuario
if user_input := st.chat_input("Escribe tu duda aquí..."):
    # Agregar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Preparar el prompt del sistema (Las reglas socráticas)
    system_instruction = f"""
    Eres un tutor socrático altamente pedagógico, especializado en {nivel}.
    Tu meta es guiar al estudiante para que encuentre la respuesta por sí mismo.
    
    REGLAS ESTRICTAS:
    1. NUNCA des la respuesta directa, soluciones completas, ni códigos resueltos.
    2. Si el usuario te pide un código o una respuesta, niégate amablemente y ofrécele una pista o una pregunta guía.
    3. Adapta tu vocabulario al nivel educativo seleccionado: {nivel}.
    4. Explica conceptos complejos usando analogías sencillas y cotidianas.
    5. Haz una sola pregunta abierta a la vez al final de tu respuesta para mantener al alumno pensando.
    """

    # Generar la respuesta usando Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Convertimos el historial de mensajes al formato de Gemini
            contents = []
            for msg in st.session_state.messages[1:]: # Omitimos el saludo inicial en el historial enviado
                # Mapeamos los roles para Gemini ('user' o 'model')
                role_map = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role_map,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))

            # Llamada oficial al modelo gpt-equivalente de Google: gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            
            assistant_response = response.text
            message_placeholder.write(assistant_response)
            
            # Guardar la respuesta en el historial
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            st.error(f"❌ Ocurrió un error al conectar con Gemini: {e}")