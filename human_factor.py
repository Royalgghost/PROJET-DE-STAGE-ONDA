from __future__ import annotations

import json
import datetime
import base64
from pathlib import Path
import pandas as pd
import plotly.express as px
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

# ── Load sites ────────────────────────────────────────────────────────────────
@st.cache_data
def load_sites() -> list[str]:
    try:
        risks = pd.read_csv(ARTIFACTS / "latest_risk_scores.csv")
        return sorted(risks["site"].unique().tolist())
    except Exception:
        return ["001-AGADIR", "002-CASABLANCA", "005-MARRAKECH", "007-FEZ", "010-TANGER"]

# ── REX reports helpers ───────────────────────────────────────────────────────
def load_rex_reports() -> list:
    rex_path = ARTIFACTS / "rex_reports.json"
    if rex_path.exists():
        try:
            with open(rex_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    # Seed data
    return [
        {
            "date": "10/08/2026",
            "site": "002-CASABLANCA",
            "type": "Erreur de configuration VLAN / Routage",
            "severity": "Moyen",
            "description": "Omission de la configuration du tronc VLAN 10 après mise à jour firmware. Restauration en 45 minutes.",
            "lesson": "Toujours copier-coller la configuration de sauvegarde avant rechargement du commutateur."
        },
        {
            "date": "05/08/2026",
            "site": "005-MARRAKECH",
            "type": "Omission de sauvegarde de configuration",
            "severity": "Critique",
            "description": "Aucune sauvegarde locale n'a été effectuée avant modification de la table de routage statique. Reprise à zéro nécessaire.",
            "lesson": "Rendre obligatoire le script de backup automatisé avant modification."
        }
    ]

def save_rex_report(report: dict):
    rex_path = ARTIFACTS / "rex_reports.json"
    reports = load_rex_reports()
    reports.append(report)
    with open(rex_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

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

[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
section[data-testid="stSidebarContent"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
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
.app-header-subtitle { font-size: 0.82rem; color: #10b981; font-weight: 500; margin-top: 2px; }

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
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(30, 41, 59, 0.9) !important; color: #cbd5e1 !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: #10b981 !important; color: #10b981 !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    border-color: #10b981 !important; color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #34d399, #10b981) !important;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.4) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: #0b1329 !important;
    border: 1px solid rgba(30, 41, 59, 0.9) !important; color: #f8fafc !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
}

/* Custom progress bar */
.progress-bar-bg {
    width: 100%; height: 12px; background: rgba(30, 41, 59, 0.8);
    border-radius: 99px; overflow: hidden; margin: 12px 0 16px 0;
}
.progress-bar-fill {
    height: 100%; border-radius: 99px;
    transition: width 0.4s ease;
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
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    border-color: #10b981 !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ── TOP BAR HEADER ────────────────────────────────────────────────────────────
top_l, top_r = st.columns([5, 1])
with top_l:
    logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="height:36px; object-fit:contain;" alt="ONDA">' if logo_b64 else '🧠'
    st.markdown(f"""
    <div class="app-header">
        <div class="app-header-left">
            {logo_img}
            <div>
                <div class="app-header-title">Facteur Humain &amp; REX Opérationnel</div>
                <div class="app-header-subtitle">Prévention des pannes d'origine humaine &amp; Standardisation des procédures DSI</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_r:
    st.write("")
    if st.button("← Retour Accueil", key="back_home_hf", use_container_width=True):
        st.switch_page("home.py")

# ── CONTENT ───────────────────────────────────────────────────────────────────
all_sites = load_sites()

t1, t2, t3, t4 = st.tabs([
    "📋 Check-lists d'Intervention", 
    "✍️ Déclaration d'Erreur & REX", 
    "📊 Statistiques du Facteur Humain",
    "📚 Sensibilisation & Bonnes Pratiques"
])

with t1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Liste de Contrôle de Conformité Procédurale")
    st.write("Sélectionnez le type d'intervention et validez chaque prérequis de sécurité avant d'appliquer vos modifications en production.")
    
    int_type = st.selectbox("Type d'intervention :", [
        "Mise à jour d'équipement (Routeur/Switch/Firewall)",
        "Changement physique de câble ou carte réseau",
        "Modification de la table de routage / VLAN"
    ])
    
    if "Mise à jour" in int_type:
        steps = [
            "Sauvegarde locale de la configuration actuelle (Show running-config > backup_xxxx.cfg)",
            "Vérification de l'intégrité de l'image firmware téléchargée (somme MD5/SHA256)",
            "Validation d'une fenêtre horaire à faible impact (heures creuses de l'aéroport)",
            "Notification du centre de supervision ONDA (DSI) avant le début de l'opération",
            "Plan de rollback prêt et validé en cas d'échec du chargement",
            "Vérification post-rechargement : connectivité des services critiques (VPN, Messagerie, etc.)"
        ]
    elif "Changement physique" in int_type:
        steps = [
            "Identification précise de l'équipement et des ports cibles (étiquetage)",
            "Vérification de la conformité du matériel de rechange (type de fibre, RJ45 blindé, etc.)",
            "Mise hors tension sécurisée de l'équipement si requis",
            "Remplacement physique et routage propre des câbles (sans tension mécanique)",
            "Vérification des indicateurs lumineux (diodes Link/Act)",
            "Validation du débit et du niveau de signal sur le port"
        ]
    else:
        steps = [
            "Sauvegarde de la table de routage actuelle",
            "Vérification du saut de routage (Next Hop) et de la métrique sur un outil de simulation",
            "Saisie des commandes par petits blocs (avec relecture par un pair si possible)",
            "Exécution d'un ping de diagnostic et traceroute vers les sites critiques",
            "Validation de l'absence de boucles de routage (Routing Loop)",
            "Notification de la fin de l'intervention à la DSI"
        ]
        
    checked_count = 0
    for i, step in enumerate(steps):
        if st.checkbox(step, key=f"step_{i}"):
            checked_count += 1
            
    pct = (checked_count / len(steps)) * 100
    
    bar_color = "#ef4444" if pct < 50 else ("#f59e0b" if pct < 100 else "#10b981")
    
    st.markdown(f"""
    <div style="margin-top: 18px;">
        <div style="display:flex; justify-content:space-between; font-weight:700; color:#f8fafc;">
            <span>Taux de conformité procédurale</span>
            <span style="color:{bar_color};">{pct:.0f}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {pct}%; background: {bar_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if pct == 100:
        st.success("✅ **Procédure 100% Conforme !** L'intervention est sécurisée. Vous pouvez clôturer la checklist.")
    elif pct >= 50:
        st.warning("⚠️ **Attention** : Des étapes cruciales de sécurité n'ont pas encore été complétées.")
    else:
        st.error("❌ **Risque Élevé** d'erreur humaine. Veuillez cocher les vérifications impératives.")
    st.markdown('</div>', unsafe_allow_html=True)
        
with t2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("✍️ Déclaration d'Erreur & REX (Retour d'Expérience)")
    st.write("Consignez de manière transparente les erreurs de manipulation ou de configuration réseau pour alimenter la base de connaissances collective DSI.")
    
    reports = load_rex_reports()
    
    with st.form("new_rex_form", clear_on_submit=True):
        f_site = st.selectbox("Site concerné :", all_sites)
        f_type = st.selectbox("Type d'erreur opérationnelle :", [
            "Erreur de configuration VLAN / Routage",
            "Omission de sauvegarde de configuration",
            "Erreur de branchement matériel (Câblage)",
            "Mauvaise manipulation d'alimentation",
            "Manque de coordination / Communication",
            "Autre erreur humaine"
        ])
        f_severity = st.selectbox("Gravité constatée :", ["Faible", "Moyen", "Critique"])
        f_desc = st.text_area("Description circonstanciée de l'erreur :", placeholder="Que s'est-il passé précisément ?")
        f_lesson = st.text_area("Enseignement tiré (Comment éviter cela à l'avenir ?) :", placeholder="Ex: Rendre obligatoire le double contrôle avant validation...")
        
        submit_rex = st.form_submit_button("Enregistrer le rapport REX", type="primary")
        if submit_rex:
            if f_desc.strip() == "" or f_lesson.strip() == "":
                st.error("Veuillez remplir la description et l'enseignement tiré.")
            else:
                new_rep = {
                    "date": datetime.datetime.now().strftime("%d/%m/%Y"),
                    "site": f_site,
                    "type": f_type,
                    "severity": f_severity,
                    "description": f_desc.strip(),
                    "lesson": f_lesson.strip()
                }
                save_rex_report(new_rep)
                st.success("✅ Rapport REX enregistré avec succès !")
                st.rerun()
                
    st.divider()
    st.subheader("📜 Base de Données REX Historique")
    if reports:
        rex_df = pd.DataFrame(reports)
        rex_df = rex_df.rename(columns={
            "date": "Date",
            "site": "Site",
            "type": "Type d'incident",
            "severity": "Gravité",
            "description": "Description de l'erreur",
            "lesson": "Leçon apprise"
        })
        st.dataframe(rex_df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun rapport REX n'a encore été déclaré.")
    st.markdown('</div>', unsafe_allow_html=True)
        
with t3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Analyse des Facteurs Humains dans les Incidents ONDA")
    st.write("Statistiques consolidées (simulées sur la base de REX historiques) de la part des erreurs humaines dans les coupures de liaisons.")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total REX Enregistrés", len(reports))
    col_m2.metric("Part des Erreurs Humaines", "18%", delta="-3% ce trimestre")
    col_m3.metric("Taux de Conformité Procédures", "94%")
    
    st.write("")
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        c_data = pd.DataFrame({
            "Origine": ["Panne Matérielle / Télécom", "Facteur Humain (Config/Manutention)", "Facteur Électrique / Externe"],
            "Proportion": [70, 18, 12]
        })
        fig_causes = px.pie(
            c_data, 
            names="Origine", 
            values="Proportion", 
            hole=0.5, 
            title="Origines principales des pannes WAN",
            color_discrete_sequence=["#1e3a8a", "#10b981", "#ef4444"]
        )
        style_chart(fig_causes)
        st.plotly_chart(fig_causes, use_container_width=True)
        
    with c_chart2:
        hf_data = pd.DataFrame({
            "Type d'erreur": ["Omission Backup", "Mauvais Port/Câble", "Erreur Masque/IP", "Double Assignation", "Changement non planifié"],
            "Fréquence": [12, 8, 15, 5, 9]
        }).sort_values("Fréquence", ascending=False)
        fig_hf = px.bar(
            hf_data, 
            x="Type d'erreur", 
            y="Fréquence", 
            title="Répartition des erreurs humaines par catégorie",
            labels={"Fréquence": "Occurrences"}
        )
        style_chart(fig_hf)
        fig_hf.update_traces(marker_color="#10b981")
        st.plotly_chart(fig_hf, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
with t4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📚 Sensibilisation &amp; Règles d'Or DSI ONDA")
    st.markdown(
        """
        #### 🌟 Les 5 Règles d'Or du Technicien Réseau ONDA
        
        1. **Sauvegarde Obligatoire** : Ne jamais modifier une configuration en production sans une sauvegarde locale récente vérifiée (`show running-config`).
        2. **Double Regard (Four-Eyes Principle)** : Les modifications d'adressage IP ou de routage dynamique complexes doivent être relues par un second ingénieur avant validation.
        3. **Horaires Adaptés** : Toute modification impactante doit se faire uniquement durant les fenêtres horaires de maintenance (01h00 - 05h00 locale pour les aéroports principaux).
        4. **Vérification de Câblage** : Toujours étiqueter les deux extrémités de chaque fibre optique ou câble Ethernet lors du déploiement.
        5. **Clôture et Notification** : Déclarer immédiatement la fin de l'intervention à la DSI avec les tests de connectivité de fin validés.
        
        ---
        
        #### 🚒 En cas de coupure accidentelle (Procédure d'Urgence) :
        - **Règle 1** : Ne pas paniquer. L'erreur est humaine. L'urgence est au rétablissement du service.
        - **Règle 2** : Appliquer immédiatement le plan de rollback (remise en état initiale).
        - **Règle 3** : Si le rollback échoue, contacter le responsable d'astreinte DSI et notifier l'opérateur (IAM/Orange).
        - **Règle 4** : Ne pas tenter de configurations 'hasardeuses' sous la pression de la panne.
        """
    )
    st.markdown('</div>', unsafe_allow_html=True)
