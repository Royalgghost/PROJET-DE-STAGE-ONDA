import json
import base64
import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── Load video as base64 ──────────────────────────────────────────────────────
@st.cache_data
def get_video_b64() -> str:
    vid_path = ROOT / "vids" / "Loginvid.mp4"
    if vid_path.exists():
        with open(vid_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

# ── Load logo as base64 ───────────────────────────────────────────────────────
@st.cache_data
def get_logo_b64() -> str:
    logo_path = ROOT / "vids" / "logo-onda (1).png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

# ── Load credentials ──────────────────────────────────────────────────────────
def load_credentials() -> dict:
    path = ROOT / "credentials.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def try_login(email: str, password: str) -> dict | None:
    creds = load_credentials()
    user = creds.get(email.lower().strip())
    if user and user["password"] == password:
        return user
    return None

# ── Video Background & Global CSS ─────────────────────────────────────────────
video_b64 = get_video_b64()
logo_b64  = get_logo_b64()

video_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {{
    font-family: 'Outfit', sans-serif !important;
    background: #04080f !important;
    color: #94a3b8 !important;
}}

/* Hide sidebars and headers */
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="collapsedControl"], section[data-testid="stSidebarContent"] {{
    display: none !important; width: 0 !important;
}}
[data-testid="stHeader"], footer {{ display: none !important; }}

/* Fullscreen Background Video - Scaled up to crop letterbox black bars */
#bg-video {{
    position: fixed;
    top: 50%;
    left: 50%;
    width: 100vw;
    height: 100vh;
    min-width: 100vw;
    min-height: 100vh;
    object-fit: cover;
    z-index: 0;
    transform: translate(-50%, -50%) scale(1.25);
    filter: brightness(0.60) contrast(1.10);
    pointer-events: none;
}}

/* Dark overlay over video */
#video-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(4, 8, 15, 0.45);
    z-index: 1;
    pointer-events: none;
}}

/* Solid Opaque Login Card Container (Directly on .block-container) */
.block-container {{
    position: relative !important;
    z-index: 10 !important;
    padding: 36px 32px 30px 32px !important;
    max-width: 440px !important;
    margin: 4.5rem auto 2rem auto !important;
    background-color: #0b1329 !important;
    background: #0b1329 !important;
    border: 1px solid #1e3a5f !important;
    border-top: 3px solid #38bdf8 !important;
    border-radius: 24px !important;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.95), 0 0 35px rgba(56, 189, 248, 0.20) !important;
}}

/* Input fields */
.stTextInput > div > div > input {{
    background: #152238 !important;
    border: 1px solid #283a5c !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25) !important;
}}
.stTextInput > label {{
    color: #cbd5e1 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}}

/* Login button */
.stButton > button {{
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
    padding: 13px 0 !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4) !important;
}}
.stButton > button:hover {{
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}}

.stAlert {{ border-radius: 10px !important; font-family: 'Outfit', sans-serif !important; }}
</style>

<video autoplay loop muted playsinline id="bg-video">
    <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
</video>
<div id="video-overlay"></div>
"""

st.markdown(video_html, unsafe_allow_html=True)

# ── Login Card Content ────────────────────────────────────────────────────────
logo_html = f"""
<div style="background: #ffffff; border-radius: 14px; padding: 10px 22px; display: inline-flex;
            align-items: center; justify-content: center; margin-bottom: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
    <img src="data:image/png;base64,{logo_b64}" style="height: 52px; max-width: 180px; object-fit: contain;" alt="ONDA Logo">
</div>
""" if logo_b64 else '<div style="display:inline-flex; align-items:center; justify-content:center; width:60px; height:60px; border-radius:16px; background:linear-gradient(135deg, #0ea5e9, #2563eb); font-size:1.8rem; margin-bottom:14px;">✈️</div>'

header_html = (
    f'<div style="text-align: center; margin-bottom: 22px;">'
    f'{logo_html}'
    f'<h2 style="color: #f8fafc; font-size: 1.45rem; font-weight: 800; margin: 10px 0 6px 0; letter-spacing: -0.01em;">'
    f'Office National Des Aéroports'
    f'</h2>'
    f'<p style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; margin: 0 0 6px 0; letter-spacing: 0.04em; text-transform: uppercase;">'
    f'Plateforme Risques &amp; REX WAN'
    f'</p>'
    f'<p style="color: #94a3b8; font-size: 0.82rem; margin: 0; font-weight: 300;">'
    f'Accès réservé — Personnel ONDA autorisé'
    f'</p>'
    f'</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

email    = st.text_input("Adresse email", placeholder="prenom.nom@onada.com")
password = st.text_input("Mot de passe",  placeholder="••••••••••", type="password")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
login_btn = st.button("Se connecter", use_container_width=True)

if login_btn:
    clean_email = email.strip().lower()
    allowed_domains = ("@onda.ma", "@onada.com", "@onda.com")
    if not clean_email:
        st.error("Veuillez saisir votre adresse email professionnelle.")
    elif not any(clean_email.endswith(domain) for domain in allowed_domains):
        st.error("⚠️ Seules les adresses **@onda.ma** ou **@onada.com** sont autorisées sur cette plateforme.")
    elif not password:
        st.error("Veuillez saisir votre mot de passe.")
    else:
        user = try_login(clean_email, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.user_name     = user["name"]
            st.session_state.user_email    = clean_email
            st.session_state.user_role     = user["role"]
            st.rerun()
        else:
            st.error("❌ Identifiants incorrects. Vérifiez votre email et mot de passe.")

st.markdown("""
<p style="text-align: center; color: #64748b; font-size: 0.78rem; margin-top: 22px; margin-bottom: 0; letter-spacing: 0.03em;">
    Problème de connexion ? Contactez la DSI ONDA
</p>
""", unsafe_allow_html=True)
