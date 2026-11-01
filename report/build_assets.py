from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "images" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#0B2A50"
BLUE = "#2D7EDB"
CYAN = "#0EA5E9"
GREEN = "#159A68"
ORANGE = "#E79A14"
RED = "#D94A4A"
PURPLE = "#7651B9"
GRAY = "#566879"
LIGHT = "#F4F7FB"
GRID = "#CAD6E3"

FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    for candidate in [FONT_DIR / name, FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


REG = lambda s: font("segoeui.ttf", s)
BOLD = lambda s: font("segoeuib.ttf", s)


def text_center(draw, box, value, f, fill=NAVY, spacing=4):
    x1, y1, x2, y2 = box
    lines = []
    for raw in str(value).split("\n"):
        words = raw.split()
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if draw.textbbox((0, 0), trial, font=f)[2] <= (x2 - x1 - 26):
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    heights = [draw.textbbox((0, 0), line, font=f)[3] for line in lines]
    total = sum(heights) + spacing * max(0, len(lines) - 1)
    y = y1 + max(8, (y2 - y1 - total) / 2)
    for line, h in zip(lines, heights):
        width = draw.textbbox((0, 0), line, font=f)[2]
        draw.text((x1 + (x2 - x1 - width) / 2, y), line, font=f, fill=fill)
        y += h + spacing


def title(draw, value, subtitle=None):
    draw.text((70, 42), value, font=BOLD(42), fill=NAVY)
    if subtitle:
        draw.text((72, 100), subtitle, font=REG(24), fill=GRAY)


def arrow(draw, start, end, fill=NAVY, width=5):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            pts = [(x2, y2), (x2 - 18, y2 - 10), (x2 - 18, y2 + 10)]
        else:
            pts = [(x2, y2), (x2 + 18, y2 - 10), (x2 + 18, y2 + 10)]
    else:
        if y2 >= y1:
            pts = [(x2, y2), (x2 - 10, y2 - 18), (x2 + 10, y2 - 18)]
        else:
            pts = [(x2, y2), (x2 - 10, y2 + 18), (x2 + 10, y2 + 18)]
    draw.polygon(pts, fill=fill)


def rounded(draw, box, outline=BLUE, fill="#FFFFFF", radius=22, width=5):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def save(img, name):
    img.save(OUT / name, "PNG", optimize=True)


def make_usecase():
    img = Image.new("RGB", (1800, 1050), "white")
    d = ImageDraw.Draw(img)
    title(d, "Diagramme global des cas d'utilisation", "Acteurs et fonctions de la plateforme fusionnée ONDA / CyberRange")
    rounded(d, (335, 150, 1465, 945), outline=NAVY, width=5)
    d.text((640, 168), "Plateforme de résilience réseau", font=BOLD(28), fill=NAVY)
    actors = [(170, 320, "DSI /\nDirecteur"), (170, 640, "Ingénieur\nréseau"), (1630, 320, "Responsable\nmaintenance"), (1630, 640, "Analyste\nsécurité")]
    for x, y, label in actors:
        d.ellipse((x - 18, y - 70, x + 18, y - 34), outline=NAVY, width=4)
        d.line((x, y - 34, x, y + 35), fill=NAVY, width=4)
        d.line((x - 35, y - 5, x + 35, y - 5), fill=NAVY, width=4)
        d.line((x, y + 35, x - 27, y + 75), fill=NAVY, width=4)
        d.line((x, y + 35, x + 27, y + 75), fill=NAVY, width=4)
        text_center(d, (x - 105, y + 85, x + 105, y + 145), label, BOLD(22), NAVY)
    cases = [
        ((520, 245, 870, 330), "Consulter le\nportail exécutif", CYAN),
        ((930, 245, 1280, 330), "Consulter les\nalertes et scores", RED),
        ((520, 390, 870, 475), "Explorer l'historique\nd'un site", BLUE),
        ((930, 390, 1280, 475), "Enregistrer une\naction de mitigation", GREEN),
        ((520, 535, 870, 620), "Valider la check-list\nd'intervention", GREEN),
        ((930, 535, 1280, 620), "Analyser causes et\nopérateurs", ORANGE),
        ((520, 680, 870, 765), "Simuler un scénario\ndans le CyberRange", PURPLE),
        ((930, 680, 1280, 765), "Détecter et produire\ndes IOC", NAVY),
        ((720, 825, 1080, 910), "Capitaliser le\nretour d'expérience", GREEN),
    ]
    for box, label, color in cases:
        d.ellipse(box, outline=color, fill=LIGHT, width=4)
        text_center(d, box, label, BOLD(21), NAVY)
    links = [((205, 350), (520, 290)), ((205, 350), (930, 290)), ((205, 670), (520, 435)), ((205, 670), (930, 435)), ((1595, 350), (520, 575)), ((1595, 350), (930, 575)), ((1595, 670), (520, 720)), ((1595, 670), (930, 720)), ((805, 765), (805, 825)), ((1100, 765), (1000, 825))]
    for a, b in links:
        arrow(d, a, b, fill=GRID, width=3)
    save(img, "usecase_global.png")


def make_pipeline():
    img = Image.new("RGB", (1800, 1000), "white")
    d = ImageDraw.Draw(img)
    title(d, "Architecture logique de la solution", "De la donnée de maintenance à la décision et au retour d'expérience")
    blocks = [
        ((90, 220, 390, 420), "Sources\nExcel incidents\nTickets / REX", BLUE),
        ((500, 220, 800, 420), "Préparation\nNettoyage\nNormalisation\nClassification", CYAN),
        ((910, 220, 1210, 420), "Dataset\nSite-semaine\nFenêtres temporelles\nCible 30 jours", PURPLE),
        ((1320, 220, 1710, 420), "Modèle IA\nRégression logistique\nProbabilité\nScore 0–100", GREEN),
        ((320, 600, 650, 800), "Décision\nAlertes et\nclassement", RED),
        ((760, 600, 1090, 800), "Prévention\nOpérateur\nCause / impact", ORANGE),
        ((1200, 600, 1530, 800), "CyberRange\nIOC, YARA, Snort\nValidation contrôlée", NAVY),
    ]
    for box, label, color in blocks:
        rounded(d, box, outline=color, fill="#F7FAFD", radius=24, width=6)
        text_center(d, box, label, BOLD(27), NAVY)
    for a, b in [((390, 320), (500, 320)), ((800, 320), (910, 320)), ((1210, 320), (1320, 320)), ((1520, 420), (650, 600)), ((1055, 420), (925, 600)), ((1325, 420), (1365, 600))]:
        arrow(d, a, b, fill=GRAY, width=5)
    d.rounded_rectangle((180, 875, 1620, 940), radius=18, fill="#EAF5FF", outline=CYAN, width=3)
    text_center(d, (180, 875, 1620, 940), "Boucle de résilience : prédire → simuler → détecter → répondre → prévenir → apprendre", BOLD(27), NAVY)
    save(img, "solution_pipeline.png")


def make_deployment():
    img = Image.new("RGB", (1800, 1000), "white")
    d = ImageDraw.Draw(img)
    title(d, "Architecture de déploiement", "Séparation entre l'application de pilotage et le laboratoire d'expérimentation")
    rounded(d, (70, 180, 1030, 900), outline=BLUE, fill="#F7FBFF", radius=28, width=6)
    d.text((115, 210), "Environnement ONDA / application", font=BOLD(30), fill=NAVY)
    nodes = [((140, 330, 430, 515), "Poste DSI\nNavigateur", CYAN), ((530, 330, 940, 515), "Application Streamlit\nModules de pilotage", BLUE), ((330, 650, 750, 825), "Données et artefacts\nExcel · CSV · modèle", GREEN)]
    for box, label, color in nodes:
        rounded(d, box, outline=color, fill="white", radius=22, width=5)
        text_center(d, box, label, BOLD(25), NAVY)
    arrow(d, (430, 420), (530, 420), GRAY, 5); arrow(d, (735, 515), (545, 650), GRAY, 5); arrow(d, (545, 650), (650, 515), GREEN, 5)
    rounded(d, (1110, 180, 1730, 900), outline=PURPLE, fill="#FCFAFF", radius=28, width=6)
    d.text((1150, 210), "CyberRange isolé", font=BOLD(30), fill=NAVY)
    vms = [((1170, 340, 1640, 500), "Kali Linux 2024\n192.168.243.129\nAnalyseur / attaquant", BLUE), ((1170, 610, 1640, 770), "Metasploitable 2\n192.168.243.128\nCible de test", GREEN)]
    for box, label, color in vms:
        rounded(d, box, outline=color, fill="white", radius=22, width=5)
        text_center(d, box, label, BOLD(24), NAVY)
    arrow(d, (1405, 500), (1405, 610), RED, 6)
    d.rounded_rectangle((1180, 815, 1630, 865), radius=14, fill="#EAF5FF", outline=NAVY, width=3)
    text_center(d, (1180, 815, 1630, 865), "VirtualBox · Host-Only · sans Internet", BOLD(20), NAVY)
    d.line((1030, 540, 1110, 540), fill=RED, width=5)
    d.text((1022, 480), "aucun flux\nproduction → lab", font=BOLD(20), fill=RED, anchor="ra")
    save(img, "deployment_architecture.png")


def make_sequence():
    img = Image.new("RGB", (1800, 1050), "white")
    d = ImageDraw.Draw(img)
    title(d, "Diagramme de séquence : traitement d'une alerte", "Scénario nominal de consultation, qualification et action")
    participants = [(180, "Ingénieur"), (520, "Interface"), (890, "Modèle"), (1260, "Prévention"), (1600, "Journal / REX")]
    for x, name in participants:
        d.rounded_rectangle((x - 100, 160, x + 100, 225), radius=12, fill="#EAF5FF", outline=NAVY, width=3)
        text_center(d, (x - 100, 160, x + 100, 225), name, BOLD(22), NAVY)
        d.line((x, 225, x, 940), fill="#9AAABB", width=3)
    events = [(280, 180, 520, "Demander les alertes"), (360, 520, 890, "Charger les scores"), (440, 890, 1260, "Retourner score + raisons"), (535, 1260, 520, "Afficher plan prioritaire"), (640, 180, 520, "Consulter la fiche site"), (725, 520, 1600, "Enregistrer action / ticket"), (815, 1600, 520, "Confirmer la traçabilité"), (900, 520, 180, "Présenter décision")]
    for y, x1, x2, label in events:
        arrow(d, (x1, y), (x2, y), fill=BLUE if x1 < x2 else GREEN, width=4)
        middle = (x1 + x2) / 2
        d.rounded_rectangle((middle - 115, y - 28, middle + 115, y + 28), radius=10, fill="white", outline=GRID, width=2)
        text_center(d, (middle - 115, y - 28, middle + 115, y + 28), label, REG(17), NAVY)
    d.rounded_rectangle((80, 970, 1720, 1015), radius=12, fill="#EDFCF6", outline=GREEN, width=2)
    text_center(d, (80, 970, 1720, 1015), "La validation humaine reste obligatoire avant toute action terrain ou changement de production.", BOLD(21), NAVY)
    save(img, "sequence_alert.png")


def make_data_model():
    img = Image.new("RGB", (1800, 1050), "white")
    d = ImageDraw.Draw(img)
    title(d, "Modèle de données conceptuel", "Entités minimales pour relier incidents, sites, scores et actions")
    boxes = [((100, 250, 530, 710), "SITE\n\nsite_code\nsite_name\ncriticité\nlocalisation", BLUE), ((685, 180, 1115, 680), "INCIDENT\n\nticket_number\ndate_incident\nduration\ncategory\noperator\nincident_type", RED), ((1270, 250, 1700, 710), "SCORE_RISQUE\n\nreference_date\nrisk_probability\nrisk_score\nrisk_level\nrisk_reasons", GREEN), ((400, 800, 820, 990), "ACTION_MITIGATION\n\nsite\naction\nstatus\noperator\ndate", ORANGE), ((990, 800, 1410, 990), "REX\n\nsite\ntype\ndescription\nimpact\nmesures", PURPLE)]
    for box, label, color in boxes:
        rounded(d, box, outline=color, fill="#F8FBFE", radius=20, width=5)
        text_center(d, box, label, BOLD(24), NAVY)
    for a, b, lab in [((530, 380), (685, 380), "1 — N"), ((1115, 380), (1270, 380), "1 — N"), ((420, 710), (560, 800), "1 — N"), ((1380, 710), (1260, 800), "1 — N")]:
        arrow(d, a, b, GRAY, 4)
        x = (a[0] + b[0]) / 2; y = (a[1] + b[1]) / 2 - 26
        d.text((x, y), lab, font=BOLD(19), fill=GRAY, anchor="mm")
    save(img, "data_model.png")


if __name__ == "__main__":
    make_usecase()
    make_pipeline()
    make_deployment()
    make_sequence()
    make_data_model()
    print("generated", OUT)
