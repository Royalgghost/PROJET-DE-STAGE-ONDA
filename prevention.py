from __future__ import annotations

import json
import datetime
import base64
from pathlib import Path
import pandas as pd
import numpy as np
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

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    font-family: 'Outfit', sans-serif !important;
    background: #030712 !important;
    color: #94a3b8 !important;
}
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="collapsedControl"], section[data-testid="stSidebarContent"] {
    display: none !important; width: 0 !important;
}
[data-testid="stHeader"], footer { display: none !important; }

.block-container { padding: 20px 48px 40px 48px !important; max-width: 100% !important; }

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
.app-header-subtitle { font-size: 0.82rem; color: #f59e0b; font-weight: 500; margin-top: 2px; }

.glass-card {
    background: rgba(11, 18, 35, 0.75);
    border: 1px solid rgba(30, 41, 59, 0.8);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    margin-bottom: 20px;
    backdrop-filter: blur(12px);
}

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

.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(30, 41, 59, 0.9) !important; color: #cbd5e1 !important;
    border-radius: 10px !important; transition: all 0.2s ease !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    border-color: #f59e0b !important; color: #f59e0b !important;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    border-color: #f59e0b !important; color: white !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px !important;
    background-color: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(30, 41, 59, 0.8) !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    color: white !important;
    border-color: #f59e0b !important;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ── TOP BAR HEADER ────────────────────────────────────────────────────────────
top_l, top_r = st.columns([5, 1])
with top_l:
    logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="height:36px; object-fit:contain;" alt="ONDA">' if logo_b64 else '🛡️'
    st.markdown(f"""
    <div class="app-header">
        <div class="app-header-left">
            {logo_img}
            <div>
                <div class="app-header-title">Plan de Prévention des Coupures WAN</div>
                <div class="app-header-subtitle">Planification d'actions préventives, Analyse d'impact &amp; Prédictions à 30 jours</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_r:
    st.write("")
    if st.button("← Retour Accueil", key="back_home_prev", use_container_width=True):
        st.switch_page("home.py")

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    inc = pd.read_csv(
        ARTIFACTS / "incidents_clean.csv",
        parse_dates=["date_incident", "date_ticket", "date_recovery", "date_closure"],
    )
    risks = pd.read_csv(ARTIFACTS / "latest_risk_scores.csv", parse_dates=["reference_date"])
    return inc, risks

inc, risks = load_data()

def style_chart(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Outfit"),
        xaxis=dict(gridcolor="rgba(30, 41, 59, 0.6)", zerolinecolor="rgba(30, 41, 59, 0.6)",
                   title_font=dict(size=12, color="#94a3b8"), tickfont=dict(size=10, color="#94a3b8")),
        yaxis=dict(gridcolor="rgba(30, 41, 59, 0.6)", zerolinecolor="rgba(30, 41, 59, 0.6)",
                   title_font=dict(size=12, color="#94a3b8"), tickfont=dict(size=10, color="#94a3b8")),
        legend=dict(bgcolor="rgba(15,23,42,0.6)", bordercolor="rgba(30, 41, 59, 0.8)",
                    font=dict(size=10, color="#cbd5e1")),
        margin=dict(t=42, b=40, l=40, r=30),
    )
    return fig

# ── KPI Banner ────────────────────────────────────────────────────────────────
total_inc        = len(inc)
wan_pct          = round((inc["category"] == "LIAISON_WAN").mean() * 100, 1)
elec_pct         = round((inc["category"] == "ELECTRICITE").mean() * 100, 1)
orange_pct       = round((inc["operator"] == "ORANGE").mean() * 100, 1)
high_risk_sites  = int((risks["risk_level"] == "ÉLEVÉ").sum())
avg_downtime     = round(inc["incident_duration_h"].mean(), 1)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Incidents totaux", f"{total_inc:,}".replace(",", " "))
k2.metric("Liaison WAN", f"{wan_pct}%")
k3.metric("Électricité", f"{elec_pct}%")
k4.metric("Opérateur Orange", f"{orange_pct}%")
k5.metric("Sites ÉLEVÉ actifs", high_risk_sites)
k6.metric("Durée moy. coupure", f"{avg_downtime} h")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Plan d'Action Prioritaire",
    "📅 Analyse Temporelle des Coupures",
    "⚡ Analyse par Cause & Opérateur",
    "🔮 Prévisions 30 Jours",
])

# ─── TAB 1 : Priority prevention action plan ─────────────────────────────────
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Plan d'Intervention Préventive Prioritaire")
    st.write(
        "Plan d'action généré automatiquement selon les scores de risque ML et l'analyse d'impact historique."
    )

    site_agg = (
        inc.groupby("site")
        .agg(
            total_inc=("ticket_number", "count"),
            wan_inc=("category", lambda x: (x == "LIAISON_WAN").sum()),
            elec_inc=("category", lambda x: (x == "ELECTRICITE").sum()),
            orange_inc=("operator", lambda x: (x == "ORANGE").sum()),
            iam_inc=("operator", lambda x: (x == "IAM").sum()),
            avg_dur=("incident_duration_h", "mean"),
            max_dur=("incident_duration_h", "max"),
        )
        .reset_index()
    )
    plan = risks.merge(site_agg, on="site", how="left").sort_values("risk_score", ascending=False)

    def recommend(row):
        actions = []
        if row.get("electric_incidents_90d", 0) >= 2:
            actions.append("⚡ Vérifier alimentation ondulée (UPS) — risque électrique élevé")
        if row.get("orange_incidents_90d", 0) >= 3:
            actions.append("📡 Escalader ticket chez Orange — lien principal instable")
        if row.get("iam_incidents_90d", 0) >= 3:
            actions.append("📡 Escalader ticket chez IAM — lien de secours instable")
        if row.get("downtime_90d_h", 0) >= 100:
            actions.append("🔧 Planifier mission technique sur site — indisponibilité critique")
        if row.get("days_since_last_incident", 999) <= 7:
            actions.append("🚨 Incident récent (< 7j) — surveillance renforcée requise")
        if not actions:
            actions.append("✅ Maintenir surveillance standard — aucun facteur aggravant identifié")
        return " | ".join(actions)

    plan["action_recommandée"] = plan.apply(recommend, axis=1)

    level_colors = {"ÉLEVÉ": "#ef4444", "MOYEN": "#f59e0b", "FAIBLE": "#10b981"}

    for _, row in plan.iterrows():
        color = level_colors.get(row["risk_level"], "#94a3b8")
        border = f"2px solid {color}"

        st.markdown(f"""
        <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(30,41,59,0.8);
                    border-left:{border}; border-radius:14px; padding:18px 22px;
                    margin-bottom:16px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="color:#f1f5f9; font-weight:800; font-size:1.1rem;">📍 {row['site']}</span>
            <span style="background:{color}22; border:1px solid {color}55;
                         color:{color}; border-radius:99px; padding:4px 16px;
                         font-size:0.8rem; font-weight:700;">
              {row['risk_level']} — Score : {row['risk_score']:.1f}/100
            </span>
          </div>
          <div style="color:#64748b; font-size:0.85rem; margin-bottom:10px;">
            <b style="color:#94a3b8;">Raison ML :</b> {row['risk_reasons']}
          </div>
          <div style="color:#e2e8f0; font-size:0.88rem; line-height:1.7;">
            <b style="color:#f59e0b;">Actions recommandées :</b><br>
            {row['action_recommandée'].replace(' | ', '<br>')}
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── TAB 2 : Temporal pattern analysis ───────────────────────────────────────
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📅 Patterns Temporels des Coupures WAN")
    st.write("Identification des périodes récurrentes de fragilité pour planifier les maintenances préventives.")

    c1, c2 = st.columns(2)

    with c1:
        monthly = (
            inc.assign(month_num=inc["date_incident"].dt.month)
            .groupby("month_num")
            .size()
            .reset_index(name="incidents")
        )
        month_names = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Jun",
                       7:"Jul",8:"Aoû",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}
        monthly["mois"] = monthly["month_num"].map(month_names)
        fig_m = px.bar(
            monthly, x="mois", y="incidents",
            title="Saisonnalité mensuelle des coupures",
            labels={"mois": "Mois", "incidents": "Nombre de coupures"},
            color="incidents",
            color_continuous_scale=[[0,"#1e3a8a"],[0.5,"#f59e0b"],[1,"#ef4444"]],
        )
        style_chart(fig_m)
        fig_m.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_m, use_container_width=True)

    with c2:
        dow_map = {0:"Lundi",1:"Mardi",2:"Mercredi",3:"Jeudi",4:"Vendredi",5:"Samedi",6:"Dimanche"}
        dow = (
            inc.assign(dow=inc["date_incident"].dt.dayofweek)
            .groupby("dow")
            .size()
            .reset_index(name="incidents")
        )
        dow["jour"] = dow["dow"].map(dow_map)
        fig_d = px.bar(
            dow, x="jour", y="incidents",
            title="Répartition par jour de la semaine",
            labels={"jour": "Jour", "incidents": "Coupures"},
            color="incidents",
            color_continuous_scale=[[0,"#1e3a8a"],[0.5,"#f59e0b"],[1,"#ef4444"]],
        )
        style_chart(fig_d)
        fig_d.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_d, use_container_width=True)

    yoy = (
        inc.assign(
            month=inc["date_incident"].dt.to_period("M").dt.to_timestamp(),
            year=inc["date_incident"].dt.year.astype(str),
        )
        .groupby(["month", "year"])
        .size()
        .reset_index(name="incidents")
    )
    fig_yoy = px.line(
        yoy, x="month", y="incidents", color="year",
        markers=True,
        title="Évolution mensuelle des incidents (2021-2024)",
        labels={"month": "Date", "incidents": "Coupures", "year": "Année"},
        color_discrete_sequence=["#38bdf8", "#818cf8", "#f59e0b", "#10b981", "#ef4444"],
    )
    style_chart(fig_yoy)
    st.plotly_chart(fig_yoy, use_container_width=True)

    st.markdown("#### ⏱️ Durée moyenne de coupure selon l'heure de survenue")
    inc_hour = (
        inc.assign(heure=inc["date_incident"].dt.hour)
        .groupby("heure")
        .agg(avg_dur=("incident_duration_h", "mean"), count=("ticket_number", "count"))
        .reset_index()
    )
    fig_h = px.bar(
        inc_hour, x="heure", y="avg_dur",
        title="Durée moyenne de coupure par heure (0-23h)",
        labels={"heure": "Heure (0-23h)", "avg_dur": "Durée moy. (h)"},
        color="avg_dur",
        color_continuous_scale=[[0,"#1e3a8a"],[0.5,"#f59e0b"],[1,"#ef4444"]],
    )
    style_chart(fig_h)
    st.plotly_chart(fig_h, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── TAB 3 : Cause & Operator analysis ───────────────────────────────────────
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ Analyse par Cause de Coupure &amp; Opérateur Responsible")

    c1, c2 = st.columns(2)

    with c1:
        cat_data = inc["category"].value_counts().reset_index()
        cat_data.columns = ["Catégorie", "Incidents"]
        label_map = {"LIAISON_WAN": "Coupure Liaison WAN", "ELECTRICITE": "Panne Électricité",
                     "AUTRE": "Autre", "VPN_FIREWALL": "VPN / Firewall"}
        cat_data["Catégorie"] = cat_data["Catégorie"].map(label_map).fillna(cat_data["Catégorie"])
        fig_cat = px.pie(
            cat_data, names="Catégorie", values="Incidents", hole=0.5,
            title="Répartition par catégorie d'incident",
            color_discrete_sequence=["#3b82f6", "#f59e0b", "#10b981", "#818cf8"],
        )
        style_chart(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        op_data = inc["operator"].value_counts().reset_index()
        op_data.columns = ["Opérateur", "Incidents"]
        op_map = {"ORANGE": "Orange", "IAM": "IAM (Maroc Telecom)", "NON_IDENTIFIE": "Non Identifié"}
        op_data["Opérateur"] = op_data["Opérateur"].map(op_map).fillna(op_data["Opérateur"])
        fig_op = px.pie(
            op_data, names="Opérateur", values="Incidents", hole=0.5,
            title="Répartition par opérateur télécom",
            color_discrete_sequence=["#f97316", "#38bdf8", "#6b7280"],
        )
        style_chart(fig_op)
        st.plotly_chart(fig_op, use_container_width=True)

    dur_cat = (
        inc.groupby("category")["incident_duration_h"]
        .agg(["mean", "median", "max"])
        .reset_index()
        .rename(columns={"category": "Catégorie", "mean": "Moyenne (h)",
                         "median": "Médiane (h)", "max": "Maximum (h)"})
    )
    dur_cat["Catégorie"] = dur_cat["Catégorie"].map(label_map).fillna(dur_cat["Catégorie"])

    st.markdown("#### ⏱️ Durée des coupures par catégorie (heures)")
    st.dataframe(dur_cat.round(1), use_container_width=True, hide_index=True)

    st.markdown("#### 💥 Top 10 — Coupures les plus longues enregistrées")
    worst = (
        inc.nlargest(10, "incident_duration_h")[
            ["site", "date_incident", "incident_duration_h", "category", "operator", "incident_nature_raw"]
        ]
        .rename(columns={
            "site": "Site", "date_incident": "Date",
            "incident_duration_h": "Durée (h)", "category": "Catégorie",
            "operator": "Opérateur", "incident_nature_raw": "Nature",
        })
    )
    st.dataframe(worst, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── TAB 4 : 30-day forecast ─────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔮 Prévisions de Coupures — Horizon 30 Jours")
    st.write(
        "Projection ML des probabilités d'incident sur chaque site aéroportuaire pour les 30 prochains jours."
    )

    forecast = (
        risks[["site", "risk_probability", "risk_score", "risk_level",
               "incidents_30d", "downtime_90d_h", "days_since_last_incident"]]
        .sort_values("risk_probability", ascending=False)
        .reset_index(drop=True)
    )
    forecast["Probabilité (%)"] = (forecast["risk_probability"] * 100).round(1)
    forecast["Rang"] = forecast.index + 1

    top15 = forecast.head(15).copy()
    color_map = {"ÉLEVÉ": "#ef4444", "MOYEN": "#f59e0b", "FAIBLE": "#10b981"}
    top15["color"] = top15["risk_level"].map(color_map)

    fig_fc = go.Figure()
    for _, row in top15.iterrows():
        fig_fc.add_trace(go.Bar(
            x=[row["Probabilité (%)"]],
            y=[row["site"]],
            orientation="h",
            marker_color=row["color"],
            name=row["risk_level"],
            showlegend=False,
            text=f"{row['Probabilité (%)']}%",
            textposition="outside",
            textfont=dict(color="#cbd5e1", size=11, family="Outfit"),
        ))

    for lvl, col in color_map.items():
        fig_fc.add_trace(go.Bar(x=[None], y=[None], orientation="h",
                                name=lvl, marker_color=col, showlegend=True))

    style_chart(fig_fc)
    fig_fc.update_layout(
        title="Top 15 — Probabilité de coupure dans les 30 prochains jours",
        xaxis=dict(title="Probabilité (%)", range=[0, 110], gridcolor="rgba(30,41,59,0.6)"),
        yaxis=dict(autorange="reversed"),
        height=480,
        barmode="overlay",
        showlegend=True,
        legend_title_text="Niveau de risque",
    )
    st.plotly_chart(fig_fc, use_container_width=True)

    st.markdown("#### 📋 Tableau complet des prévisions par site")
    display_forecast = forecast[["Rang", "site", "Probabilité (%)", "risk_level",
                                  "incidents_30d", "downtime_90d_h", "days_since_last_incident"]].rename(columns={
        "site": "Site", "risk_level": "Niveau",
        "incidents_30d": "Incidents (30j)", "downtime_90d_h": "Indisponibilité 90j (h)",
        "days_since_last_incident": "Jours depuis dernier incident",
    })
    st.dataframe(display_forecast, use_container_width=True, hide_index=True)

    st.write("")
    st.download_button(
        "📥 Exporter les prévisions en CSV",
        data=display_forecast.to_csv(index=False).encode("utf-8-sig"),
        file_name="onda_previsions_30j.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
