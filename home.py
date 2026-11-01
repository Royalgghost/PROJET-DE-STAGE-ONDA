import streamlit as st
import base64
import json
import pandas as pd
import plotly.express as px
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

# ── Load assets ───────────────────────────────────────────────────────────────
@st.cache_data
def get_logo_b64() -> str:
    p = ROOT / "vids" / "logo-onda (1).png"
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_logo_b64()

# ── Load data for executive widgets ──────────────────────────────────────────
@st.cache_data
def load_home_summary():
    try:
        risks = pd.read_csv(ARTIFACTS / "latest_risk_scores.csv")
        incidents = pd.read_csv(ARTIFACTS / "incidents_clean.csv", parse_dates=["date_incident"])
        return risks, incidents
    except Exception:
        return None, None

risks_df, incidents_df = load_home_summary()

# ── Session state defaults ───────────────────────────────────────────────────
user_name  = st.session_state.get("user_name",  "Utilisateur ONDA")
user_role  = st.session_state.get("user_role",  "DSI")
user_email = st.session_state.get("user_email", "")

# ── Global CSS & Design System ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    font-family: 'Outfit', sans-serif !important;
    background: #030712 !important;
    color: #94a3b8 !important;
    margin: 0; padding: 0;
}
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="collapsedControl"], section[data-testid="stSidebarContent"] {
    display: none !important; width: 0 !important;
}
[data-testid="stHeader"], footer { display: none !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── NAVBAR ── */
.onda-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 48px;
    background: rgba(3, 7, 18, 0.92);
    border-bottom: 1px solid rgba(30, 41, 59, 0.8);
    position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(16px);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}
.onda-nav-brand { display: flex; align-items: center; gap: 14px; }
.onda-nav-brand img { height: 40px; object-fit: contain; filter: drop-shadow(0 2px 8px rgba(56,189,248,0.3)); }
.onda-nav-title {
    font-size: 1.1rem; font-weight: 800; color: #f8fafc;
    letter-spacing: -0.01em;
}
.onda-nav-title span {
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.onda-nav-user {
    display: flex; align-items: center; gap: 10px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 99px; padding: 6px 18px;
    font-size: 0.85rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}
.onda-nav-user .avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 0.8rem;
}
.onda-nav-user .name { color: #f1f5f9; font-weight: 600; }
.onda-nav-user .role { color: #38bdf8; font-weight: 500; font-size: 0.78rem; background: rgba(56,189,248,0.1); padding: 2px 8px; border-radius: 99px; }
.onda-nav-user .mail { color: #64748b; font-size: 0.8rem; }

/* ── ALERT TICKER ── */
.ticker-wrap {
    background: rgba(239, 68, 68, 0.08);
    border-bottom: 1px solid rgba(239, 68, 68, 0.25);
    padding: 8px 48px;
    display: flex; align-items: center; justify-content: space-between;
    font-size: 0.82rem; color: #fca5a5;
}
.ticker-badge {
    background: #ef4444; color: white; font-weight: 800; font-size: 0.68rem;
    padding: 3px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.05em;
}

/* ── HERO ── */
.hero {
    text-align: center !important;
    padding: 56px 48px 40px 48px !important;
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(14,165,233,0.14) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(99,102,241,0.08) 0%, transparent 60%),
        #030712;
    position: relative; overflow: hidden;
}
.hero-badge {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    background: rgba(14,165,233,0.08);
    border: 1px solid rgba(14,165,233,0.25);
    border-radius: 99px; padding: 6px 20px;
    color: #38bdf8; font-size: 0.78rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    margin: 0 auto 20px auto !important;
    box-shadow: 0 0 20px rgba(14,165,233,0.15);
}
.hero h1 {
    font-size: 3.4rem !important; font-weight: 900 !important; line-height: 1.12 !important;
    letter-spacing: -0.03em !important; margin: 0 auto 16px auto !important;
    text-align: center !important;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero h1 em {
    font-style: normal;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.08rem !important; font-weight: 300 !important; color: #94a3b8 !important;
    max-width: 720px !important; margin: 0 auto 36px auto !important; line-height: 1.75 !important;
    text-align: center !important; display: block !important;
}

/* ── KPI BAR ── */
.kpi-bar {
    display: flex; justify-content: center; gap: 0;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(30, 41, 59, 0.8);
    border-radius: 20px; padding: 0;
    max-width: 920px; margin: 0 auto;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
}
.kpi-item {
    flex: 1; padding: 22px 18px; text-align: center;
    border-right: 1px solid rgba(30, 41, 59, 0.8);
    transition: background 0.2s ease;
}
.kpi-item:hover { background: rgba(30, 41, 59, 0.4); }
.kpi-item:last-child { border-right: none; }
.kpi-value {
    font-size: 2rem; font-weight: 800; color: #f8fafc;
    line-height: 1; margin-bottom: 6px; font-family: 'Outfit', sans-serif;
}
.kpi-value.blue { color: #38bdf8; text-shadow: 0 0 20px rgba(56,189,248,0.4); }
.kpi-value.green { color: #10b981; text-shadow: 0 0 20px rgba(16,185,129,0.4); }
.kpi-value.amber { color: #f59e0b; text-shadow: 0 0 20px rgba(245,158,11,0.4); }
.kpi-value.purple { color: #a855f7; text-shadow: 0 0 20px rgba(168,85,247,0.4); }
.kpi-label {
    font-size: 0.72rem; color: #64748b; text-transform: uppercase;
    letter-spacing: 0.06em; font-weight: 600;
}

/* ── SECTION LABELS ── */
.section-label {
    display: flex; align-items: center; gap: 16px;
    padding: 44px 48px 20px 48px;
}
.section-label-line { flex: 1; height: 1px; background: rgba(30, 41, 59, 0.8); }
.section-label-text {
    font-size: 0.75rem; font-weight: 800; color: #475569;
    text-transform: uppercase; letter-spacing: 0.14em; white-space: nowrap;
}

/* ── MODULE CARDS ── */
.module-card {
    background: rgba(11, 18, 35, 0.85);
    border-radius: 22px;
    border: 1px solid rgba(30, 41, 59, 0.8);
    padding: 30px 26px 22px 26px;
    position: relative;
    overflow: hidden;
    height: 100%;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}
.module-card:hover {
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 30px rgba(56, 189, 248, 0.15);
}
.card-glow {
    position: absolute; top: -60px; right: -60px;
    width: 180px; height: 180px; border-radius: 50%;
    pointer-events: none;
}
.card-icon-wrap {
    display: inline-flex; align-items: center; justify-content: center;
    width: 52px; height: 52px; border-radius: 16px;
    font-size: 1.5rem; margin-bottom: 18px;
}
.card-tag {
    display: inline-block;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 4px 12px;
    border-radius: 99px; margin-bottom: 14px;
}
.card-title {
    font-size: 1.3rem; font-weight: 800; color: #f8fafc;
    margin: 0 0 12px 0; line-height: 1.25;
}
.card-desc {
    font-size: 0.88rem; color: #94a3b8; line-height: 1.65;
    margin: 0 0 22px 0; min-height: 54px;
}
.card-feat {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 0; border-top: 1px solid rgba(30, 41, 59, 0.6);
    font-size: 0.84rem; color: #cbd5e1;
}
.card-feat:first-of-type { border-top: none; }
.card-feat-dot {
    width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
}

/* Container Columns Padding */
div[data-testid="stHorizontalBlock"] {
    padding: 0 48px !important;
    gap: 24px !important;
}

/* Button Styles per Column */
div[data-testid="stColumn"]:nth-of-type(1) .stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 0 !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stColumn"]:nth-of-type(1) .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5) !important;
}

div[data-testid="stColumn"]:nth-of-type(2) .stButton > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 0 !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stColumn"]:nth-of-type(2) .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
}

div[data-testid="stColumn"]:nth-of-type(3) .stButton > button {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 0 !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stColumn"]:nth-of-type(3) .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(245, 158, 11, 0.5) !important;
}

/* Logout row button */
.logout-bar .stButton > button {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(239, 68, 68, 0.4) !important;
    color: #fca5a5 !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
    padding: 10px 0 !important;
    font-weight: 600 !important;
}
.logout-bar .stButton > button:hover {
    background: rgba(239, 68, 68, 0.15) !important;
    border-color: #ef4444 !important;
    color: #ffffff !important;
}

/* ── FOOTER ── */
.onda-footer {
    background: #030712;
    border-top: 1px solid rgba(30, 41, 59, 0.8);
    padding: 24px 48px;
    margin-top: 48px;
    display: flex; align-items: center; justify-content: space-between;
}
.onda-footer-left { font-size: 0.8rem; color: #64748b; }
.onda-footer-right { display: flex; gap: 8px; align-items: center; }
.footer-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #10b981;
    box-shadow: 0 0 10px #10b981;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.9); }
}
.footer-status { font-size: 0.8rem; color: #10b981; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── NAVBAR ────────────────────────────────────────────────────────────────────
logo_img = f'<img src="data:image/png;base64,{logo_b64}" alt="ONDA Logo">' if logo_b64 else '✈️'
initial_letter = user_name[0].upper() if user_name else "U"

st.markdown(f"""
<div class="onda-nav">
    <div class="onda-nav-brand">
        {logo_img}
        <div>
            <div class="onda-nav-title">ONDA <span>Risk Intelligence</span></div>
        </div>
    </div>
    <div class="onda-nav-user">
        <div class="avatar">{initial_letter}</div>
        <span class="name">{user_name}</span>
        <span class="role">{user_role}</span>
        <span class="mail">&nbsp;{user_email}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✈️ &nbsp; Office National Des Aéroports — DSI / Direction Réseaux WAN</div>
    <h1>Plateforme de <em>Risk Management</em><br>Intelligente & REX</h1>
    <p class="hero-sub">
        Système de supervision prédictive des incidents réseau aéroportuaires propulsé par l'IA 
        et gestion opérationnelle du facteur humain — pour 27 aéroports et sites WAN actifs.
    </p>
    <div class="kpi-bar">
        <div class="kpi-item">
            <div class="kpi-value blue">864</div>
            <div class="kpi-label">Incidents analysés</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-value">27</div>
            <div class="kpi-label">Sites aéroportuaires</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-value amber">11</div>
            <div class="kpi-label">Sites à risque élevé</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-value green">62%</div>
            <div class="kpi-label">Précision modèle ML</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-value purple">4 ans</div>
            <div class="kpi-label">Historique 2021–2024</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── EXECUTIVE SNAPSHOT WIDGET ─────────────────────────────────────────────────
if risks_df is not None and incidents_df is not None:
    st.markdown("""
    <div class="section-label">
        <div class="section-label-line"></div>
        <div class="section-label-text">Aperçu Exécutif Réseau en Temps Réel</div>
        <div class="section-label-line"></div>
    </div>
    """, unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Donut Chart for Risk Level Breakdown
        risk_summary = risks_df["risk_level"].value_counts().reset_index()
        risk_summary.columns = ["Niveau", "Sites"]
        fig_donut = px.pie(
            risk_summary,
            names="Niveau",
            values="Sites",
            hole=0.6,
            color="Niveau",
            color_discrete_map={"ÉLEVÉ": "#ef4444", "MOYEN": "#f59e0b", "FAIBLE": "#10b981"},
            title="Distribution Actuelle du Risque WAN"
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1", family="Outfit"),
            margin=dict(t=40, b=20, l=20, r=20),
            height=240,
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_chart2:
        # Top 5 Highest Risk Sites Quick View
        top5 = risks_df.sort_values("risk_score", ascending=False).head(5)
        fig_bar = px.bar(
            top5,
            x="risk_score",
            y="site",
            orientation="h",
            color="risk_level",
            color_discrete_map={"ÉLEVÉ": "#ef4444", "MOYEN": "#f59e0b", "FAIBLE": "#10b981"},
            title="Top 5 des Sites les plus Critiques"
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1", family="Outfit"),
            xaxis=dict(gridcolor="#1e293b", title="", range=[0, 100]),
            yaxis=dict(gridcolor="#1e293b", title="", autorange="reversed"),
            margin=dict(t=40, b=20, l=20, r=20),
            height=240,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ── SECTION LABEL MODULES ─────────────────────────────────────────────────────
st.markdown("""
<div class="section-label">
    <div class="section-label-line"></div>
    <div class="section-label-text">Modules Principaux de la Plateforme</div>
    <div class="section-label-line"></div>
</div>
""", unsafe_allow_html=True)

# ── THREE MODULE CARDS WITH DIRECT STREAMLIT BUTTON NAVIGATION ────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="module-card">
        <div class="card-glow" style="background:radial-gradient(circle,rgba(56,189,248,0.15) 0%,transparent 70%);"></div>
        <div class="card-icon-wrap" style="background:linear-gradient(135deg,#0ea5e9,#2563eb);box-shadow:0 8px 24px rgba(14,165,233,0.4);">🤖</div>
        <div class="card-tag" style="background:rgba(56,189,248,0.12);color:#38bdf8;border:1px solid rgba(56,189,248,0.3);">IA · Machine Learning</div>
        <div class="card-title">Risque Réseau Prédictif</div>
        <div class="card-desc">Modèle ML entraîné sur 4 ans d'incidents WAN. Prédit et classe les sites à risque sur les 30 prochains jours.</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#38bdf8;"></div>Alertes critiques &amp; classement dynamique</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#38bdf8;"></div>Fiche site avec historique d'incidents</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#38bdf8;"></div>Journal de mitigation interactif par site</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#38bdf8;"></div>Diagnostic et courbes de performance du modèle</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    if st.button("Accéder au module Risque IA →", key="go_tech", use_container_width=True):
        st.switch_page("app.py")

with col2:
    st.markdown("""
    <div class="module-card">
        <div class="card-glow" style="background:radial-gradient(circle,rgba(16,185,129,0.15) 0%,transparent 70%);"></div>
        <div class="card-icon-wrap" style="background:linear-gradient(135deg,#10b981,#059669);box-shadow:0 8px 24px rgba(16,185,129,0.4);">🧠</div>
        <div class="card-tag" style="background:rgba(16,185,129,0.12);color:#10b981;border:1px solid rgba(16,185,129,0.3);">REX · Opérationnel</div>
        <div class="card-title">Facteur Humain &amp; REX</div>
        <div class="card-desc">Prévention des pannes d'origine opérationnelle. Check-lists procédurales, déclarations d'erreur et base REX.</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#10b981;"></div>Checklists de conformité procédurale</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#10b981;"></div>Déclarations REX persistantes</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#10b981;"></div>Statistiques d'erreurs &amp; causes racines</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#10b981;"></div>Fiches réflexes &amp; Règles d'Or techniciens</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    if st.button("Accéder au module Facteur Humain →", key="go_human", use_container_width=True):
        st.switch_page("human_factor.py")

with col3:
    st.markdown("""
    <div class="module-card">
        <div class="card-glow" style="background:radial-gradient(circle,rgba(245,158,11,0.15) 0%,transparent 70%);"></div>
        <div class="card-icon-wrap" style="background:linear-gradient(135deg,#f59e0b,#d97706);box-shadow:0 8px 24px rgba(245,158,11,0.4);">🛡️</div>
        <div class="card-tag" style="background:rgba(245,158,11,0.12);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);">Prévention · Analyse</div>
        <div class="card-title">Prévention des Coupures WAN</div>
        <div class="card-desc">Plan d'action priorisé basé sur les données historiques. Prévisions de coupures sur 30 jours avec analyse saisonnière.</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#f59e0b;"></div>Plan d'action priorisé par site critique</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#f59e0b;"></div>Analyse temporelle &amp; saisonnalité</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#f59e0b;"></div>Analyse par cause &amp; opérateur (Orange/IAM)</div>
        <div class="card-feat"><div class="card-feat-dot" style="background:#f59e0b;"></div>Prévisions ML 30 jours exportables</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    if st.button("Accéder au module Prévention →", key="go_prev", use_container_width=True):
        st.switch_page("prevention.py")

# ── LOGOUT ROW ────────────────────────────────────────────────────────────────
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
_, logout_col = st.columns([6, 1])
with logout_col:
    st.markdown('<div class="logout-bar">', unsafe_allow_html=True)
    if st.button("🚪 Déconnexion", key="btn_logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="onda-footer">
    <div class="onda-footer-left">
        © 2024–2026 Office National Des Aéroports (ONDA) &nbsp;·&nbsp; DSI — Division Infrastructure &amp; Réseaux WAN &nbsp;·&nbsp; v3.2
    </div>
    <div class="onda-footer-right">
        <div class="footer-dot"></div>
        <span class="footer-status">Système Opérationnel Active ML</span>
    </div>
</div>
""", unsafe_allow_html=True)
