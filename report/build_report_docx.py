from pathlib import Path
import shutil
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(r"C:\Users\nouam\Downloads\ONDA_Projet_Sauvegarde")
REPORT = ROOT / "report"
OUT_DIR = REPORT / "output" / "docx"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE = Path(r"C:\Users\nouam\Downloads\template rapport de stage 4IIR (1).docx")
OUT = OUT_DIR / "rapport_final.docx"

IMG = REPORT / "images"
ONDA = IMG / "onda"
CR = IMG / "cyberrange"
DIAG = IMG / "diagrams"

TITLE = "Conception d'un modèle d'analyse des risques et d'alertes prédictives basé sur les données de maintenance des actifs informatiques"
SHORT_TITLE = "Analyse des risques et alertes prédictives des actifs informatiques"


def clear_element(el):
    for child in list(el):
        el.remove(child)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text, bold=False, color="000000"):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_table_borders(table, color="B7C3D0", sz="6"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), sz)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def add_field(run, instruction, cached=""):
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = cached
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(text)
    run._r.append(fld_end)


def set_run(run, size=12, bold=False, italic=False, color="000000", font="Times New Roman"):
    run.font.name = font
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)
    return run


def set_para(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=True, before=6, after=6, spacing=1.5):
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Cm(0.8) if first_line and align == WD_ALIGN_PARAGRAPH.JUSTIFY else Cm(0)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    return p


def add_text(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=True, before=6, after=6):
    p = doc.add_paragraph(style="Body Text")
    set_para(p, align, first_line, before, after)
    set_run(p.add_run(text))
    return p


def add_heading(doc, text, level=1, page_break=False):
    if page_break:
        p = doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)
    style = f"Heading {level}"
    p = doc.add_paragraph(style=style)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.keep_together = True
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.first_line_indent = Cm(0)
    return p.add_run(text)


def add_caption(doc, text):
    p = doc.add_paragraph(style="Caption")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(9)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run(text), size=10, italic=True, color="404040")
    return p


def add_figure(doc, filename, caption, width=15.2, page_break=False):
    if page_break:
        p = doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)
    path = Path(filename)
    if not path.exists():
        add_text(doc, f"[Figure non disponible : {path.name}]", align=WD_ALIGN_PARAGRAPH.CENTER, first_line=False)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run()
    r.add_picture(str(path), width=Cm(width))
    add_caption(doc, caption)


def add_table(doc, headers, rows, widths=None, caption=None):
    if caption:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Cm(0)
        set_run(p.add_run(caption), size=10, bold=True, color="1F4E79")
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    try:
        table.style = "Table Grid"
    except KeyError:
        pass
    set_table_borders(table)
    for i, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], header, bold=True, color="FFFFFF")
        set_cell_shading(table.rows[0].cells[i], "1F4E79")
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value)
            if ridx % 2 == 1:
                set_cell_shading(cells[i], "EEF3F8")
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Cm(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Paragraph")
        p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.first_line_indent = Cm(-0.35)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        set_run(p.add_run("• " + item))


def add_toc_field(doc, instruction):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run()
    add_field(r, instruction, "Ouvrir le document dans Word puis actualiser le champ")
    return p


def add_index_entry(doc, text):
    p = doc.add_paragraph(style="List Paragraph")
    p.paragraph_format.left_indent = Cm(0.2)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.0
    set_run(p.add_run(text), size=10)
    return p


def clear_header_footer(hf):
    clear_element(hf._element)


def configure_section(section, main=False):
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.header_distance = Cm(1.25)
    section.footer_distance = Cm(1.25)
    section.different_first_page_header_footer = False
    clear_header_footer(section.header)
    clear_header_footer(section.footer)
    if not main:
        return
    hp = section.header.paragraphs[0] if section.header.paragraphs else section.header.add_paragraph()
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.paragraph_format.space_after = Pt(2)
    hp.paragraph_format.first_line_indent = Cm(0)
    hr = hp.add_run()
    add_field(hr, 'STYLEREF "Heading 1"', "Chapitre")
    set_run(hr, size=9, bold=True, color="1F4E79")
    add_bottom_border(hp, "1F4E79", "6")
    fp = section.footer.paragraphs[0] if section.footer.paragraphs else section.footer.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(2)
    fp.paragraph_format.first_line_indent = Cm(0)
    fr = fp.add_run(SHORT_TITLE + "   —   ")
    set_run(fr, size=9, color="555555")
    page_run = fp.add_run()
    add_field(page_run, "PAGE", "1")
    set_run(page_run, size=9, color="555555")
    add_top_border(fp, "1F4E79", "6")
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:start"), "1")
    section._sectPr.append(pg)


def add_bottom_border(p, color, size):
    p_pr = p._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    border = OxmlElement("w:bottom")
    border.set(qn("w:val"), "single")
    border.set(qn("w:sz"), size)
    border.set(qn("w:space"), "1")
    border.set(qn("w:color"), color)
    borders.append(border)


def add_top_border(p, color, size):
    p_pr = p._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    border = OxmlElement("w:top")
    border.set(qn("w:val"), "single")
    border.set(qn("w:sz"), size)
    border.set(qn("w:space"), "1")
    border.set(qn("w:color"), color)
    borders.append(border)


def configure_styles(doc):
    for name in ("Normal", "Body Text", "List Paragraph"):
        style = doc.styles[name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(12)
    body = doc.styles["Body Text"]
    body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    body.paragraph_format.first_line_indent = Cm(0.8)
    body.paragraph_format.line_spacing = 1.5
    body.paragraph_format.space_before = Pt(6)
    body.paragraph_format.space_after = Pt(6)
    for level, size in [(1, 17), (2, 14), (3, 12)]:
        style = doc.styles[f"Heading {level}"]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.italic = False
        style.font.color.rgb = RGBColor(31, 78, 121)
        style.paragraph_format.space_before = Pt(14 if level == 1 else 9)
        style.paragraph_format.space_after = Pt(8)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.keep_together = True
        style.paragraph_format.first_line_indent = Cm(0)
    try:
        cap = doc.styles["Caption"]
    except KeyError:
        cap = doc.styles.add_style("Caption", 1)
        cap.base_style = doc.styles["Body Text"]
    cap.font.name = "Times New Roman"
    cap._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    cap.font.size = Pt(10)
    cap.font.italic = True


def add_front_title(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(15)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run(text), size=17, bold=True, color="1F4E79")


def add_intro(doc, title, paragraphs):
    add_heading(doc, title, 1, page_break=True)
    for para in paragraphs:
        add_text(doc, para)


def build():
    shutil.copy2(TEMPLATE, OUT)
    doc = Document(str(OUT))
    body = doc._element.body
    sect_pr = body.sectPr
    for child in list(body):
        if child is not sect_pr:
            body.remove(child)
    configure_styles(doc)

    # Front cover, based on the EMSI template placeholders.
    first = doc.sections[0]
    configure_section(first, main=False)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(12)
    p.add_run().add_picture(str(ONDA / "onda_logo.png"), width=Cm(3.0))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(15)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run("OFFICE NATIONAL DES AÉROPORTS"), size=13, bold=True, color="1F4E79")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(25)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run("PROJET DE FIN D'ANNEE"), size=20, bold=True, color="1F4E79")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run("4ème Année en Ingénierie Informatique et Réseaux"), size=13, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run(TITLE), size=17, bold=True, color="1F4E79")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(22)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run("Rapport de projet — version technique intégrée"), size=12, italic=True, color="555555")
    add_table(doc, ["Réalisé par", "Encadrement"], [["Azzat Nouamane\nHnid Aimane", "Encadrement professionnel : Mme Jaouhari Ouafaa — ONDA\nEncadrement pédagogique : Mme Khadija Bousmar — EMSI"]], widths=[7.0, 8.0], caption=None)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(35)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run("Organisme d'accueil : Office National des Aéroports (ONDA)"), size=11, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run(p.add_run("Année universitaire : 2025–2026"), size=11)

    # Preliminary pages.
    doc.add_page_break()
    add_front_title(doc, "Dédicace")
    add_text(doc, "Nous dédions ce travail à nos familles, pour leur soutien constant, leur patience et la confiance qu’elles nous accordent tout au long de notre formation. Leur encouragement nous a accompagnés pendant les phases de recherche, de développement, de tests et de rédaction, parfois lorsque les difficultés techniques exigeaient davantage de temps et de persévérance.", align=WD_ALIGN_PARAGRAPH.CENTER, first_line=False)
    add_text(doc, "Nous dédions également ce projet à toutes les personnes qui nous ont transmis le goût de l’apprentissage et de l’innovation dans les domaines des réseaux, de la cybersécurité et de l’intelligence artificielle. À travers ce rapport, nous souhaitons valoriser le travail collectif, la responsabilité professionnelle et la volonté de construire des solutions utiles aux organisations qui dépendent de leurs systèmes d’information.", align=WD_ALIGN_PARAGRAPH.CENTER, first_line=False)
    doc.add_page_break()
    add_front_title(doc, "Remerciements")
    add_text(doc, "Nous remercions vivement Mme Jaouhari Ouafaa, notre encadrante au sein de l’ONDA, pour son accompagnement professionnel, sa disponibilité et les orientations qui nous ont permis de mieux comprendre les contraintes d’un réseau aéroportuaire. Ses remarques nous ont aidés à rapprocher les fonctionnalités développées des besoins concrets d’une équipe chargée de la continuité de service.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=True)
    add_text(doc, "Nous remercions également Mme Khadija Bousmar, notre encadrante pédagogique à l’EMSI, pour ses conseils méthodologiques, son suivi régulier et son attention portée à la qualité de la présentation. Nous lui sommes reconnaissants de nous avoir encouragés à structurer le travail selon une démarche claire, à justifier nos choix techniques et à exposer les limites de la solution avec honnêteté.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=True)
    add_text(doc, "Enfin, nous remercions les équipes de l’ONDA, nos enseignants et toutes les personnes qui ont contribué, directement ou indirectement, à rendre cette expérience formatrice. Les échanges, les lectures, les essais et les corrections successives ont enrichi notre compréhension de la maintenance informatique et de la cybersécurité. Ce projet est le résultat d’un effort de collaboration et de transmission.", align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=True)
    doc.add_page_break()
    add_front_title(doc, "Résumé")
    add_text(doc, "Ce projet porte sur la conception d’un modèle d’analyse des risques et d’alertes prédictives basé sur les données de maintenance des actifs informatiques de l’Office National des Aéroports. La solution exploite l’historique des incidents WAN de 27 sites pour estimer un score de risque sur un horizon de 30 jours, hiérarchiser les alertes et proposer des actions de prévention. L’objectif n’est pas de remplacer l’expertise des équipes, mais de leur fournir une information préparée, comparable et exploitable au moment de décider d’une intervention.")
    add_text(doc, "La plateforme associe un portail exécutif, un module de diagnostic du modèle, une gestion du facteur humain et un plan d’intervention préventive. Elle permet de passer d’une lecture dispersée des tickets à une vision structurée : les incidents sont agrégés, les tendances sont rendues visibles, les sites sont classés et les recommandations sont rattachées à des causes ou à des situations observées. Les résultats peuvent ainsi être discutés avec les responsables réseau et adaptés aux contraintes opérationnelles.")
    add_text(doc, "Un CyberRange isolé complète la validation en reproduisant un scénario d’incident de sécurité autorisé, depuis l’observation jusqu’à la détection et la remédiation. Cet environnement ne représente pas le réseau de production ; il sert à vérifier la capacité à collecter des preuves, à écrire des contrôles défensifs et à transformer les enseignements techniques en retour d’expérience. Cette intégration relie la continuité de service, la gouvernance de la maintenance et la préparation à la réponse aux incidents.")
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.8)
    set_run(p.add_run("Mots-clés : "), bold=True)
    set_run(p.add_run("analyse de risques, maintenance informatique, réseau WAN, apprentissage automatique, alertes prédictives, CyberRange, détection, REX."))
    doc.add_page_break()
    add_front_title(doc, "Abstract")
    add_text(doc, "This project addresses the design of a risk analysis and predictive alerting model based on IT asset maintenance data for Morocco’s National Airports Authority. The solution uses the incident history of 27 WAN sites to estimate a 30-day risk score, prioritize alerts and recommend preventive actions. It is designed as a decision-support system: the prediction highlights where attention should be focused, while operational teams retain responsibility for confirming the context and selecting the appropriate intervention.")
    add_text(doc, "The platform combines an executive portal, model diagnostics, human-factor controls and a preventive intervention plan. It organizes incident records into comparable indicators, makes the main risk drivers visible and links the result to concrete maintenance actions. An isolated CyberRange complements the validation by reproducing an authorized security-incident scenario, from observation to detection and remediation. The integrated approach connects service continuity, maintenance governance and incident-response readiness while keeping the production network outside the simulation perimeter.")
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.8)
    set_run(p.add_run("Keywords: "), bold=True)
    set_run(p.add_run("risk analysis, IT maintenance, WAN, machine learning, predictive alerts, CyberRange, detection, lessons learned."))
    doc.add_page_break()
    add_front_title(doc, "Table des matières")
    add_toc_field(doc, 'TOC \\o "1-3" \\h \\z \\u')
    add_text(doc, "La table des matières est générée automatiquement à partir des styles de titres. Dans Microsoft Word, clic droit sur la table puis « Mettre à jour les champs » pour actualiser les numéros de page.", align=WD_ALIGN_PARAGRAPH.CENTER, first_line=False, before=18)
    doc.add_page_break()
    add_front_title(doc, "Liste des figures")
    figure_titles = [
        "Figure 1. Chaîne intégrée : prédire, simuler, détecter, remédier et capitaliser.",
        "Figure 2. Diagramme global des cas d’utilisation.",
        "Figure 3. Architecture fonctionnelle de la solution intégrée.",
        "Figure 4. Séquence de production d’une alerte et de capitalisation.",
        "Figure 5. Modèle logique simplifié des données.",
        "Figure 6. Architecture de déploiement et périmètre isolé du CyberRange.",
        "Figure 7. Écran d’accès réservé au personnel ONDA autorisé.",
        "Figure 8. Portail exécutif ONDA Risk Intelligence.",
        "Figure 9. Accès aux trois modules principaux de la plateforme.",
        "Figure 10. Vue d’ensemble du risque réseau et classement dynamique des sites.",
        "Figure 11. Liste des alertes de risque actives.",
        "Figure 12. Fiche détaillée d’un site et historique d’incidents.",
        "Figure 13. Explorateur de données par site.",
        "Figure 14. Diagnostic du modèle : métriques, matrice de confusion et comparaison temporelle.",
        "Figure 15. Checklist de conformité avant une intervention sur équipement.",
        "Figure 16. Plan d’intervention préventive prioritaire.",
        "Figure 17. Topologie du laboratoire CyberRange isolé.",
        "Figure 18. Architecture pédagogique du CyberRange.",
        "Figure 19. Déroulement contrôlé du scénario et points de détection.",
        "Figure 20. Observation des services exposés dans le réseau de laboratoire.",
        "Figure 21. Observation des échanges réseau dans Wireshark.",
        "Figure 22. Preuve de session dans l’environnement de test.",
        "Figure 23. Analyse statique d’un artefact dans Ghidra.",
        "Figure 24. Graphe de flux utilisé pour comprendre le comportement de l’artefact.",
        "Figure 25. Règle YARA de détection dans le contexte de laboratoire.",
        "Figure 26. Règle Snort destinée à signaler un indicateur réseau.",
        "Figure 27. Mesures de remédiation et de durcissement proposées.",
        "Figure 28. Passage de la preuve technique à la décision défensive.",
    ]
    for figure_title in figure_titles:
        add_index_entry(doc, figure_title)
    doc.add_page_break()
    add_front_title(doc, "Liste des tableaux")
    table_titles = [
        "Tableau 1. Planification synthétique du projet.",
        "Tableau 2. Acteurs et responsabilités.",
        "Tableau 3. Exigences non fonctionnelles.",
        "Tableau 4. Dictionnaire synthétique des données.",
        "Tableau 5. Environnement de réalisation.",
        "Tableau 6. Paramètres de l’évaluation temporelle.",
        "Tableau 7. Matrice de confusion du modèle.",
        "Tableau 8. Récapitulatif des indicateurs.",
    ]
    for table_title in table_titles:
        add_index_entry(doc, table_title)

    # Main section begins at Introduction générale and restarts pagination at 1.
    main = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_section(main, main=True)
    add_heading(doc, "Introduction générale", 1, page_break=False)
    add_text(doc, "Les activités aéroportuaires dépendent d’une infrastructure informatique disponible, cohérente et surveillée. Au sein de l’Office National des Aéroports, les liaisons WAN relient les sites et transportent des services nécessaires à l’exploitation : enregistrement des passagers, échanges de données, systèmes de sûreté, traitement des bagages et communication interne. Une indisponibilité prolongée peut donc dépasser le simple incident technique et perturber directement la continuité des opérations.")
    add_text(doc, "Dans un fonctionnement principalement réactif, l’équipe intervient après l’apparition d’une coupure. Les historiques de tickets contiennent pourtant des signaux utiles : fréquence récente des incidents, durée d’indisponibilité, ancienneté du dernier incident, cause déclarée et opérateur concerné. La problématique de ce projet est ainsi la suivante : comment transformer ces données de maintenance en alertes prédictives compréhensibles et en actions de prévention applicables par les équipes réseau ?")
    add_text(doc, "Nous avons conçu une plateforme de pilotage qui calcule le risque des sites, permet l’exploration des historiques, documente les actions de maintenance et formalise les contrôles liés au facteur humain. Afin de compléter la vision disponibilité par une mise en situation de cybersécurité, un CyberRange isolé est intégré comme laboratoire de validation : les traces d’un scénario autorisé peuvent être observées, détectées, documentées et transformées en retour d’expérience.")
    add_text(doc, "Le périmètre retenu couvre la préparation des données, la construction d’un modèle de classification, la restitution des indicateurs et la formalisation d’un plan d’action. Il couvre aussi la prévention des erreurs de procédure et l’analyse défensive d’un scénario de laboratoire. En revanche, il ne prétend pas remplacer une solution de supervision temps réel, un système de ticketing de production ou un centre opérationnel de sécurité ; il constitue une couche d’aide à la décision et de capitalisation.")
    add_text(doc, "La démarche repose sur deux principes complémentaires. Le premier consiste à rendre la prédiction explicable en présentant les historiques, les causes et les métriques au lieu de fournir un score isolé. Le second consiste à conserver une séparation stricte entre les activités réelles et les essais de cybersécurité. Cette distinction protège le réseau de production et permet de discuter les résultats du laboratoire dans un cadre pédagogique et contrôlé.")
    add_text(doc, "Le rapport est organisé en quatre chapitres. Le premier présente le contexte ONDA, l’existant et la solution proposée. Le deuxième spécifie les besoins et les cas d’utilisation. Le troisième décrit la conception, les modèles et les architectures. Le quatrième présente la réalisation, les résultats, les interfaces et la simulation contrôlée en CyberRange.")

    # Chapter 1
    add_heading(doc, "Chapitre 1 : Présentation du cadre de projet", 1, page_break=True)
    add_heading(doc, "1.1 Introduction", 2)
    add_text(doc, "Ce chapitre situe le projet dans son environnement institutionnel et technique. Il décrit le rôle de l’ONDA, les contraintes d’un réseau WAN aéroportuaire, les limites d’une surveillance réactive et l’organisation retenue pour développer une solution de prévention intégrant l’analyse prédictive et l’expérimentation sécurisée.")
    add_text(doc, "L’enjeu est particulier dans un aéroport : la disponibilité informatique accompagne directement des activités qui fonctionnent selon des horaires, des flux de passagers et des exigences de sûreté. Une décision de maintenance doit donc tenir compte de la criticité du site, de la durée probable d’indisponibilité, de l’existence éventuelle d’un lien de secours et de la possibilité d’intervenir sans perturber l’exploitation. Ces éléments donnent une dimension opérationnelle au traitement des données historiques.")
    add_heading(doc, "1.2 Présentation de l’organisme d’accueil", 2)
    add_text(doc, "L’Office National des Aéroports (ONDA) est l’organisme marocain chargé de l’exploitation et de la gestion des aéroports nationaux. Son système d’information s’appuie sur des infrastructures distribuées, dont les liaisons WAN assurent la communication entre les sites et les services centraux. Dans ce contexte, la DSI et la direction des réseaux WAN doivent disposer d’une vision consolidée de l’état des sites, des incidents et des priorités d’intervention.")
    add_text(doc, "La diversité géographique des sites augmente la difficulté du pilotage. Les aéroports ne présentent pas tous les mêmes volumes de trafic, les mêmes conditions d’accès, les mêmes fournisseurs ou les mêmes dépendances électriques. Une coupure de liaison peut provenir d’un équipement, d’une alimentation, d’un opérateur télécom, d’un câble ou d’une erreur de manipulation. Un outil utile doit donc associer une vue nationale à une capacité d’analyse locale, afin d’éviter une lecture uniforme de situations différentes.")
    add_text(doc, "Le projet a été réalisé par le binôme Azzat Nouamane et Hnid Aimane. L’encadrement professionnel au sein de l’ONDA est assuré par Mme Jaouhari Ouafaa et l’encadrement pédagogique à l’EMSI par Mme Khadija Bousmar.")
    add_heading(doc, "1.3 Situation existante", 2)
    add_text(doc, "Les tickets de maintenance constituent une source historique riche, mais leur exploitation est généralement orientée vers le suivi d’incidents déjà ouverts. L’analyse manuelle rend difficile la comparaison de 27 sites, l’identification des signaux faibles et la priorisation homogène des actions. En parallèle, les incidents de sécurité et les erreurs de manipulation peuvent rester séparés des activités de maintenance, alors qu’ils affectent la même exigence de continuité de service.")
    add_text(doc, "Le fonctionnement existant peut être représenté par une succession d’étapes : déclaration d’un incident, qualification, recherche de la cause, intervention, rétablissement puis clôture du ticket. Cette chaîne est nécessaire, mais elle intervient surtout après la dégradation du service. La valeur du projet consiste à exploiter la même mémoire historique avant l’incident, pour détecter les combinaisons de signaux qui justifient une vérification préventive.")
    add_bullets(doc, [
        "suivi des incidents et des durées d’indisponibilité après leur survenue ;",
        "absence d’un classement prédictif commun à tous les sites ;",
        "difficulté à relier les causes, opérateurs, périodes et sites ;",
        "capitalisation inégale des contrôles préalables et des retours d’expérience ;",
        "validation sécurité réalisée dans un environnement distinct du pilotage opérationnel."
    ])
    add_heading(doc, "1.4 Critique de l’existant", 2)
    add_text(doc, "La principale limite n’est pas l’absence de données, mais l’absence d’une chaîne unifiée entre donnée, décision et action. Un tableau de tickets peut signaler un volume d’incidents sans indiquer quel site doit être traité en premier. De même, une simulation de sécurité peut produire des traces techniques sans les rattacher à un plan de remédiation ou à un REX opérationnel. Le projet répond à cette limite en plaçant l’alerte, l’intervention, la détection et la capitalisation dans un même parcours.")
    add_text(doc, "Une deuxième limite concerne l’interprétation des indicateurs. Un nombre important d’incidents ne signifie pas toujours que le risque actuel est maximal : une série de petits événements peut être moins urgente qu’une seule indisponibilité longue sur un site critique. C’est pourquoi le score combine plusieurs fenêtres temporelles et plusieurs dimensions, notamment la récence, la fréquence et la durée. Cette combinaison reste une approximation qui doit être confrontée au contexte connu par les professionnels.")
    add_heading(doc, "1.5 Solution proposée", 2, page_break=True)
    add_text(doc, "La solution proposée est une plateforme de supervision prédictive composée de quatre modules fonctionnels : un portail exécutif, un module de risque réseau piloté par un modèle de machine learning, un module facteur humain et REX, et un module de prévention des coupures WAN. Le CyberRange est positionné comme un laboratoire isolé relié au processus de validation : il permet d’examiner un scénario contrôlé, ses indicateurs de compromission et les mesures de détection/remédiation, sans toucher au réseau de production.")
    add_text(doc, "Le choix d’une architecture modulaire facilite l’évolution du projet. Les seuils de classement peuvent être ajustés sans modifier la checklist ; les indicateurs de prévention peuvent évoluer lorsque de nouvelles catégories d’incidents apparaissent ; le laboratoire peut être enrichi par d’autres scénarios sans changer le portail exécutif. Cette séparation clarifie également les responsabilités : le modèle fournit une estimation, l’équipe confirme l’urgence et le REX conserve la décision prise.")
    add_text(doc, "Le portail exécutif constitue le point d’entrée pour la lecture globale. Il rassemble les indicateurs essentiels, la distribution des niveaux de risque et le classement des sites les plus exposés. Cette vue permet à la direction de repérer rapidement les priorités, puis de transmettre la demande d’analyse à l’équipe compétente. Elle ne remplace pas les outils de supervision existants ; elle ajoute une lecture consolidée orientée vers la prévention.")
    add_text(doc, "Le module de risque transforme les historiques de maintenance en informations comparables. Pour chaque site, il prend en compte la fréquence des incidents, leur récence, les durées d’indisponibilité et les causes observées. Le module facteur humain complète cette analyse en vérifiant que les interventions sont préparées selon une procédure : sauvegarde de configuration, contrôle de l’intégrité, fenêtre d’intervention, notification, retour arrière et vérification après changement.")
    add_text(doc, "Le cycle se termine par la capitalisation. Une action réalisée, une alerte confirmée ou une simulation de sécurité doivent laisser une trace exploitable pour les équipes. Les résultats peuvent alors être rapprochés des incidents futurs afin d’évaluer l’efficacité des mesures prises. La plateforme forme ainsi une boucle d’amélioration dans laquelle la donnée sert à prévoir, la décision sert à agir et le retour d’expérience sert à améliorer la prochaine intervention.")
    add_figure(doc, DIAG / "solution_pipeline.png", "Figure 1. Chaîne intégrée : prédire, simuler, détecter, remédier et capitaliser.", width=15.0)
    add_heading(doc, "1.6 Méthode de développement", 2, page_break=True)
    add_text(doc, "Le développement suit une démarche itérative inspirée de Scrum. Le binôme découpe le projet en incréments : compréhension du besoin, préparation des données, construction du modèle, réalisation des interfaces, intégration du facteur humain, validation CyberRange et rédaction. Chaque incrément est vérifié à partir de critères observables : cohérence des données, lisibilité du score, fonctionnement des parcours, isolement du laboratoire et traçabilité des résultats.")
    add_text(doc, "À chaque itération, nous avons cherché à produire un résultat démontrable plutôt qu’une fonctionnalité isolée. La préparation des données devait alimenter une première mesure ; le modèle devait être visible dans une interface ; la checklist devait déclencher un état de conformité ; la simulation devait fournir des preuves et une recommandation défensive. Cette logique permet de vérifier progressivement que les composants contribuent bien au même objectif de prévention.")
    add_heading(doc, "1.7 Planification prévisionnelle", 2)
    add_table(doc, ["Itération", "Travaux principaux", "Livrable"], [
        ["S1", "Cadrage ONDA, collecte des attentes et inventaire des données", "Périmètre et objectifs"],
        ["S2", "Nettoyage, exploration et définition des indicateurs", "Jeu de données documenté"],
        ["S3", "Entraînement et évaluation du modèle", "Score et métriques"],
        ["S4", "Portail exécutif et module d’alertes", "Interfaces de pilotage"],
        ["S5", "Facteur humain, checklist et REX", "Module opérationnel"],
        ["S6", "Prévention WAN, opérateurs et prévisions", "Plan d’action"],
        ["S7", "CyberRange isolé et collecte des preuves", "Scénario de validation"],
        ["S8", "Intégration, tests et rédaction", "Version finale du rapport"]
    ], widths=[2.0, 9.5, 3.5], caption="Tableau 1. Planification synthétique du projet.")
    add_heading(doc, "1.8 Conclusion", 2, page_break=True)
    add_text(doc, "Le contexte ONDA justifie une approche qui dépasse le simple affichage de tickets. La solution retenue transforme l’historique de maintenance en priorités prédictives et ajoute un laboratoire CyberRange pour relier disponibilité, sécurité et REX. Le chapitre suivant précise les besoins fonctionnels, les contraintes et les acteurs de cette solution.")
    add_text(doc, "Le cadre de projet est donc défini par un équilibre entre ambition et maîtrise du périmètre. Les fonctionnalités livrées sont suffisamment larges pour couvrir la décision, la prévention et la validation, tout en restant compatibles avec les données disponibles et avec un environnement de démonstration. Cette base permet maintenant de formaliser les attentes des utilisateurs et les conditions de qualité à respecter.")
    add_text(doc, "La valeur du projet repose également sur la complémentarité des profils utilisateurs. Les responsables disposent d’une synthèse pour arbitrer les priorités, les ingénieurs ont accès aux éléments qui expliquent le score et les techniciens disposent de contrôles concrets avant modification. Le dispositif de prévention devient ainsi un support commun entre les personnes qui observent le risque, celles qui interviennent et celles qui capitalisent les résultats.")
    add_text(doc, "Ce cadre fixe enfin les limites de l’étude. Les données historiques sont exploitées pour construire une aide à la décision, mais toute alerte doit être confrontée à la situation réelle du site. De la même manière, le CyberRange sert uniquement à valider des pratiques défensives dans un environnement isolé. Ces principes guideront la spécification des besoins et la conception des fonctionnalités présentées dans les chapitres suivants.")

    # Chapter 2
    add_heading(doc, "Chapitre 2 : Spécification des besoins", 1, page_break=True)
    add_heading(doc, "2.1 Introduction", 2)
    add_text(doc, "La spécification traduit le problème métier en services attendus par les utilisateurs. Elle distingue les fonctions visibles dans la plateforme, les contraintes de qualité et de sécurité, puis formalise les interactions entre acteurs et système.")
    add_text(doc, "La spécification prend en compte des profils qui ne consultent pas le système avec le même niveau de détail. Un directeur recherche une synthèse et des priorités, un ingénieur veut comprendre les facteurs du score, un technicien a besoin de contrôles pratiques et un analyste sécurité examine des preuves. La solution doit donc offrir plusieurs niveaux de lecture sans perdre la cohérence des informations affichées.")
    add_heading(doc, "2.2 Acteurs du système", 2)
    add_table(doc, ["Acteur", "Responsabilité"], [
        ["Administrateur DSI", "Accéder à la vision globale, gérer les droits et contrôler les indicateurs."],
        ["Ingénieur réseau", "Examiner les alertes, les historiques, les causes et les actions de mitigation."],
        ["Responsable maintenance", "Prioriser les interventions, suivre les opérateurs et vérifier la prévention."],
        ["Analyste sécurité", "Observer les preuves du CyberRange, vérifier les indicateurs et proposer une remédiation."],
        ["Technicien", "Exécuter les checklists, documenter l’intervention et contribuer au REX."],
        ["Opérateur télécom", "Recevoir les escalades et traiter les incidents de liaison." ]
    ], widths=[4.5, 10.5], caption="Tableau 2. Acteurs et responsabilités.")
    add_heading(doc, "2.3 Besoins fonctionnels", 2)
    add_text(doc, "Les besoins fonctionnels sont organisés autour d’un cycle de prévention. Le système doit d’abord observer les historiques, ensuite produire une estimation, puis permettre la vérification humaine et le suivi de l’action. La simulation de sécurité suit le même principe : préparer un scénario, observer les événements, vérifier les détections et consigner les mesures correctives. Chaque fonction est associée à un résultat visible pour éviter que la prédiction ou la preuve ne reste sans suite opérationnelle.")
    add_bullets(doc, [
        "BF1 — Afficher une vue exécutive de l’état du réseau et de la distribution des niveaux de risque.",
        "BF2 — Calculer et classer un score de risque compris entre 0 et 100 pour chaque site.",
        "BF3 — Filtrer les alertes par niveau, rechercher un site et ouvrir sa fiche détaillée.",
        "BF4 — Consulter l’historique, les catégories d’incidents, la durée d’indisponibilité et la date du dernier incident.",
        "BF5 — Diagnostiquer le modèle à l’aide de métriques, d’une matrice de confusion et d’une courbe de comparaison.",
        "BF6 — Analyser les causes, les opérateurs et les saisonnalités pour générer des recommandations à 30 jours.",
        "BF7 — Contrôler une intervention par checklist, déclarer une erreur et enregistrer un REX.",
        "BF8 — Reproduire un scénario de sécurité en laboratoire isolé, collecter les preuves et relier la remédiation au REX."
    ])
    add_heading(doc, "2.4 Besoins non fonctionnels", 2)
    add_text(doc, "Les exigences non fonctionnelles sont importantes car la plateforme traite des informations liées à la disponibilité d’un service critique. La transparence du modèle, la protection des données, la continuité d’accès et l’isolement de la simulation sont aussi importants que la présence d’un graphique. Les choix de conception doivent donc favoriser la lisibilité, la vérifiabilité et la possibilité de revenir sur la décision prise.")
    add_table(doc, ["Qualité", "Exigence"], [
        ["Sécurité", "Le CyberRange doit être isolé du réseau de production et les données sensibles doivent être limitées."],
        ["Traçabilité", "Les recommandations, actions et REX doivent être datés et associés à un site ou à un scénario."],
        ["Lisibilité", "Les niveaux de risque doivent être visibles au premier regard et expliqués par des indicateurs."],
        ["Reproductibilité", "Les versions des données, du modèle et du scénario de test doivent être identifiables."],
        ["Performance", "Les tableaux et graphiques doivent rester consultables avec un volume de tickets historique."],
        ["Maintenabilité", "Les modules doivent être séparés afin de permettre l’évolution du score et des règles."],
        ["Portabilité", "La solution doit pouvoir être exécutée dans un environnement Python documenté."],
        ["Responsabilité", "Les alertes sont une aide à la décision et doivent être validées par un responsable humain."]
    ], widths=[4.0, 11.0], caption="Tableau 3. Exigences non fonctionnelles.")
    add_heading(doc, "2.5 Cas d’utilisation", 2)
    add_text(doc, "Le diagramme global regroupe les parcours principaux autour de quatre familles : piloter le réseau, analyser le risque, prévenir l’incident et capitaliser l’expérience. Le CyberRange n’est pas un module autonome destiné à lancer des actions sur une cible quelconque ; il est un cas d’utilisation de validation défensive, réalisé dans un périmètre explicitement autorisé.")
    add_text(doc, "Le premier parcours concerne le pilotage exécutif : le responsable consulte les indicateurs globaux, observe la répartition des niveaux de risque et identifie les sites qui nécessitent une attention prioritaire. Le deuxième concerne l’analyse technique : l’ingénieur filtre les sites, ouvre une fiche détaillée, vérifie les incidents récents et compare les éléments qui contribuent au score. Le troisième parcours transforme l’analyse en action grâce à la checklist de pré-intervention, au suivi des mesures de mitigation et aux recommandations du plan de prévention.")
    add_text(doc, "Ces cas d’utilisation forment une chaîne continue plutôt qu’une simple collection d’écrans. Une alerte doit pouvoir être expliquée par des données historiques, soumise à une vérification humaine, associée à une intervention puis documentée dans le REX. Le système distingue ainsi la décision automatique, qui produit une estimation, de la décision opérationnelle, qui reste validée par un responsable. Cette séparation améliore la traçabilité et limite le risque qu’un score soit interprété comme une certitude.")
    add_text(doc, "Le périmètre du CyberRange complète cette chaîne sur le plan de la sécurité. Les utilisateurs autorisés peuvent y observer un scénario de laboratoire, recueillir des preuves, tester une règle de détection et formuler une mesure de remédiation. Aucun cas d’utilisation ne prévoit de connexion directe au réseau de production : les résultats sont exportés sous forme de constats et de recommandations afin d’être examinés avant toute transposition.")
    add_figure(doc, DIAG / "usecase_global.png", "Figure 2. Diagramme global des cas d’utilisation.", width=15.2)
    add_heading(doc, "2.6 Description de cas d’utilisation représentatifs", 2)
    add_heading(doc, "2.6.1 Consulter les alertes de risque", 3)
    add_text(doc, "L’acteur ouvre le module de risque et sélectionne éventuellement un niveau ou un site. Le système charge le classement, affiche les éléments les plus critiques et permet d’ouvrir une fiche détaillée. Le résultat attendu est une liste priorisée, accompagnée des facteurs qui expliquent le score.")
    add_text(doc, "Le prérequis est la disponibilité d’un jeu de données préparé et d’un modèle identifié. Le scénario nominal se termine lorsque l’utilisateur dispose d’un site prioritaire et de ses indicateurs de contexte. En cas de données incomplètes, le système doit signaler la limite plutôt que présenter un score comme une certitude ; cette règle protège la qualité de la décision.")
    add_heading(doc, "2.6.2 Générer un plan de prévention", 3)
    add_text(doc, "Le responsable maintenance consulte les causes et les opérateurs, puis ouvre l’onglet des prévisions. Le système agrège l’historique et produit des recommandations telles que la vérification de l’alimentation secourue, la planification d’une mission technique ou l’escalade vers un opérateur.")
    add_text(doc, "La recommandation est ensuite transformée en action suivie : responsable, priorité, échéance et commentaire. Le système doit permettre de distinguer une action proposée d’une action confirmée, puis d’une action réalisée. Cette distinction est nécessaire pour évaluer plus tard si une prévention a effectivement réduit le risque ou si elle doit être adaptée.")
    add_heading(doc, "2.6.3 Valider une intervention", 3)
    add_text(doc, "Avant une modification, le technicien sélectionne le type d’intervention et coche les prérequis : sauvegarde de configuration, contrôle d’intégrité, fenêtre horaire, notification, rollback et vérification post-opération. Le système calcule un taux de conformité et signale un risque humain si des contrôles impératifs manquent.")
    add_text(doc, "Le parcours prévoit également un arrêt préventif. Si un contrôle critique n’est pas validé, l’intervention ne doit pas être considérée comme conforme, même si les autres cases sont cochées. Après l’opération, le technicien peut compléter le commentaire, joindre une preuve et signaler une difficulté rencontrée. Ces informations enrichissent le REX et contribuent à réduire la répétition des erreurs.")
    add_heading(doc, "2.6.4 Examiner une simulation de sécurité", 3)
    add_text(doc, "L’analyste sécurité exécute un scénario autorisé dans l’environnement Host-Only, observe les preuves réseau et système, puis consigne les indicateurs, les règles de détection et les mesures de remédiation. Le scénario est considéré comme un élément de validation et non comme un accès à une infrastructure réelle.")
    add_text(doc, "Le résultat attendu est un dossier de validation comprenant le périmètre, les hôtes de test, la chronologie, les observations, les alertes obtenues et les mesures recommandées. Une simulation incomplète reste utile si elle permet d’identifier un manque de visibilité ou une règle à améliorer. La priorité est donnée à la compréhension et à la défense, sans publier de procédure offensive applicable à un système tiers.")
    add_heading(doc, "2.7 Conclusion", 2)
    add_text(doc, "Les besoins montrent que la plateforme doit fournir à la fois une vue synthétique, des analyses explicables et des actions contrôlées. La spécification couvre la continuité WAN, le facteur humain et la sécurité de laboratoire dans un même parcours. La conception de ces flux et de leurs données est présentée au chapitre suivant.")
    add_text(doc, "Cette spécification fournit un critère de vérification pour la suite du projet : chaque interface, chaque indicateur et chaque capture doit pouvoir être rattaché à un besoin identifié. Elle évite également de confondre l’objectif de prédiction avec celui de simulation. L’un aide à prioriser la maintenance ; l’autre vérifie la préparation à la détection et à la remédiation dans un cadre isolé.")

    # Chapter 3
    add_heading(doc, "Chapitre 3 : Conception du système", 1, page_break=True)
    add_heading(doc, "3.1 Introduction", 2)
    add_text(doc, "La conception décrit les échanges entre les composants, la structure des données et l’architecture de déploiement. Elle tient compte du caractère hybride du projet : l’analyse prédictive s’appuie sur des historiques de maintenance, tandis que le CyberRange est un environnement de test isolé qui fournit des preuves complémentaires.")
    add_text(doc, "Un principe de conception guide l’ensemble du système : conserver la traçabilité entre une donnée source et la décision produite. Un score doit pouvoir être expliqué par une période, un site et des indicateurs ; une recommandation doit être reliée à une cause ou à une tendance ; une preuve CyberRange doit être rattachée à une étape du scénario. Cette traçabilité facilite la validation par les utilisateurs et la rédaction du REX.")
    add_heading(doc, "3.2 Architecture fonctionnelle", 2)
    add_text(doc, "L’architecture fonctionnelle suit une chaîne de traitement en cinq niveaux. Les données sont d’abord préparées, puis transformées en variables temporelles. Le modèle produit une probabilité et un score de risque. Les modules d’interface expliquent les résultats et génèrent une action. Enfin, l’exécution et les preuves alimentent le retour d’expérience.")
    add_text(doc, "La chaîne sépare les opérations de calcul des opérations de présentation. Les agrégations temporelles sont réalisées avant l’affichage afin que les différentes vues utilisent les mêmes valeurs. Le portail ne recalcule pas une interprétation différente pour chaque écran : il restitue un référentiel commun, ce qui réduit les incohérences entre le tableau de bord, la fiche d’un site et le plan de prévention.")
    add_figure(doc, DIAG / "solution_pipeline.png", "Figure 3. Architecture fonctionnelle de la solution intégrée.", width=15.0)
    add_heading(doc, "3.3 Modélisation dynamique", 2)
    add_heading(doc, "3.3.1 Séquence d’une alerte prédictive", 3)
    add_text(doc, "La séquence commence par l’import ou la mise à jour des tickets. Le service de préparation calcule les fenêtres temporelles, puis le modèle évalue la probabilité d’incident. Le portail classe les sites et le responsable valide l’action. Une intervention peut déclencher la checklist ; une simulation peut produire des preuves de détection ; dans les deux cas, les résultats sont capitalisés dans le REX.")
    add_text(doc, "Le flux prévoit un contrôle avant la diffusion de l’alerte. Les dates doivent être cohérentes, le site doit appartenir au référentiel et les valeurs nécessaires au calcul doivent être disponibles. Si une anomalie est détectée, elle doit être signalée à l’utilisateur ou exclue du calcul selon une règle documentée. Cette étape évite de donner une apparence de précision à une prédiction fondée sur une donnée incorrecte.")
    add_figure(doc, DIAG / "sequence_alert.png", "Figure 4. Séquence de production d’une alerte et de capitalisation.", width=15.0)
    add_heading(doc, "3.3.2 Activité globale", 3)
    add_bullets(doc, [
        "Importer les tickets et contrôler la qualité des dates, sites, catégories et durées.",
        "Construire les variables récentes et historiques sans utiliser d’informations futures.",
        "Produire le score et affecter un niveau de risque selon les seuils retenus.",
        "Afficher l’alerte, vérifier l’impact et sélectionner une action de prévention.",
        "Contrôler l’intervention ou analyser les preuves CyberRange.",
        "Enregistrer la décision, les résultats et le REX."
    ])
    add_heading(doc, "3.4 Modélisation statique et modèle de données", 2)
    add_text(doc, "Le modèle de données relie les sites, les incidents, les prédictions, les actions de maintenance et les retours d’expérience. L’entité ScenarioCyberRange conserve la référence d’un scénario isolé et ses preuves, mais ne mélange pas les données de simulation avec les tickets de production. Cette séparation limite les ambiguïtés d’interprétation.")
    add_text(doc, "Les relations sont pensées pour conserver l’historique. Une nouvelle prédiction ne doit pas écraser la précédente, car l’évolution du score peut être utile pour mesurer l’effet d’une action. De même, une action de maintenance peut être associée à plusieurs observations et un REX peut référencer un incident, une intervention ou une simulation. Cette approche permet d’étudier non seulement le risque, mais aussi la réponse apportée.")
    add_figure(doc, DIAG / "data_model.png", "Figure 5. Modèle logique simplifié des données.", width=15.0)
    add_table(doc, ["Entité", "Attributs principaux", "Rôle"], [
        ["Site", "id_site, code, nom, région", "Référentiel des 27 sites suivis."],
        ["Incident", "id, site, date, catégorie, opérateur, durée", "Historique des événements WAN."],
        ["Prediction", "site, date, probabilité, score, niveau", "Résultat calculé par le modèle."],
        ["ActionMaintenance", "site, type, statut, date, commentaire", "Suivi des mesures préventives."],
        ["Checklist", "intervention, prérequis, conformité", "Contrôle des étapes avant production."],
        ["REX", "auteur, contexte, cause, action, date", "Capitalisation des enseignements."],
        ["ScenarioCyberRange", "id, hôtes, scénario, preuves, remédiation", "Validation sécurité isolée."]
    ], widths=[4.0, 6.0, 5.0], caption="Tableau 4. Dictionnaire synthétique des données.")
    add_heading(doc, "3.5 Architecture logicielle", 2)
    add_text(doc, "La plateforme est organisée en modules Python correspondant aux responsabilités fonctionnelles. home.py porte la vue exécutive ; app.py regroupe l’analyse de risque et le diagnostic du modèle ; human_factor.py gère checklist, erreurs et REX ; prevention.py regroupe l’analyse des causes, opérateurs et prévisions. Les composants de visualisation et de préparation des données sont appelés par ces modules, ce qui facilite les évolutions.")
    add_text(doc, "Cette organisation rend les tests plus simples. Les fonctions de préparation peuvent être vérifiées indépendamment du rendu graphique, les règles de checklist peuvent être testées avec plusieurs états de conformité et les indicateurs de prévention peuvent être comparés aux agrégations historiques. L’interface devient ainsi une couche de restitution, tandis que les règles métier restent identifiables et modifiables.")
    add_heading(doc, "3.6 Architecture matérielle et déploiement", 2)
    add_text(doc, "Le portail est consulté depuis un poste DSI via un navigateur. La couche applicative exécute les calculs et restitue les tableaux de bord. Les données historiques sont stockées dans un espace contrôlé. Le CyberRange est déployé séparément dans VirtualBox avec un réseau Host-Only, de sorte que les machines de test communiquent entre elles sans accès à Internet ni au réseau de production.")
    add_text(doc, "Le déploiement doit aussi prendre en compte la gestion des versions et des sauvegardes. Le modèle, les fichiers de données, les règles de détection et les captures doivent être conservés avec un identifiant ou une date de référence. En cas de réentraînement, l’équipe doit pouvoir comparer les métriques et comprendre pourquoi le classement des sites a changé. Cette discipline est indispensable avant toute utilisation régulière de l’outil.")
    add_figure(doc, DIAG / "deployment_architecture.png", "Figure 6. Architecture de déploiement et périmètre isolé du CyberRange.", width=15.0)
    add_heading(doc, "3.7 Principes de sécurité de la simulation", 2)
    add_bullets(doc, [
        "Utiliser uniquement des machines vulnérables prévues pour l’entraînement, notamment Metasploitable 2.",
        "Maintenir le mode Host-Only et vérifier l’absence de route vers Internet avant l’exercice.",
        "Ne pas réutiliser les charges, identifiants ou indicateurs sur une infrastructure réelle.",
        "Conserver les captures comme preuves de laboratoire, avec leur contexte et leur date.",
        "Associer chaque observation à une mesure défensive : détection, durcissement, segmentation ou remédiation."
    ])
    add_heading(doc, "3.8 Conclusion", 2)
    add_text(doc, "La conception relie le score de risque aux flux opérationnels et maintient une séparation nette entre la production et la simulation. Les modèles de données, la séquence d’alerte et l’architecture Host-Only fournissent une base cohérente pour la réalisation. Les interfaces et les résultats obtenus sont présentés dans le dernier chapitre.")
    add_text(doc, "Les choix de conception donnent donc une place centrale à l’explicabilité et à la sécurité du périmètre. Le système est capable de produire un résultat exploitable, mais il conserve les conditions nécessaires à son interprétation : origine de la donnée, période d’analyse, responsable de la décision et environnement de validation. Cette cohérence constitue le lien entre la conception théorique et les éléments réalisés.")

    # Chapter 4
    add_heading(doc, "Chapitre 4 : Réalisation du système", 1, page_break=True)
    add_heading(doc, "4.1 Introduction", 2)
    add_text(doc, "Ce chapitre présente l’environnement de réalisation, les interfaces de la plateforme ONDA, les résultats du modèle et la validation complémentaire menée dans le CyberRange. Les captures sont utilisées comme éléments de preuve visuelle de la solution et du laboratoire de test.")
    add_text(doc, "La réalisation est présentée dans l’ordre d’utilisation. Nous commençons par la préparation des données et l’évaluation, puis nous décrivons les écrans qui rendent les résultats accessibles aux différents profils. Nous terminons par le scénario CyberRange, qui montre comment les observations de sécurité peuvent être documentées et réinjectées dans une démarche de prévention.")
    add_heading(doc, "4.2 Environnement matériel et logiciel", 2)
    add_text(doc, "L’environnement de développement a été choisi pour permettre une expérimentation reproductible et une présentation claire des résultats. Les outils de traitement servent à préparer les historiques et à calculer les indicateurs ; les outils de visualisation rendent ces indicateurs accessibles ; VirtualBox fournit un périmètre séparé pour la simulation. Les versions et les paramètres importants doivent être conservés avec le projet afin de faciliter une reprise ultérieure.")
    add_text(doc, "La partie applicative est organisée autour de modules Python séparant les responsabilités : le portail exécutif présente la synthèse, le module de risque exploite les agrégations et les scores, le module facteur humain gère les contrôles de procédure et le module de prévention regroupe les analyses de causes et les recommandations. Cette séparation facilite la maintenance du code et permet de faire évoluer une fonction sans remettre en cause les autres parcours.")
    add_text(doc, "La préparation des données et l’évaluation du modèle sont exécutées dans un environnement contrôlé, avec un schéma de données documenté et des paramètres conservés. Pour reproduire une expérience, il faut disposer du même périmètre d’observations, des mêmes règles de nettoyage et d’une date de référence comparable. La conservation de ces éléments permet de distinguer une évolution réelle du risque d’une simple modification de la préparation.")
    add_text(doc, "La simulation de cybersécurité est isolée dans VirtualBox au moyen d’un réseau Host-Only. Les machines prévues pour la formation communiquent uniquement dans le laboratoire, tandis que les captures, les règles et les conclusions sont conservées comme éléments de preuve. Cette configuration réduit le risque de propagation et rappelle que les outils de test doivent être utilisés uniquement sur des systèmes explicitement autorisés.")
    add_table(doc, ["Composant", "Technologies / configuration"], [
        ["Développement", "Python, notebooks/scripts d’analyse, environnement virtuel documenté."],
        ["Interface", "Application web Python avec tableaux, graphiques, filtres et formulaires."],
        ["Données", "Historique des incidents WAN et variables temporelles par site."],
        ["Modèle", "Régression logistique pour une classification binaire et un score probabiliste."],
        ["Simulation", "VirtualBox, Kali Linux 2024 et Metasploitable 2."],
        ["Observation", "Wireshark, traces réseau, analyse statique et règles de détection." ]
    ], widths=[4.0, 11.0], caption="Tableau 5. Environnement de réalisation.")
    add_heading(doc, "4.3 Préparation des données et modèle", 2)
    add_text(doc, "Le jeu exploité contient 864 incidents historiques répartis sur 27 sites. Les variables décrivent notamment les incidents sur 7, 30, 90 et 180 jours, les durées récentes, la moyenne et le maximum de durée, le nombre d’incidents par cause ou opérateur, ainsi que le nombre de jours depuis le dernier incident. La séparation temporelle évite d’entraîner le modèle sur des informations postérieures à la période évaluée.")
    add_text(doc, "La préparation commence par l’harmonisation des dates, des codes de site, des catégories et des durées. Les incidents sont ensuite regroupés selon plusieurs fenêtres afin de représenter à la fois une activité récente et un profil historique. Cette représentation est importante : un site peut avoir peu d’incidents dans la dernière semaine tout en conservant une tendance défavorable sur plusieurs mois. Les agrégations permettent au modèle d’exploiter ces deux dimensions.")
    add_text(doc, "La cible correspond à l’existence d’un incident dans la période de prédiction. Les variables utilisées pour une date donnée doivent être calculées à partir des informations disponibles avant cette date. Le découpage temporel est donc préférable à un mélange aléatoire des lignes, car il reproduit davantage le fonctionnement réel : entraîner sur le passé, puis évaluer sur une période future.")
    add_table(doc, ["Élément", "Valeur"], [
        ["Fenêtre d’entraînement", "2021-12-06 → 2023-12-25 (2 916 observations)"],
        ["Fenêtre de test", "2024-01-01 → 2024-09-23 (1 053 observations)"],
        ["Modèle", "Régression logistique"],
        ["Horizon opérationnel", "30 jours"],
        ["Référence de l’interface", "25 octobre 2024"]
    ], widths=[5.0, 10.0], caption="Tableau 6. Paramètres de l’évaluation temporelle.")
    add_heading(doc, "4.4 Résultats du modèle", 2)
    add_text(doc, "Le modèle fournit une bonne capacité de rappel, ce qui est cohérent avec un usage de prévention où manquer un site à risque peut être plus coûteux que déclencher une vérification supplémentaire. Les valeurs observées sont : accuracy 62,39 %, précision 54,70 %, rappel 88,44 %, F1-score 67,59 %, ROC-AUC 0,777 et PR-AUC 0,705. L’interface d’accueil affiche un indicateur arrondi de 62 % ; il correspond à l’accuracy du modèle et non à la précision au sens strict.")
    add_text(doc, "La précision indique la proportion d’alertes réellement associées à un incident, tandis que le rappel mesure la proportion d’incidents retrouvés par le modèle. Dans une logique de prévention, le rappel élevé est utile pour ne pas laisser de côté les sites qui méritent une vérification. En contrepartie, la précision montre qu’une partie des alertes devra être examinée par un professionnel avant de déclencher une intervention.")
    add_text(doc, "La lecture conjointe des indicateurs est importante. Sur la période de validation, 413 incidents sont correctement détectés, ce qui explique le rappel élevé, alors que 342 observations sans incident sont également signalées comme positives, ce qui réduit la précision. Ce comportement peut être acceptable lorsque le coût d’une vérification préventive est inférieur au coût d’une coupure non anticipée. Il doit cependant être suivi afin d’éviter que les équipes ne reçoivent trop d’alertes peu actionnables.")
    add_text(doc, "Le F1-score synthétise le compromis entre précision et rappel, tandis que les courbes ROC et précision-rappel donnent une vision plus large du classement lorsque le seuil de décision varie. Dans un contexte de maintenance, le seuil ne doit pas être choisi uniquement pour maximiser une métrique : il doit aussi tenir compte de la capacité de l’équipe à traiter les alertes, de la criticité du site et de la disponibilité d’une fenêtre d’intervention.")
    add_table(doc, ["Réalité / prédiction", "Sans incident", "Incident"], [["Sans incident", "244", "342"], ["Incident", "54", "413"]], widths=[5.0, 5.0, 5.0], caption="Tableau 7. Matrice de confusion du modèle.")
    add_text(doc, "Les scores sont une aide à la décision. Ils ne remplacent pas l’expertise de l’équipe réseau, notamment lorsque les données sont incomplètes, que le contexte opérationnel change ou qu’une intervention récente n’est pas encore reflétée dans l’historique.")
    add_text(doc, "La matrice de confusion confirme également ce compromis : 413 incidents sont correctement identifiés, tandis que 54 incidents sont classés comme sans incident. Les 342 faux positifs ne doivent pas être interprétés uniquement comme un défaut ; ils représentent des situations où une vérification est proposée sans qu’un incident soit ensuite constaté. Le suivi de ces cas est important pour ajuster les seuils, améliorer les variables et éviter une surcharge des équipes.")
    add_heading(doc, "4.5 Portail exécutif", 2)
    add_figure(doc, ONDA / "onda_login.png", "Figure 7. Écran d’accès réservé au personnel ONDA autorisé.", width=15.0)
    add_figure(doc, ONDA / "onda_home.png", "Figure 8. Portail exécutif ONDA Risk Intelligence.", width=15.0)
    add_figure(doc, ONDA / "onda_modules.png", "Figure 9. Accès aux trois modules principaux de la plateforme.", width=15.0)
    add_text(doc, "Le portail exécutif présente les indicateurs de synthèse : incidents analysés, sites suivis, sites à risque élevé, indicateur de performance du modèle et période historique. La distribution des niveaux et le top des sites critiques permettent à un décideur d’identifier rapidement les priorités.")
    add_text(doc, "La page d’accueil joue également un rôle de communication. Elle transforme des résultats techniques en une lecture directement compréhensible : le nombre de sites suivis, la proportion de niveaux de risque et le classement des cinq sites prioritaires. Les couleurs servent à distinguer les catégories, mais le texte et les chiffres restent nécessaires pour éviter qu’une couleur seule ne soit prise comme une conclusion.")
    add_heading(doc, "4.6 Module de risque et exploration des sites", 2)
    add_figure(doc, ONDA / "onda_overview.png", "Figure 10. Vue d’ensemble du risque réseau et classement dynamique des sites.", width=15.0)
    add_figure(doc, ONDA / "onda_alerts.png", "Figure 11. Liste des alertes de risque actives.", width=15.0)
    add_figure(doc, ONDA / "onda_detail.png", "Figure 12. Fiche détaillée d’un site et historique d’incidents.", width=15.0)
    add_figure(doc, ONDA / "onda_explorer.png", "Figure 13. Explorateur de données par site.", width=15.0)
    add_text(doc, "À la date de référence, les sites les plus exposés sont 129-OUARZAZATE, 199-ZAGORA, 159-BENS-SLIMANE, 218-BOUARFA et 229-GUELMIM. Par exemple, la fiche de 129-OUARZAZATE affiche un score de 99,9/100, cinq incidents sur 30 jours et 380,8 heures d’indisponibilité sur 90 jours. À l’inverse, la fiche 001-CASABLANCA illustre un site à faible risque avec un score de 2,7/100 et aucune indisponibilité sur 90 jours dans la capture considérée.")
    add_text(doc, "La fiche détaillée évite une lecture trop rapide du classement. Elle permet de vérifier si le score est cohérent avec la récence du dernier incident, les événements observés sur 90 jours et la répartition des catégories. L’explorateur apporte une vue complémentaire pour un site qui n’est pas nécessairement dans le top des alertes. L’ingénieur peut ainsi passer du niveau national au diagnostic local sans changer de source de données.")
    add_text(doc, "Cette navigation à plusieurs niveaux aide à transformer un classement en décision. Le tableau de bord sert à organiser la priorité, la fiche de site sert à comprendre la situation et l’explorateur sert à retrouver le contexte historique complet. Avant toute action, l’équipe peut donc comparer la tendance du site, la durée des indisponibilités, la cause déclarée et l’opérateur concerné. Une alerte est ainsi traitée comme un signal à qualifier, et non comme une intervention automatique.")
    add_text(doc, "Dans le cas d’un site fortement classé, la recommandation peut combiner une vérification de l’alimentation, une revue du lien principal ou de secours et une prise de contact avec l’opérateur. Pour un site faiblement classé, l’absence d’alerte ne dispense pas d’un suivi normal : elle indique seulement qu’aucune priorité particulière ne ressort des données disponibles à la date considérée. Cette interprétation maintient le rôle de l’outil comme aide au pilotage.")
    add_heading(doc, "4.7 Diagnostic du modèle", 2)
    add_figure(doc, ONDA / "onda_model.png", "Figure 14. Diagnostic du modèle : métriques, matrice de confusion et comparaison temporelle.", width=15.0)
    add_text(doc, "Le diagnostic rend la performance interprétable par les équipes techniques. La matrice de confusion montre le compromis entre détection et fausses alertes. La courbe de probabilité prédite comparée au taux observé permet de suivre la stabilité du modèle sur la période de test et de repérer les évolutions qui nécessiteraient une réévaluation.")
    add_text(doc, "Cette page permet aussi d’installer une culture de suivi du modèle. Une performance mesurée une seule fois ne garantit pas une performance permanente : les habitudes de maintenance, les opérateurs, la topologie et la qualité de saisie peuvent évoluer. Le diagnostic doit donc être consulté lors des réentraînements et après une modification importante du périmètre des sites.")
    add_heading(doc, "4.8 Facteur humain et REX", 2)
    add_figure(doc, ONDA / "onda_human.png", "Figure 15. Checklist de conformité avant une intervention sur équipement.", width=15.0)
    add_text(doc, "Le module impose une vérification avant modification en production : sauvegarde de la configuration, intégrité du firmware, fenêtre horaire, notification du centre de supervision, plan de rollback et contrôle de connectivité après rechargement. Le taux de conformité et l’alerte de risque humain rendent visibles les prérequis non validés. Le REX complète cette approche en conservant les erreurs, leurs causes et les règles à appliquer lors de futures interventions.")
    add_text(doc, "L’intérêt de cette checklist est de rendre explicites des gestes parfois considérés comme évidents. Dans une situation urgente, un technicien peut se concentrer sur le rétablissement et oublier la sauvegarde, la notification ou le retour arrière. La plateforme transforme ces points en une étape formelle, mesurable et partageable. Elle ne remplace pas une procédure approuvée, mais elle aide à vérifier que la procédure est appliquée.")
    add_heading(doc, "4.9 Prévention des coupures WAN", 2)
    add_figure(doc, ONDA / "onda_prevention.png", "Figure 16. Plan d’intervention préventive prioritaire.", width=15.0)
    add_text(doc, "Le module de prévention agrège les causes et opérateurs associés aux incidents. Il met en évidence la part de la catégorie liaison WAN, la part liée à l’électricité, la contribution d’Orange et le nombre de sites actuellement élevés. Pour chaque site, les recommandations sont formulées en langage opérationnel : vérification de l’UPS, mission technique sur site, surveillance renforcée ou escalade vers l’opérateur concerné.")
    add_text(doc, "L’analyse temporelle complète cette lecture en recherchant des périodes où les coupures sont plus fréquentes. Elle peut orienter la planification des contrôles, mais elle doit être interprétée avec le calendrier des travaux, les changements de fournisseur et les événements exceptionnels. Une saisonnalité n’est pas une cause en elle-même ; elle constitue un signal à confronter aux informations de terrain.")
    add_heading(doc, "4.10 Mise en œuvre du CyberRange", 2)
    add_text(doc, "La validation sécurité a été conduite dans un laboratoire Host-Only avec Kali Linux 2024 comme machine d’analyse et Metasploitable 2 comme machine vulnérable. Les captures fournies montrent les adresses 192.168.243.129 pour Kali et 192.168.243.128 pour la cible. Ces adresses sont propres au réseau de laboratoire observé ; elles ne constituent pas une consigne de connexion à une infrastructure réelle.")
    add_text(doc, "Le scénario suit une progression pédagogique : identifier les hôtes du laboratoire, observer les services, examiner les traces produites, analyser un artefact et tester des contrôles de détection. La cible est une machine volontairement vulnérable conçue pour l’entraînement. Toutes les manipulations sont réalisées dans le réseau isolé, avec l’objectif de comprendre les preuves et les mesures de défense, et non de reproduire ces actions sur un système tiers.")
    add_figure(doc, CR / "cr_network.png", "Figure 17. Topologie du laboratoire CyberRange isolé.", width=15.0)
    add_figure(doc, CR / "cr_architecture.png", "Figure 18. Architecture pédagogique du CyberRange.", width=15.0)
    add_figure(doc, CR / "cr_killchain.png", "Figure 19. Déroulement contrôlé du scénario et points de détection.", width=15.0)
    add_heading(doc, "4.10.1 Observation et collecte de preuves", 3)
    add_figure(doc, CR / "cr_nmap.png", "Figure 20. Observation des services exposés dans le réseau de laboratoire.", width=15.0)
    add_figure(doc, CR / "cr_wireshark.png", "Figure 21. Observation des échanges réseau dans Wireshark.", width=15.0)
    add_figure(doc, CR / "cr_shell.png", "Figure 22. Preuve de session dans l’environnement de test.", width=15.0)
    add_text(doc, "L’objectif de cette étape est de documenter les traces observables : hôtes, services, échanges, événements et contexte temporel. Les détails d’exploitation ne sont pas reproduits comme une procédure opérationnelle ; le rapport se concentre sur les contrôles, les preuves et la défense.")
    add_text(doc, "Les captures réseau permettent de compléter les journaux applicatifs. Elles peuvent révéler une séquence de connexions, un transfert inhabituel ou une communication persistante. Pour être utiles, elles doivent être accompagnées de métadonnées : date, machine utilisée, adresse du laboratoire, filtre appliqué et interprétation. Sans ce contexte, une image isolée est difficile à reproduire et à comparer.")
    add_heading(doc, "4.10.2 Analyse et détection", 3)
    add_figure(doc, CR / "cr_decompile.png", "Figure 23. Analyse statique d’un artefact dans Ghidra.", width=15.0)
    add_figure(doc, CR / "cr_ghidra_graph.png", "Figure 24. Graphe de flux utilisé pour comprendre le comportement de l’artefact.", width=15.0)
    add_figure(doc, CR / "cr_yara.png", "Figure 25. Règle YARA de détection dans le contexte de laboratoire.", width=15.0)
    add_figure(doc, CR / "cr_snort.png", "Figure 26. Règle Snort destinée à signaler un indicateur réseau.", width=15.0)
    add_text(doc, "L’analyse statique et les signatures transforment les observations en contrôles réutilisables. Les règles sont testées uniquement sur les artefacts et flux du CyberRange. Leur transfert vers un environnement ONDA nécessiterait une validation, une adaptation aux journaux disponibles et l’accord des responsables de sécurité.")
    add_text(doc, "L’analyse statique aide à repérer des fonctions, des chaînes ou des comportements qui peuvent devenir des indicateurs. Les signatures YARA ciblent des caractéristiques d’un fichier, tandis qu’une règle réseau de type Snort cherche un motif dans un flux. Ces approches sont complémentaires, mais elles peuvent produire des faux positifs et doivent être testées sur des données représentatives avant toute mise en production.")
    add_heading(doc, "4.10.3 Remédiation et REX", 3)
    add_figure(doc, CR / "cr_remediation.png", "Figure 27. Mesures de remédiation et de durcissement proposées.", width=15.0)
    add_figure(doc, CR / "cr_transition.png", "Figure 28. Passage de la preuve technique à la décision défensive.", width=15.0)
    add_text(doc, "La remédiation porte sur la segmentation, la réduction de l’exposition des services, le filtrage, la supervision, la sauvegarde des configurations et la mise à jour maîtrisée. Chaque mesure doit être associée à un responsable, une échéance et une preuve de vérification. Cette logique rejoint le module REX : le résultat de la simulation devient une leçon exploitable dans les futures opérations.")
    add_text(doc, "Le passage de la preuve à l’action est essentiel. Une alerte sans responsable peut être ignorée, et une recommandation sans preuve de clôture ne permet pas de vérifier son efficacité. Le REX doit donc décrire le contexte, ce qui a été observé, la décision prise, le résultat obtenu et l’amélioration proposée. Cette structure rend l’expérience utile à une équipe qui n’a pas participé à la simulation initiale.")
    add_heading(doc, "4.11 Limites et précautions", 2)
    add_text(doc, "Les limites concernent à la fois les données, le modèle, l’interface et la simulation. Les résultats présentés sont ceux d’un prototype démontrable à partir des informations disponibles. Une industrialisation demanderait une gouvernance des données, une gestion des accès, un raccordement aux sources opérationnelles et une validation par les responsables de la DSI et de la sécurité.")
    add_bullets(doc, [
        "Les données disponibles permettent principalement un score au niveau du site ; une prédiction au niveau de chaque équipement nécessiterait un identifiant et des attributs d’actif fiables.",
        "Les performances mesurées dépendent de la qualité des tickets, de l’équilibre des classes et de la stabilité des causes déclarées.",
        "Un score élevé signale une priorité de vérification, mais ne prouve pas qu’une coupure aura lieu.",
        "Le CyberRange est un environnement pédagogique isolé ; ses résultats ne doivent pas être généralisés sans validation sécurité et opérationnelle.",
        "Certaines captures de simulation proviennent de scénarios distincts ; elles sont présentées comme preuves complémentaires et non comme une session unique non documentée."
    ])
    add_heading(doc, "4.12 Conclusion", 2)
    add_text(doc, "La réalisation met en œuvre une plateforme capable de passer de l’historique de maintenance à une décision priorisée. Les interfaces couvrent la vision exécutive, le diagnostic technique, la checklist humaine et la prévention WAN. La validation CyberRange ajoute une dimension de détection et de remédiation, tout en conservant l’isolement nécessaire. L’ensemble constitue une base cohérente pour améliorer progressivement la qualité des données, la précision du modèle et l’intégration aux processus réels de la DSI.")
    add_text(doc, "La valeur principale du système est donc la continuité du parcours : comprendre le risque, décider d’une vérification, contrôler l’intervention, observer les résultats et mémoriser l’expérience. Cette continuité donne une cohérence aux différents modules et permet d’envisager des améliorations futures sans perdre l’objectif initial de prévention des interruptions.")

    # Closing pages.
    add_heading(doc, "Conclusion générale", 1, page_break=True)
    add_text(doc, "Ce projet a permis de concevoir une approche intégrée de l’analyse des risques et des alertes prédictives à partir des données de maintenance des actifs informatiques de l’ONDA. En exploitant les historiques de 27 sites WAN, la plateforme calcule un score à 30 jours, classe les priorités et propose des actions de prévention compréhensibles par les équipes. Le portail exécutif facilite la décision, le module de risque rend les indicateurs et les performances du modèle visibles, le module facteur humain réduit les oublis avant intervention et le REX organise la capitalisation. Chaque composant répond ainsi à une étape du même problème : éviter qu’un signal connu ne soit ignoré jusqu’à devenir une interruption coûteuse.")
    add_text(doc, "La simulation menée dans un CyberRange Host-Only complète cette vision en donnant un cadre contrôlé pour observer des traces, tester des détections et formaliser des mesures de remédiation. Elle rappelle que la disponibilité d’un service ne dépend pas uniquement d’un équipement ou d’un opérateur ; elle dépend aussi de la capacité à surveiller, à réagir et à apprendre. Les preuves techniques obtenues dans le laboratoire peuvent donc servir de support pédagogique pour discuter la segmentation, le filtrage, la supervision et la documentation des incidents.")
    add_text(doc, "Les résultats doivent toutefois être interprétés avec prudence. Le modèle décrit principalement un risque au niveau site, dépend de la qualité des tickets et reste une aide à la décision. La performance mesurée doit être suivie dans le temps, les faux positifs doivent être analysés et toute alerte doit être confrontée au contexte opérationnel. De la même manière, les règles de détection issues du CyberRange ne peuvent pas être appliquées directement à la production sans validation, adaptation et accord des responsables compétents.")
    add_text(doc, "Les perspectives sont l’enrichissement du référentiel d’actifs, l’ajout de données de topologie et de supervision temps réel, le suivi du drift du modèle, l’intégration d’une authentification et d’un journal d’audit, ainsi que la validation progressive des règles de détection dans un environnement conforme aux procédures de sécurité de l’ONDA. À terme, cette évolution pourrait fournir un historique complet reliant l’état d’un site, son risque estimé, les interventions réalisées, les preuves observées et l’efficacité des mesures prises.")
    add_heading(doc, "Bibliographie et Nétographie", 1, page_break=True)
    for ref in [
        "[1] Documentation Python, Python Software Foundation, https://docs.python.org/3/.",
        "[2] Scikit-learn, User Guide — Logistic Regression and model evaluation, https://scikit-learn.org/stable/user_guide.html.",
        "[3] Pandas Documentation, User Guide, https://pandas.pydata.org/docs/.",
        "[4] VirtualBox User Manual, Oracle, https://www.virtualbox.org/manual/.",
        "[5] Wireshark Documentation, User’s Guide, https://www.wireshark.org/docs/.",
        "[6] Ghidra Documentation, National Security Agency, https://ghidra-sre.org/.",
        "[7] YARA Documentation, https://yara.readthedocs.io/.",
        "[8] Snort Documentation, Cisco Talos, https://www.snort.org/documents.",
        "[9] MITRE ATT&CK, Enterprise Matrix, https://attack.mitre.org/.",
        "[10] OWASP, Secure Coding Practices and Application Security Verification resources, https://owasp.org/.",
        "[11] Documentation interne du projet ONDA : historiques d’incidents, écrans de la plateforme et résultats d’évaluation, 2024.",
        "[12] Rapport technique CyberRange du binôme, éléments de laboratoire et captures intégrées au présent rapport."
    ]:
        p = doc.add_paragraph(style="List Paragraph")
        p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.first_line_indent = Cm(-0.7)
        p.paragraph_format.space_after = Pt(5)
        set_run(p.add_run(ref))
    add_heading(doc, "Annexes", 1, page_break=True)
    add_heading(doc, "Annexe A — Principaux indicateurs du projet", 2)
    add_table(doc, ["Indicateur", "Valeur"], [
        ["Incidents historiques analysés", "864"],
        ["Sites aéroportuaires", "27"],
        ["Horizon de prédiction", "30 jours"],
        ["Accuracy", "62,39 %"],
        ["Précision", "54,70 %"],
        ["Rappel", "88,44 %"],
        ["F1-score", "67,59 %"],
        ["PR-AUC", "0,705"]
    ], widths=[9.0, 6.0], caption="Tableau 8. Récapitulatif des indicateurs.")
    add_heading(doc, "Annexe B — Périmètre de la simulation", 2)
    add_text(doc, "La simulation est limitée à un réseau Host-Only contrôlé, à des machines prévues pour la formation et à des objectifs de détection/remédiation. Elle ne fournit aucune autorisation d’essai sur le réseau ONDA ou sur un tiers. Toute reprise opérationnelle doit faire l’objet d’une validation formelle, d’un périmètre défini et d’une supervision compétente.")

    # Update-fields flag and core properties.
    settings = doc.settings._element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")
    props = doc.core_properties
    props.title = TITLE
    props.subject = "Projet de fin d’année — ONDA / EMSI"
    props.author = "Azzat Nouamane et Hnid Aimane"
    props.keywords = "ONDA, maintenance, risques, alertes prédictives, WAN, CyberRange"
    props.comments = "Version restructurée conformément au modèle de rapport 4IIR."
    doc.save(str(OUT))
    print(OUT)


if __name__ == "__main__":
    build()
