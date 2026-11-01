from pathlib import Path
import io
import re
import shutil
from xml.sax.saxutils import escape

from docx import Document
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.oxml.ns import qn
from docx.enum.text import WD_BREAK

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    NextPageTemplate, Table, TableStyle, Image, KeepTogether, Flowable,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(r"C:\Users\nouam\Downloads\ONDA_Projet_Sauvegarde")
REPORT = ROOT / "report"
DOCX = REPORT / "output" / "docx" / "rapport_final.docx"
OUT_DIR = REPORT / "output" / "pdf"
ASSET_DIR = OUT_DIR / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "rapport_final.pdf"

TITLE = "Conception d'un modèle d'analyse des risques et d'alertes prédictives basé sur les données de maintenance des actifs informatiques"
SHORT_TITLE = "Analyse des risques et alertes prédictives des actifs informatiques"

BLUE = colors.HexColor("#1F4E79")
LIGHT_BLUE = colors.HexColor("#EEF3F8")
GRAY = colors.HexColor("#555555")

# A Palatino-style serif is close to the academic typography of the source
# LaTeX report and is available on the host for embedding in the PDF.
PALATINO = Path(r"C:\Windows\Fonts\pala.ttf")
PALATINO_BOLD = Path(r"C:\Windows\Fonts\palab.ttf")
PALATINO_ITALIC = Path(r"C:\Windows\Fonts\palai.ttf")
PALATINO_BOLDITALIC = Path(r"C:\Windows\Fonts\palabi.ttf")
pdfmetrics.registerFont(TTFont("LaTeXPalatino", str(PALATINO)))
pdfmetrics.registerFont(TTFont("LaTeXPalatino-Bold", str(PALATINO_BOLD)))
pdfmetrics.registerFont(TTFont("LaTeXPalatino-Italic", str(PALATINO_ITALIC)))
pdfmetrics.registerFont(TTFont("LaTeXPalatino-BoldItalic", str(PALATINO_BOLDITALIC)))
pdfmetrics.registerFontFamily("LaTeXPalatino", normal="LaTeXPalatino", bold="LaTeXPalatino-Bold", italic="LaTeXPalatino-Italic", boldItalic="LaTeXPalatino-BoldItalic")


class NumberedCanvasState:
    main_start = None


def roman(number):
    values = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    result = ""
    for value, symbol in values:
        while number >= value:
            result += symbol
            number -= value
    return result


def front_page(canvas, doc):
    page = canvas.getPageNumber()
    if page <= 1:
        return
    canvas.saveState()
    canvas.setFont("LaTeXPalatino", 9)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(A4[0] / 2, 1.25 * cm, roman(page - 1))
    canvas.restoreState()


def main_page(canvas, doc):
    if NumberedCanvasState.main_start is None:
        NumberedCanvasState.main_start = canvas.getPageNumber()
    number = canvas.getPageNumber() - NumberedCanvasState.main_start + 1
    width, height = A4
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.5)
    canvas.line(2.5 * cm, height - 2.0 * cm, width - 2.5 * cm, height - 2.0 * cm)
    canvas.setFont("LaTeXPalatino-Italic", 9)
    canvas.setFillColor(colors.black)
    canvas.drawString(2.5 * cm, height - 1.75 * cm, "RAPPORT DE PROJET — ANALYSE DES RISQUES ET ALERTES PRÉDICTIVES")
    canvas.setFont("LaTeXPalatino-Bold", 9)
    canvas.drawRightString(width - 2.5 * cm, height - 1.75 * cm, "EMSI")
    canvas.line(2.5 * cm, 1.75 * cm, width - 2.5 * cm, 1.75 * cm)
    canvas.setFont("LaTeXPalatino", 9)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(width / 2, 1.42 * cm, str(number))
    canvas.restoreState()


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(2.5 * cm, 2.5 * cm, A4[0] - 5 * cm, A4[1] - 5 * cm, id="normal")
        self.addPageTemplates([
            PageTemplate(id="front", frames=[frame], onPage=front_page),
            PageTemplate(id="main", frames=[frame], onPage=main_page),
        ])

    def beforeDocument(self):
        super().beforeDocument()
        NumberedCanvasState.main_start = None

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in ("PDFHeading1", "PDFHeading2", "PDFHeading3"):
                level = int(style[-1]) - 1
                text = re.sub(r"<[^>]+>", "", flowable.getPlainText())
                key = f"h{level}-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page))


class SmallRule(Flowable):
    def __init__(self, width=15 * cm):
        super().__init__()
        self.width = width
        self.height = 0.2 * cm

    def draw(self):
        self.canv.setStrokeColor(BLUE)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, self.width, 0)


def make_styles():
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "PDFBody", parent=styles["BodyText"], fontName="LaTeXPalatino", fontSize=12,
        leading=16, alignment=TA_JUSTIFY, firstLineIndent=0.65 * cm,
        spaceBefore=4, spaceAfter=4, textColor=colors.black,
    )
    centered = ParagraphStyle("PDFCentered", parent=body, alignment=TA_CENTER, firstLineIndent=0)
    h1 = ParagraphStyle(
        "PDFHeading1", parent=styles["Heading1"], fontName="LaTeXPalatino-Bold", fontSize=20,
        leading=24, textColor=BLUE, spaceBefore=18, spaceAfter=9, keepWithNext=True,
    )
    h2 = ParagraphStyle(
        "PDFHeading2", parent=styles["Heading2"], fontName="LaTeXPalatino-Bold", fontSize=14,
        leading=18, textColor=BLUE, spaceBefore=9, spaceAfter=6, keepWithNext=True,
    )
    h3 = ParagraphStyle(
        "PDFHeading3", parent=styles["Heading3"], fontName="LaTeXPalatino-Bold", fontSize=12,
        leading=16, textColor=colors.HexColor("#305C82"), spaceBefore=8, spaceAfter=5, keepWithNext=True,
    )
    caption = ParagraphStyle(
        "PDFCaption", parent=body, fontName="LaTeXPalatino-Italic", fontSize=10, leading=13,
        alignment=TA_CENTER, firstLineIndent=0, textColor=GRAY, spaceBefore=2, spaceAfter=8,
    )
    front_title = ParagraphStyle(
        "FrontTitle", parent=h1, alignment=TA_CENTER, fontSize=17, leading=22,
        firstLineIndent=0, spaceBefore=12, spaceAfter=16,
    )
    cover_title = ParagraphStyle(
        "CoverTitle", parent=h1, alignment=TA_CENTER, fontSize=17, leading=22,
        firstLineIndent=0, spaceBefore=12, spaceAfter=12,
    )
    cover_big = ParagraphStyle(
        "CoverBig", parent=h1, alignment=TA_CENTER, fontSize=20, leading=25,
        firstLineIndent=0, spaceBefore=10, spaceAfter=12,
    )
    small = ParagraphStyle("PDFSmall", parent=body, fontName="LaTeXPalatino", fontSize=10, leading=13, firstLineIndent=0)
    index = ParagraphStyle("PDFIndex", parent=body, fontName="LaTeXPalatino", fontSize=10, leading=12,
                           alignment=TA_LEFT, firstLineIndent=0, spaceBefore=1, spaceAfter=1)
    return {"body": body, "center": centered, "h1": h1, "h2": h2, "h3": h3, "caption": caption,
            "front": front_title, "cover": cover_title, "coverbig": cover_big, "small": small, "index": index}


def para(text, style):
    text = text or ""
    text = escape(text.replace("\t", " ").replace("\r", ""))
    text = text.replace("&lt;br/&gt;", "<br/>")
    text = text.replace("\n", "<br/>")
    return Paragraph(text, style)


def image_from_paragraph(doc, p, index):
    blips = p._p.xpath('.//a:blip')
    if not blips:
        return None
    rid = blips[0].get(qn("r:embed"))
    part = doc.part.related_parts.get(rid)
    if part is None or not hasattr(part, "blob"):
        return None
    path = ASSET_DIR / f"image_{index:03d}.bin"
    path.write_bytes(part.blob)
    return path


def has_page_break(p):
    return bool(p._p.xpath('.//w:br[@w:type="page"]'))


def table_flowable(table, styles):
    rows = []
    for row in table.rows:
        vals = []
        for cell in row.cells:
            txt = cell.text.replace("\n", "<br/>")
            vals.append(Paragraph(escape(txt).replace("&lt;br/&gt;", "<br/>"), styles["small"]))
        rows.append(vals)
    if not rows:
        return Spacer(1, 0.1 * cm)
    col_count = len(rows[0])
    widths = [((A4[0] - 5 * cm) / col_count) for _ in range(col_count)]
    t = Table(rows, colWidths=widths, repeatRows=1, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "LaTeXPalatino-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "LaTeXPalatino"),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def static_front(styles, docx):
    story = []
    logo = REPORT / "images" / "onda" / "onda_logo.png"
    if logo.exists():
        im = Image(str(logo), width=3 * cm, height=3 * cm)
        story.extend([Spacer(1, 0.2 * cm), im, Spacer(1, 0.2 * cm)])
    story.append(para("OFFICE NATIONAL DES AÉROPORTS", styles["center"]))
    story.append(Spacer(1, 0.7 * cm))
    story.append(para("PROJET DE FIN D'ANNEE", styles["coverbig"]))
    story.append(para("4ème Année en Ingénierie Informatique et Réseaux", styles["center"]))
    story.append(Spacer(1, 0.8 * cm))
    story.append(para(TITLE, styles["cover"]))
    story.append(para("Rapport de projet — version technique intégrée", styles["center"]))
    story.append(Spacer(1, 0.8 * cm))
    data = [
        [para("Réalisé par", styles["small"]), para("Encadrement", styles["small"])],
        [para("Azzat Nouamane<br/>Hnid Aimane", styles["small"]),
         para("Encadrement professionnel : Mme Jaouhari Ouafaa — ONDA<br/>Encadrement pédagogique : Mme Khadija Bousmar — EMSI", styles["small"])],
    ]
    t = Table(data, colWidths=[7 * cm, 8 * cm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "LaTeXPalatino-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "LaTeXPalatino"),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([t, Spacer(1, 1.0 * cm), para("Organisme d'accueil : Office National des Aéroports (ONDA)", styles["center"]), Spacer(1, 0.25 * cm), para("Année universitaire : 2025–2026", styles["center"]), PageBreak()])
    story.append(para("Dédicace", styles["front"]))
    story.append(para("Nous dédions ce travail à nos familles, pour leur soutien constant, leur patience et la confiance qu’elles nous accordent tout au long de notre formation. Leur encouragement nous a accompagnés pendant les phases de recherche, de développement, de tests et de rédaction, parfois lorsque les difficultés techniques exigeaient davantage de temps et de persévérance.", styles["center"]))
    story.append(para("Nous dédions également ce projet à toutes les personnes qui nous ont transmis le goût de l’apprentissage et de l’innovation dans les domaines des réseaux, de la cybersécurité et de l’intelligence artificielle. À travers ce rapport, nous souhaitons valoriser le travail collectif, la responsabilité professionnelle et la volonté de construire des solutions utiles aux organisations qui dépendent de leurs systèmes d’information.", styles["center"]))
    story.append(PageBreak())
    story.append(para("Remerciements", styles["front"]))
    story.append(para("Nous remercions vivement Mme Jaouhari Ouafaa, notre encadrante au sein de l’ONDA, pour son accompagnement professionnel, sa disponibilité et les orientations qui nous ont permis de mieux comprendre les contraintes d’un réseau aéroportuaire. Ses remarques nous ont aidés à rapprocher les fonctionnalités développées des besoins concrets d’une équipe chargée de la continuité de service.", styles["body"]))
    story.append(para("Nous remercions également Mme Khadija Bousmar, notre encadrante pédagogique à l’EMSI, pour ses conseils méthodologiques, son suivi régulier et son attention portée à la qualité de la présentation. Nous lui sommes reconnaissants de nous avoir encouragés à structurer le travail selon une démarche claire, à justifier nos choix techniques et à exposer les limites de la solution avec honnêteté.", styles["body"]))
    story.append(para("Enfin, nous remercions les équipes de l’ONDA, nos enseignants et toutes les personnes qui ont contribué, directement ou indirectement, à rendre cette expérience formatrice. Les échanges, les lectures, les essais et les corrections successives ont enrichi notre compréhension de la maintenance informatique et de la cybersécurité. Ce projet est le résultat d’un effort de collaboration et de transmission.", styles["body"]))
    story.append(PageBreak())
    story.append(para("Résumé", styles["front"]))
    story.append(para("Ce projet porte sur la conception d’un modèle d’analyse des risques et d’alertes prédictives basé sur les données de maintenance des actifs informatiques de l’Office National des Aéroports. La solution exploite l’historique des incidents WAN de 27 sites pour estimer un score de risque sur un horizon de 30 jours, hiérarchiser les alertes et proposer des actions de prévention. L’objectif n’est pas de remplacer l’expertise des équipes, mais de leur fournir une information préparée, comparable et exploitable au moment de décider d’une intervention.", styles["body"]))
    story.append(para("La plateforme associe un portail exécutif, un module de diagnostic du modèle, une gestion du facteur humain et un plan d’intervention préventive. Elle permet de passer d’une lecture dispersée des tickets à une vision structurée : les incidents sont agrégés, les tendances sont rendues visibles, les sites sont classés et les recommandations sont rattachées à des causes ou à des situations observées. Les résultats peuvent ainsi être discutés avec les responsables réseau et adaptés aux contraintes opérationnelles.", styles["body"]))
    story.append(para("Un CyberRange isolé complète la validation en reproduisant un scénario d’incident de sécurité autorisé, depuis l’observation jusqu’à la détection et la remédiation. Cet environnement ne représente pas le réseau de production ; il sert à vérifier la capacité à collecter des preuves, à écrire des contrôles défensifs et à transformer les enseignements techniques en retour d’expérience. Cette intégration relie la continuité de service, la gouvernance de la maintenance et la préparation à la réponse aux incidents.", styles["body"]))
    story.append(para("Mots-clés : analyse de risques, maintenance informatique, réseau WAN, apprentissage automatique, alertes prédictives, CyberRange, détection, REX.", styles["body"]))
    story.append(PageBreak())
    story.append(para("Abstract", styles["front"]))
    story.append(para("This project addresses the design of a risk analysis and predictive alerting model based on IT asset maintenance data for Morocco’s National Airports Authority. The solution uses the incident history of 27 WAN sites to estimate a 30-day risk score, prioritize alerts and recommend preventive actions. It is designed as a decision-support system: the prediction highlights where attention should be focused, while operational teams retain responsibility for confirming the context and selecting the appropriate intervention.", styles["body"]))
    story.append(para("The platform combines an executive portal, model diagnostics, human-factor controls and a preventive intervention plan. It organizes incident records into comparable indicators, makes the main risk drivers visible and links the result to concrete maintenance actions. An isolated CyberRange complements the validation by reproducing an authorized security-incident scenario, from observation to detection and remediation. The integrated approach connects service continuity, maintenance governance and incident-response readiness while keeping the production network outside the simulation perimeter.", styles["body"]))
    story.append(para("Keywords: risk analysis, IT maintenance, WAN, machine learning, predictive alerts, CyberRange, detection, lessons learned.", styles["body"]))
    story.append(PageBreak())
    story.append(para("Table des matières", styles["front"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOCLevel0", fontName="LaTeXPalatino-Bold", fontSize=12, leftIndent=0, firstLineIndent=0, leading=17, spaceBefore=5),
        ParagraphStyle(name="TOCLevel1", fontName="LaTeXPalatino", fontSize=11, leftIndent=0.6 * cm, firstLineIndent=0, leading=15),
        ParagraphStyle(name="TOCLevel2", fontName="LaTeXPalatino", fontSize=10, leftIndent=1.2 * cm, firstLineIndent=0, leading=14),
    ]
    story.append(toc)
    story.append(PageBreak())
    story.append(para("Liste des figures", styles["front"]))
    figures = [
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
    for f in figures:
        story.append(para("• " + f, styles["index"]))
    story.append(PageBreak())
    story.append(para("Liste des tableaux", styles["front"]))
    tables = [
        "Tableau 1. Planification synthétique du projet.", "Tableau 2. Acteurs et responsabilités.",
        "Tableau 3. Exigences non fonctionnelles.", "Tableau 4. Dictionnaire synthétique des données.",
        "Tableau 5. Environnement de réalisation.", "Tableau 6. Paramètres de l’évaluation temporelle.",
        "Tableau 7. Matrice de confusion du modèle.", "Tableau 8. Récapitulatif des indicateurs.",
    ]
    for t in tables:
        story.append(para("• " + t, styles["body"]))
    return story


def main_story(styles, docx):
    story = [NextPageTemplate("main"), PageBreak()]
    image_idx = 1
    started = False
    for child in docx.element.body.iterchildren():
        if child.tag == qn("w:p"):
            p = DocxParagraph(child, docx)
            text = p.text.strip()
            if text == "Introduction générale":
                started = True
            if not started:
                continue
            if has_page_break(p):
                story.append(PageBreak())
            if not text:
                img_path = image_from_paragraph(docx, p, image_idx)
                if img_path:
                    image_idx += 1
                    story.append(Spacer(1, 0.15 * cm))
                    try:
                        from PIL import Image as PILImage
                        with PILImage.open(io.BytesIO(img_path.read_bytes())) as pil:
                            w, h = pil.size
                        max_w, max_h = 15.2 * cm, 19 * cm
                        scale = min(max_w / w, max_h / h)
                        story.append(Image(str(img_path), width=w * scale, height=h * scale))
                    except Exception:
                        story.append(Image(str(img_path), width=14 * cm, height=7 * cm))
                continue
            if p.style.name.startswith("Heading"):
                level = int(re.search(r"(\d+)$", p.style.name).group(1))
                story.append(Paragraph(escape(text), styles[f"h{level}"]))
            elif p.style.name == "Caption":
                img_path = image_from_paragraph(docx, p, image_idx)
                if img_path:
                    image_idx += 1
                    story.append(Image(str(img_path), width=14 * cm, height=7 * cm))
                story.append(Paragraph(escape(text), styles["caption"]))
            elif p.style.name in ("List Paragraph", "List Paragraph 2"):
                story.append(para(text, styles["body"]))
            else:
                # Most image paragraphs contain no text; image extraction is handled here too.
                img_path = image_from_paragraph(docx, p, image_idx)
                if img_path:
                    image_idx += 1
                    try:
                        from PIL import Image as PILImage
                        with PILImage.open(io.BytesIO(img_path.read_bytes())) as pil:
                            w, h = pil.size
                        max_w, max_h = 15.2 * cm, 19 * cm
                        scale = min(max_w / w, max_h / h)
                        story.append(Image(str(img_path), width=w * scale, height=h * scale))
                    except Exception:
                        story.append(Image(str(img_path), width=14 * cm, height=7 * cm))
                if text and not text.startswith("La table des matières est générée"):
                    story.append(para(text, styles["body"]))
        elif child.tag == qn("w:tbl") and started:
            table = DocxTable(child, docx)
            story.append(table_flowable(table, styles))
            story.append(Spacer(1, 0.12 * cm))
    return story


def build():
    docx = Document(str(DOCX))
    styles = make_styles()
    story = static_front(styles, docx)
    story.extend(main_story(styles, docx))
    pdf = ReportDocTemplate(str(OUT), pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm, topMargin=2.5 * cm, bottomMargin=2.5 * cm, title=TITLE, author="Azzat Nouamane et Hnid Aimane")
    pdf.multiBuild(story)
    print(OUT)


if __name__ == "__main__":
    build()
