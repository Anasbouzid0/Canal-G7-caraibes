import streamlit as st

# Initialisation session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.set_page_config(page_title="Connexion G7", layout="centered")

# Affichage page login
if not st.session_state.authenticated:
    st.title("🔐 Connexion au Dashboard G7")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

    users = {
        "admin@g7.com": "admin123",
        "caraibes@g7.com": "g7caraibes"
    }

    if submitted:
        if email in users and users[email] == password:
            st.success("Connexion réussie ✅")
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Email ou mot de passe incorrect ❌")
else:
    st.success("✅ Connexion active. Accédez aux onglets à gauche.")
    st.info("👈 Sélectionnez un tableau dans la barre latérale.")
