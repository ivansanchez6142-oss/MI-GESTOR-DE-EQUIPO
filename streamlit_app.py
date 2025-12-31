import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN ---
# Si ya tenés la API Key, pegala acá entre las comillas
API_KEY = "AIzaSyBlahBlahBlah..."
if API_KEY != "TU_API_KEY_AQUÍ":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

st.title("⚽ Mi Gestor de Equipo")

# Registro de jugadores
if 'equipo' not in st.session_state:
    st.session_state.equipo = []

with st.sidebar:
    st.header("Cargar Jugador")
    nombre = st.text_input("Nombre:")
    pos = st.selectbox("Posición:", ["Arquero", "Defensa", "Medio", "Delantero"])
    if st.button("Agregar"):
        if nombre:
            st.session_state.equipo.append(f"{nombre} ({pos})")

# Lista
for j in st.session_state.equipo:
    st.write(f"🏃 {j}")

# Botón para la IA
if st.button("Pedir táctica"):
    if API_KEY == "TU_API_KEY_AQUÍ":
        st.error("Che, Iván, te falta poner la API Key en el código para que esto ande.")
    else:
        resp = model.generate_content(f"Armá una táctica para estos jugadores: {st.session_state.equipo}")
        st.write(resp.text)



