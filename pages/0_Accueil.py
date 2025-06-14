import streamlit as st

# Simuler une base d’utilisateurs
USERS = {
    "admin@gmail.com": "admin123",
    "autre@gmail.com": "azerty"
}

st.set_page_config(page_title="Authentification", layout="centered")

st.title("🔐 Connexion sécurisée")

email = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")
login_btn = st.button("Se connecter")

if login_btn:
    if email in USERS and USERS[email] == password:
        st.session_state.authenticated = True
        st.success("✅ Connexion réussie")
        # Redirection vers la page Accueil après connexion
        st.experimental_set_query_params(page="Accueil")
        st.rerun()
    else:
        st.error("❌ Identifiants invalides")
