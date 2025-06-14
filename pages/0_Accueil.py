import streamlit as st

st.set_page_config(page_title="Connexion", layout="centered")

LOGIN_EMAIL = "admin@g7caraibes.com"
LOGIN_PASSWORD = "secret123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("🔐 Dashboard G7 Caraïbes")
st.markdown("### Connectez-vous pour continuer.")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    submit = st.form_submit_button("Connexion")

    if submit:
        if email == LOGIN_EMAIL and password == LOGIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Connexion réussie. Accès débloqué.")
            st.experimental_rerun()
        else:
            st.error("❌ Identifiants incorrects")
