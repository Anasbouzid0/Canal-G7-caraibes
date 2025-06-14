import streamlit as st
import time

st.set_page_config(page_title="Connexion G7", layout="centered")

# === DESIGN ===
st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .title { font-size: 2.5em; color: #00ffcc; text-align: center; margin-bottom: 0.5em; }
    .box { background-color: #1e222d; padding: 2em; border-radius: 10px; box-shadow: 0 0 10px #00ffcc; max-width: 400px; margin: auto; }
    </style>
""", unsafe_allow_html=True)

# === PAGE ===
st.markdown('<div class="title">Bienvenue sur G7 Caraïbes</div>', unsafe_allow_html=True)
st.markdown('<div class="box">', unsafe_allow_html=True)

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    submit = st.form_submit_button("Se connecter")

# === UTILISATEURS ===
users = {
    "admin@g7.com": "admin123",
    "caraibes@g7.com": "g7caraibes"
}

if submit:
    if email in users and users[email] == password:
        st.success("Connexion réussie 🎉")
        time.sleep(1)
        st.switch_page("dashboard_g_7_caraibes.py")  # fonctionne car ce fichier est à la racine
    else:
        st.error("Identifiants incorrects ❌")

st.markdown('</div>', unsafe_allow_html=True)
