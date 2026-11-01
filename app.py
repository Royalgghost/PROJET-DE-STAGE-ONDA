from __future__ import annotations

import json
import datetime
import base64
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

# ── Load logo ────────────────────────────────────────────────────────────────
@st.cache_data
def get_logo_b64() -> str:
    p = ROOT / "vids" / "logo-onda (1).png"
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_logo_b64()

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    font-family: 'Outfit', sans-serif !important;
    background: #030712 !important;
    color: #94a3b8 !important;
}

/* Hide sidebars and Streamlit defaults */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
section[data-testid="stSidebarContent"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
}
[data-testid="stHeader"], footer { display: none !important; }

.block-container {
    padding: 20px 48px 40px 48px !important;
    max-width: 100% !important;
}

/* Header bar */
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(11, 18, 35, 0.85);
    border: 1px solid rgba(30, 41, 59, 0.8);
    border-radius: 18px; padding: 16px 28px;
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}
.app-header-left { display: flex; align-items: center; gap: 14px; }
.app-header-title { font-size: 1.25rem; font-weight: 800; color: #f8fafc; margin: 0; }
.app-header-subtitle { font-size: 0.82rem; color: #38bdf8; font-weight: 500; margin-top: 2px; }

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(30, 41, 59, 0.8) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
}
[data-testid="stMetricValue"] {
    color: #f8fafc !important; font-weight: 800 !important;
    font-size: 1.85rem !important; font-family: 'Outfit', sans-serif !important;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important; font-weight: 600 !important;
    font-size: 0.8rem !important; font-family: 'Outfit', sans-serif !important;
    text-transform: uppercase; letter-spacing: 0.04em;
}

/* Glass card */
.glass-card {
    background: rgba(11, 18, 35, 0.75);
    border: 1px solid rgba(30, 41, 59, 0.8);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    margin-bottom: 20px;
    backdrop-filter: blur(12px);
}

/* Risk badges */
.risk-high {
    background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.35);
    border-left: 6px solid #ef4444; padding: 14px 18px; border-radius: 12px;
    color: #fca5a5; margin-bottom: 16px; box-shadow: 0 0 20px rgba(239, 68, 68, 0.1);
}
.risk-medium {
    background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.35);
    border-left: 6px solid #f59e0b; padding: 14px 18px; border-radius: 12px;
    color: #fde047; margin-bottom: 16px; box-shadow: 0 0 20px rgba(245, 158, 11, 0.1);
}
.risk-low {
    background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.35);
    border-left: 6px solid #10b981; padding: 14px 18px; border-radius: 12px;
    color: #a7f3d0; margin-bottom: 16px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.1);
}

/* Buttons */
.stButton > button {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(30, 41, 59, 0.9) !important; color: #cbd5e1 !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: #38bdf8 !important; color: #38bdf8 !important;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    border-color: #38bdf8 !important; color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
}

/* Form fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: #0b1329 !important;
    border: 1px solid rgba(30, 41, 59, 0.9) !important; color: #f8fafc !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
}

/* Pill radio tabs */
div.stRadio > div[role="radiogroup"] {
    flex-direction: row !important; gap: 10px !important; margin-bottom: 24px !important;
}
div.stRadio > div[role="radiogroup"] label {
    background: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(30, 41, 59, 0.8) !important;
    border-radius: 99px !important; padding: 8px 22px !important;
    color: #94a3b8 !important; transition: all 0.2s ease !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
}
div.stRadio > div[role="radiogroup"] label:hover {
    background: rgba(56, 189, 248, 0.1) !important;
    border-color: #38bdf8 !important; color: #f8fafc !important;
}
div.stRadio > div[role="radiogroup"] [data-checked="true"] label {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    border-color: #38bdf8 !important; color: white !important; font-weight: 700 !important;
    box-shadow: 0 4px 18px rgba(14, 165, 233, 0.35) !important;
}
</style>
""", unsafe_allow_html=True)

# ── TOP BAR HEADER ────────────────────────────────────────────────────────────
top_l, top_r = st.columns([5, 1])
with top_l:
    logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="height:36px; object-fit:contain;" alt="ONDA">' if logo_b64 else '🤖'
    st.markdown(f"""
    <div class="app-header">
        <div class="app-header-left">
            {logo_img}
            <div>
                <div class="app-header-title">Risque Réseau Prédictif (IA)</div>
                <div class="app-header-subtitle">Modèle de machine learning &amp; Détection précoce d'incidents WAN</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_r:
    st.write("")
    if st.button("← Retour Accueil", key="back_home_app", use_container_width=True):
        st.switch_page("home.py")

# ── Load data helper ─────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    incidents = pd.read_csv(
        ARTIFACTS / "incidents_clean.csv",
        parse_dates=["date_incident", "date_ticket", "date_recovery", "date_closure"],
    )
    risks = pd.read_csv(
        ARTIFACTS / "latest_risk_scores.csv",
        parse_dates=["reference_date"],
    )
    predictions = pd.read_csv(
        ARTIFACTS / "test_predictions.csv",
        parse_dates=["reference_date"],
    )
    with open(ARTIFACTS / "metrics.json", encoding="utf-8") as file:
        metrics = json.load(file)
    return incidents, risks, predictions, metrics

# Mitigation logs helpers
def load_logs() -> dict:
    log_path = ARTIFACTS / "mitigation_logs.json"
    if log_path.exists():
        try:
            with open(log_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_log(site: str, action: str, status: str, operator: str):
    log_path = ARTIFACTS / "mitigation_logs.json"
    logs = load_logs()
    if site not in logs:
        logs[site] = []
    logs[site].append({
        "timestamp": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "action": action,
        "status": status,
        "operator": operator
    })
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

# Plotly style helper
def style_chart(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', family='Outfit'),
        xaxis=dict(
            gridcolor='rgba(30, 41, 59, 0.6)', 
            zerolinecolor='rgba(30, 41, 59, 0.6)',
            title_font=dict(size=12, color='#94a3b8'),
            tickfont=dict(size=10, color='#94a3b8')
        ),
        yaxis=dict(
            gridcolor='rgba(30, 41, 59, 0.6)', 
            zerolinecolor='rgba(30, 41, 59, 0.6)',
            title_font=dict(size=12, color='#94a3b8'),
            tickfont=dict(size=10, color='#94a3b8')
        ),
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0.6)',
            bordercolor='rgba(30, 41, 59, 0.8)',
            font=dict(size=10, color='#cbd5e1')
        ),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

# Custom Badge Renderers
def risk_badge(level: str, score: float, reasons: str) -> str:
    css = {
        "ÉLEVÉ": "risk-high",
        "MOYEN": "risk-medium",
        "FAIBLE": "risk-low",
    }.get(level, "risk-low")
    return (
        f'<div class="{css}"><b>Risque {level} — Score : {score:.1f} / 100</b><br>'
        f'<span style="font-size:0.88rem;">{reasons}</span></div>'
    )

# Load base data
incidents, risks, predictions, metrics = load_data()

# Initialize session state variables
if "app_subpage" not in st.session_state:
    st.session_state.app_subpage = "📊 Vue d'ensemble"
if "selected_site" not in st.session_state:
    st.session_state.selected_site = None

# Render Sub-navigation pill menu at the top
subpage_options = ["📊 Vue d'ensemble", "🚨 Alertes de Risque", "📋 Fiche Détaillée", "🔍 Explorateur de Sites", "⚙️ Diagnostic Modèle"]

sub_page = st.radio(
    "Menu Technique",
    subpage_options,
    index=subpage_options.index(st.session_state.app_subpage) if st.session_state.app_subpage in subpage_options else 0,
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state.app_subpage = sub_page

# Global Filter Options (Filter by Risk Level or Search Site)
col_filt1, col_filt2 = st.columns([3, 1])
with col_filt1:
    search_query = st.text_input("🔍 Recherche rapide de site...", placeholder="Tapez un nom d'aéroport ou de site (ex: CASABLANCA, MARRAKECH, TANGER...)", label_visibility="collapsed")
with col_filt2:
    selected_level = st.multiselect("Filtrer Niveau :", ["ÉLEVÉ", "MOYEN", "FAIBLE"], default=["ÉLEVÉ", "MOYEN", "FAIBLE"], label_visibility="collapsed")

# Apply filters
filtered_risks = risks[risks["risk_level"].isin(selected_level)].copy()
if search_query.strip():
    filtered_risks = filtered_risks[filtered_risks["site"].str.contains(search_query.strip(), case=False, na=False)]

st.divider()

# --- PAGE FUNCTIONS ---

def show_overview():
    st.markdown('<h2 style="color:white; margin-top:0;">📊 Vue d\'ensemble du Risque Réseau</h2>', unsafe_allow_html=True)
    st.write("Tableau de bord de pilotage prédictif. Permet de suivre l'état général du réseau WAN et de détecter les sites en sursis d'incident.")
    
    high_count = int((risks["risk_level"] == "ÉLEVÉ").sum())
    medium_count = int((risks["risk_level"] == "MOYEN").sum())
    mean_score = float(risks["risk_score"].mean())
    total_incidents = int(len(incidents))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Incidents Historiques", f"{total_incidents:,}".replace(",", " "))
    with c2:
        st.metric("Sites à Risque ÉLEVÉ", high_count, delta="Critiques" if high_count > 0 else None, delta_color="inverse")
    with c3:
        st.metric("Sites à Risque MOYEN", medium_count)
    with c4:
        st.metric("Score de Risque Moyen", f"{mean_score:.1f}/100")
        
    st.write("")

    left, right = st.columns([1.4, 1])
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        ranking = filtered_risks.sort_values("risk_score", ascending=True)
        if not ranking.empty:
            fig = px.bar(
                ranking,
                x="risk_score",
                y="site",
                orientation="h",
                color="risk_level",
                color_discrete_map={
                    "ÉLEVÉ": "#ef4444",
                    "MOYEN": "#f59e0b",
                    "FAIBLE": "#10b981",
                },
                labels={"risk_score": "Score de risque", "site": "Site"},
                title="Classement dynamique du risque des sites",
            )
            style_chart(fig)
            fig.update_layout(height=max(460, 26 * len(ranking)), legend_title_text="Niveau")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun site ne correspond aux filtres sélectionnés.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        # Pie chart risk levels
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        risk_counts = (
            risks["risk_level"]
            .value_counts()
            .reindex(["ÉLEVÉ", "MOYEN", "FAIBLE"], fill_value=0)
            .reset_index()
        )
        risk_counts.columns = ["Niveau", "Sites"]
        fig_pie = px.pie(
            risk_counts,
            names="Niveau",
            values="Sites",
            hole=0.55,
            color="Niveau",
            color_discrete_map={
                "ÉLEVÉ": "#ef4444",
                "MOYEN": "#f59e0b",
                "FAIBLE": "#10b981",
            },
            title="Répartition globale des niveaux de risque",
        )
        style_chart(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Monthly line chart
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        monthly = (
            incidents.assign(month=incidents["date_incident"].dt.to_period("M").dt.to_timestamp())
            .groupby("month")
            .size()
            .reset_index(name="incidents")
        )
        fig_line = px.line(
            monthly,
            x="month",
            y="incidents",
            markers=True,
            title="Tendance mensuelle globale des incidents",
            labels={"month": "Mois", "incidents": "Incidents"},
        )
        style_chart(fig_line)
        fig_line.update_traces(line_color="#38bdf8", marker=dict(color="#818cf8", size=8))
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


def show_alerts():
    st.markdown('<h2 style="color:white; margin-top:0;">🚨 Alertes de Risque Actives</h2>', unsafe_allow_html=True)
    st.write("Liste des sites nécessitant une attention immédiate. Cliquez sur **📋 Consulter la fiche** pour ouvrir le rapport d'incident complet du site.")
    
    # Sort alerts by score descending
    alerts = filtered_risks[filtered_risks["risk_level"].isin(["ÉLEVÉ", "MOYEN"])].sort_values(
        "risk_score", ascending=False
    )
    
    st.subheader(f"Alertes actives filtrées ({len(alerts)} sites)")
    
    if alerts.empty:
        st.success("✅ Aucune alerte active pour les filtres sélectionnés.")
    else:
        for idx, row in alerts.iterrows():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"### 📍 {row['site']}")
            st.markdown(
                risk_badge(row["risk_level"], row["risk_score"], row["risk_reasons"]),
                unsafe_allow_html=True,
            )
            
            # Metric details columns + Action button
            cols = st.columns([1, 1, 1, 1, 1.2])
            cols[0].metric("Incidents (30j)", int(row["incidents_30d"]))
            cols[1].metric("Incidents (90j)", int(row["incidents_90d"]))
            cols[2].metric("Indisponibilité (90j)", f"{row['downtime_90d_h']:.1f} h")
            cols[3].metric("Dernier incident", f"{int(row['days_since_last_incident'])} j")
            
            # Action button
            with cols[4]:
                st.write("") 
                if st.button("📋 Consulter la fiche", key=f"alert_btn_{row['site']}", type="primary", use_container_width=True):
                    st.session_state.selected_site = row['site']
                    st.session_state.app_subpage = "📋 Fiche Détaillée"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.download_button(
        "📥 Exporter tous les scores de risque en CSV",
        data=risks.to_csv(index=False).encode("utf-8-sig"),
        file_name="onda_scores_risque.csv",
        mime="text/csv",
        use_container_width=True
    )


def show_details():
    st.markdown('<h2 style="color:white; margin-top:0;">📋 Fiche Détaillée de Risque Site</h2>', unsafe_allow_html=True)
    
    all_sites = sorted(risks["site"].unique().tolist())
    
    if st.session_state.selected_site not in all_sites:
        st.session_state.selected_site = all_sites[0]
        
    c_header_1, c_header_2 = st.columns([3, 1.2])
    with c_header_1:
        st.write("Analyse approfondie et historique d'intervention sur le site sélectionné.")
    with c_header_2:
        selected_site = st.selectbox(
            "Changer de site :", 
            all_sites, 
            index=all_sites.index(st.session_state.selected_site),
            label_visibility="collapsed"
        )
        if selected_site != st.session_state.selected_site:
            st.session_state.selected_site = selected_site
            st.rerun()
            
    if st.button("← Retour à la liste des alertes", type="secondary"):
        st.session_state.app_subpage = "🚨 Alertes de Risque"
        st.rerun()
        
    st.divider()
    
    chosen_site = st.session_state.selected_site
    current = risks[risks["site"] == chosen_site].iloc[0]
    
    st.markdown(
        risk_badge(current["risk_level"], current["risk_score"], current["risk_reasons"]),
        unsafe_allow_html=True,
    )
    
    col_metrics = st.columns(4)
    col_metrics[0].metric("Dernier Incident", f"{int(current['days_since_last_incident'])} jours")
    col_metrics[1].metric("Incidents sur 90j", int(current["incidents_90d"]))
    col_metrics[2].metric("Indisponibilité (90j)", f"{current['downtime_90d_h']:.1f} h")
    col_metrics[3].metric("Total Incidents Historiques", int(current["total_incidents_before"]))
    
    st.divider()
    
    site_incidents = incidents[incidents["site"] == chosen_site].copy()
    site_incidents["month"] = site_incidents["date_incident"].dt.to_period("M").dt.to_timestamp()
    
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        cause_counts = site_incidents["category"].value_counts().reset_index()
        cause_counts.columns = ["Catégorie", "Incidents"]
        fig_pie = px.pie(
            cause_counts,
            names="Catégorie",
            values="Incidents",
            hole=0.4,
            title=f"Catégories d'incidents — {chosen_site}",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        style_chart(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with right_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        site_monthly = (
            site_incidents.groupby("month")
            .agg(incidents=("ticket_number", "count"))
            .reset_index()
        )
        fig_bar = px.bar(
            site_monthly,
            x="month",
            y="incidents",
            title=f"Historique d'incidents par mois — {chosen_site}",
            labels={"month": "Mois", "incidents": "Nombre d'incidents"}
        )
        style_chart(fig_bar)
        fig_bar.update_traces(marker_color="#38bdf8")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.divider()

    # INTERACTIVE MITIGATION LOGS SECTION
    st.markdown('<h3 style="color:white;">🛠️ Journal d\'Intervention &amp; Suivi des Actions</h3>', unsafe_allow_html=True)
    st.write("Consignez les actions d'intervention ou de maintenance préventive effectuées sur ce site.")
    
    logs = load_logs()
    site_logs = logs.get(chosen_site, [])
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if site_logs:
        st.write("**Historique des interventions enregistrées :**")
        log_df = pd.DataFrame(site_logs)
        log_df = log_df.rename(columns={
            "timestamp": "Date / Heure",
            "action": "Description de l'action",
            "status": "Statut",
            "operator": "Intervenant"
        })
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune intervention n'a encore été enregistrée pour ce site.")
        
    with st.expander("➕ Enregistrer une nouvelle action de mitigation / note"):
        with st.form("new_log_form", clear_on_submit=True):
            f_action = st.text_area("Description de l'action entreprise :", placeholder="Ex: Remplacement du modem Orange défectueux, Redémarrage électrique...")
            c_form_1, c_form_2 = st.columns(2)
            f_operator = c_form_1.selectbox("Intervenant :", ["Equipe ONDA DSI", "Support Maroc Telecom (IAM)", "Support Orange", "Autre prestataire"])
            f_status = c_form_2.selectbox("Statut de la panne / alerte :", ["Planifié", "En cours d'intervention", "Résolu / Stable"])
            
            submit_log = st.form_submit_button("Enregistrer l'action", type="primary")
            if submit_log:
                if f_action.strip() == "":
                    st.error("Veuillez saisir une description de l'action entreprise.")
                else:
                    save_log(chosen_site, f_action.strip(), f_status, f_operator)
                    st.success("✅ Action enregistrée avec succès !")
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
                    
    st.divider()
    
    st.markdown('<h3 style="color:white;">📋 Historique complet des tickets d\'incidents</h3>', unsafe_allow_html=True)
    display_cols = [
        "ticket_number",
        "date_incident",
        "incident_duration_h",
        "operator",
        "category",
        "incident_nature_raw",
    ]
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.dataframe(
        site_incidents[display_cols]
        .sort_values("date_incident", ascending=False)
        .rename(
            columns={
                "ticket_number": "Ticket",
                "date_incident": "Date de l'incident",
                "incident_duration_h": "Durée (h)",
                "operator": "Opérateur",
                "category": "Catégorie",
                "incident_nature_raw": "Détail / Nature",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


def show_explorer():
    st.markdown('<h2 style="color:white; margin-top:0;">🔍 Explorateur de Données par Site</h2>', unsafe_allow_html=True)
    st.write("Sélectionnez n'importe quel site du réseau pour visualiser son historique complet d'incidents sans restriction de niveau de risque.")
    
    site_list = sorted(risks["site"].unique())
    chosen_explorer_site = st.selectbox("Sélectionner un site :", site_list)
    
    explorer_incidents = incidents[incidents["site"] == chosen_explorer_site].copy()
    explorer_incidents["month"] = explorer_incidents["date_incident"].dt.to_period("M").dt.to_timestamp()
    
    c_exp_1, c_exp_2 = st.columns(2)
    with c_exp_1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        cause_counts = explorer_incidents["category"].value_counts().reset_index()
        cause_counts.columns = ["Catégorie", "Incidents"]
        fig_pie = px.pie(
            cause_counts,
            names="Catégorie",
            values="Incidents",
            hole=0.4,
            title=f"Répartition des pannes — {chosen_explorer_site}",
        )
        style_chart(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_exp_2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        explorer_monthly = (
            explorer_incidents.groupby("month")
            .agg(incidents=("ticket_number", "count"))
            .reset_index()
        )
        fig_bar = px.bar(
            explorer_monthly,
            x="month",
            y="incidents",
            title=f"Fréquence mensuelle des tickets — {chosen_explorer_site}",
        )
        style_chart(fig_bar)
        fig_bar.update_traces(marker_color="#38bdf8")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.subheader("Tickets associés")
    display_cols = [
        "ticket_number",
        "date_incident",
        "incident_duration_h",
        "operator",
        "category",
        "incident_nature_raw",
    ]
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.dataframe(
        explorer_incidents[display_cols]
        .sort_values("date_incident", ascending=False)
        .rename(
            columns={
                "ticket_number": "Ticket ID",
                "date_incident": "Date",
                "incident_duration_h": "Durée (h)",
                "operator": "Opérateur",
                "category": "Catégorie",
                "incident_nature_raw": "Description",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


def show_model():
    st.markdown('<h2 style="color:white; margin-top:0;">⚙️ Diagnostic &amp; Performance du Modèle IA</h2>', unsafe_allow_html=True)
    st.write("Évaluation des performances prédictives du modèle d'intelligence artificielle sur le jeu de validation.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Précision (Precision)", f"{metrics['precision']:.2%}")
    c2.metric("Rappel (Recall)", f"{metrics['recall']:.2%}")
    c3.metric("F1-score", f"{metrics['f1']:.2%}")
    c4.metric("PR-AUC Score", f"{metrics['pr_auc']:.3f}")
    
    st.write("")
    st.info(
        f"**Fenêtre d'entraînement** : {metrics['train_start']} → {metrics['train_end']} "
        f"({metrics['train_rows']} observations).\n\n"
        f"**Fenêtre de test (validation temporelle)** : {metrics['test_start']} → {metrics['test_end']} "
        f"({metrics['test_rows']} observations)."
    )

    col_cm, col_cal = st.columns([1, 1.2])
    
    with col_cm:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Matrice de Confusion")
        cm_raw = metrics["confusion_matrix"]
        
        # Plotly Heatmap for Confusion Matrix
        fig_cm = go.Figure(data=go.Heatmap(
            z=cm_raw,
            x=["Prédit : SANS Incident", "Prédit : INCIDENT"],
            y=["Réel : SANS Incident", "Réel : INCIDENT"],
            colorscale=[[0, "#0b1329"], [0.5, "#1e3a8a"], [1, "#0ea5e9"]],
            text=[[str(val) for val in row] for row in cm_raw],
            texttemplate="%{text}",
            textfont={"size": 18, "color": "white", "family": "Outfit"},
            showscale=False
        ))
        fig_cm.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Outfit'),
            margin=dict(t=30, b=30, l=30, r=30),
            height=300
        )
        st.plotly_chart(fig_cm, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cal:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        test_curve = (
            predictions.groupby("reference_date")
            .agg(
                risque_moyen=("risk_probability", "mean"),
                taux_reel=("target_incident_next_30d", "mean"),
            )
            .reset_index()
        )
        fig_cal = px.line(
            test_curve,
            x="reference_date",
            y=["risque_moyen", "taux_reel"],
            markers=True,
            title="Probabilité de risque prédite vs Taux réel constaté",
            labels={"value": "Taux", "reference_date": "Date de référence", "variable": "Indicateur"},
        )
        style_chart(fig_cal)
        new_names = {"risque_moyen": "Risque Moyen Prédit", "taux_reel": "Taux Réel Constaté"}
        fig_cal.for_each_trace(lambda t: t.update(name=new_names.get(t.name, t.name)))
        fig_cal.update_layout(height=300)
        st.plotly_chart(fig_cal, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# --- ROUTING LOGIC ---
if st.session_state.app_subpage == "📊 Vue d'ensemble":
    show_overview()
elif st.session_state.app_subpage == "🚨 Alertes de Risque":
    show_alerts()
elif st.session_state.app_subpage == "📋 Fiche Détaillée":
    show_details()
elif st.session_state.app_subpage == "🔍 Explorateur de Sites":
    show_explorer()
elif st.session_state.app_subpage == "⚙️ Diagnostic Modèle":
    show_model()
