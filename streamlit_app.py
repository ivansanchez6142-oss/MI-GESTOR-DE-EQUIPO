import streamlit as st
import google.generativeai as genai

# --- CONFIGURACION ---
# PEGÁ TU LLAVE ACÁ ADENTRO:
API_KEY = "AIzaSyBlahBlahBlah..."

if API_KEY != "TU_API_KEY_AQUI":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

st.title("⚽ Mi Gestor de Equipo")

if 'equipo' not in st.session_state:
    st.session_state.equipo = []

with st.sidebar:
    st.header("Cargar Jugador")
    nombre = st.text_input("Nombre:")
    pos = st.selectbox("Posición:", ["Arquero", "Defensa", "Medio", "Delantero"])
    if st.button("Agregar"):
        if nombre:
            st.session_state.equipo.append(f"{nombre} ({pos})")

for j in st.session_state.equipo:
    st.write(f"🏃 {j}")

if st.button("Pedir táctica"):
    if API_KEY == "TU_API_KEY_AQUÍ":
        st.error("Falta la API Key.")
    else:
        resp = model.generate_content(f"Armá una táctica para estos jugadores: {st.session_state.equipo}")
        st.write(resp.text)

