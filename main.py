import streamlit as st

st.set_page_config(
    page_title="ONDA — Risk Intelligence Platform",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ensure default session state variables exist
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Utilisateur ONDA"
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "DSI"
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

# Authentication routing
if not st.session_state.get("authenticated", False):
    page_login = st.Page("login.py", title="Connexion", icon="🔒", default=True)
    pg = st.navigation([page_login], position="hidden")
    pg.run()
else:
    page_home     = st.Page("home.py",         title="Accueil — ONDA",                icon="🏠", default=True)
    page_tech     = st.Page("app.py",          title="Risque Technique (IA)",        icon="📊")
    page_human    = st.Page("human_factor.py", title="Facteur Humain (REX)",         icon="🧠")
    page_prevent  = st.Page("prevention.py",   title="Prévention des Coupures WAN",  icon="🛡️")

    pg = st.navigation([page_home, page_tech, page_human, page_prevent], position="hidden")
    pg.run()
