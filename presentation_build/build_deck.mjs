import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde";
const OUT = path.join(ROOT, "report", "ONDA_Risk_Intelligence_CyberRange_Defense.pptx");
const BUILD = path.join(ROOT, "presentation_build");
const IMG = (sub, name) => path.join(ROOT, "report", "images", sub, name);

const C = {
  bg: "#07111E",
  panel: "#0D1B30",
  panel2: "#102640",
  panel3: "#132E4D",
  text: "#F5F8FC",
  muted: "#A9BCD4",
  blue: "#36B8FF",
  light: "#83DCFF",
  teal: "#25C8A4",
  orange: "#FFB22E",
  red: "#FF5D6C",
  purple: "#A98BFA",
  line: "#24425F",
  white: "#FFFFFF",
};

const pres = Presentation.create({ slideSize: { width: 1280, height: 720 } });

async function blob(file) {
  const b = await fs.readFile(file);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
}

function shape(slide, geometry, x, y, w, h, fill = "none", lineFill = "none", lineWidth = 0) {
  return slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
  });
}

function rect(slide, x, y, w, h, fill, radius = true, lineFill = "none", lineWidth = 0) {
  return shape(slide, radius ? "roundRect" : "rect", x, y, w, h, fill, lineFill, lineWidth);
}

function text(slide, value, x, y, w, h, opts = {}) {
  const s = shape(slide, "textbox", x, y, w, h, "none", "none", 0);
  s.text = value;
  s.text.style = {
    fontFamily: opts.fontFamily || "Aptos",
    fontSize: opts.fontSize || 20,
    bold: opts.bold || false,
    italic: opts.italic || false,
    color: opts.color || C.text,
    alignment: opts.alignment || "left",
    verticalAlignment: opts.verticalAlignment || "middle",
  };
  return s;
}

async function image(slide, file, x, y, w, h, fit = "contain", alt = "Project image") {
  slide.images.add({
    blob: await blob(file),
    contentType: "image/png",
    alt,
    fit,
    position: { left: x, top: y, width: w, height: h },
  });
}

function line(slide, x, y, w, color = C.line, height = 2) {
  return rect(slide, x, y, w, height, color, false);
}

function pill(slide, label, x, y, w, color = C.blue) {
  rect(slide, x, y, w, 30, C.panel2, true, color, 1);
  text(slide, label, x + 10, y + 2, w - 20, 26, { fontSize: 14, bold: true, color });
}

function addFooter(slide, n) {
  line(slide, 46, 681, 1188, C.line, 1);
  text(slide, "ONDA · Risk Intelligence & CyberRange", 48, 687, 500, 22, { fontSize: 12, color: C.muted });
  text(slide, String(n).padStart(2, "0"), 1180, 687, 52, 22, { fontSize: 12, color: C.muted, alignment: "right" });
}

function addHeader(slide, kicker, title, n) {
  text(slide, kicker.toUpperCase(), 48, 30, 620, 24, { fontSize: 13, bold: true, color: C.blue });
  text(slide, title, 48, 56, 1140, 54, { fontSize: 38, bold: true, color: C.text });
  line(slide, 48, 121, 1184, C.blue, 2);
  addFooter(slide, n);
}

function bulletList(slide, items, x, y, w, lineH = 36, color = C.text, bulletColor = C.blue, fontSize = 21) {
  items.forEach((item, i) => {
    const yy = y + i * lineH;
    text(slide, "•", x, yy, 22, lineH, { fontSize: fontSize + 3, bold: true, color: bulletColor });
    text(slide, item, x + 28, yy, w - 28, lineH, { fontSize, color });
  });
}

function metric(slide, x, y, w, value, label, color = C.blue) {
  rect(slide, x, y, w, 102, C.panel, true, C.line, 1);
  text(slide, value, x + 18, y + 12, w - 36, 44, { fontSize: 34, bold: true, color });
  text(slide, label.toUpperCase(), x + 18, y + 62, w - 36, 26, { fontSize: 12, bold: true, color: C.muted });
}

function note(slide, lines) {
  slide.speakerNotes.textFrame.setText(`[Sources]\n- ${lines.join("\n- ")}`);
  slide.speakerNotes.setVisible(true);
}

async function slideCover() {
  const s = pres.slides.add();
  s.background.fill = C.bg;
  rect(s, 0, 0, 1280, 720, C.bg, false);
  rect(s, 0, 0, 18, 720, C.blue, false);
  rect(s, 18, 0, 1262, 12, C.teal, false);
  await image(s, IMG("onda", "onda_logo.png"), 58, 54, 150, 75, "contain", "ONDA logo");
  await image(s, IMG("cyberrange", "emsi_logo.png"), 1075, 48, 145, 85, "contain", "EMSI logo");
  pill(s, "PROJET DE FIN D'ANNÉE · 4IIR", 58, 185, 252, C.teal);
  text(s, "Conception d’un modèle\nd’analyse des risques\net d’alertes prédictives", 58, 235, 750, 190, { fontSize: 50, bold: true, color: C.text });
  text(s, "basé sur les données de maintenance des actifs informatiques", 62, 437, 710, 40, { fontSize: 22, color: C.light });
  line(s, 62, 505, 620, C.blue, 3);
  text(s, "Une plateforme intégrée pour anticiper les risques WAN,\nréduire l’erreur humaine et valider la détection en environnement contrôlé.", 62, 526, 700, 62, { fontSize: 20, color: C.muted });
  rect(s, 890, 212, 284, 296, C.panel, true, C.line, 1);
  text(s, "ÉQUIPE", 920, 238, 220, 24, { fontSize: 14, bold: true, color: C.blue });
  text(s, "Azzat Nouamane\nHnid Aimane", 920, 272, 220, 72, { fontSize: 26, bold: true, color: C.text });
  line(s, 920, 365, 214, C.line, 1);
  text(s, "Encadrement professionnel\nMme Jaouhari Ouafaa · ONDA", 920, 383, 230, 42, { fontSize: 15, color: C.muted });
  text(s, "Encadrement pédagogique\nMme Khadija Bousmar · EMSI", 920, 438, 230, 42, { fontSize: 15, color: C.muted });
  text(s, "ONDA · Office National des Aéroports", 62, 662, 550, 24, { fontSize: 14, color: C.muted });
  text(s, "Soutenance · 2026", 1060, 662, 160, 24, { fontSize: 14, color: C.muted, alignment: "right" });
  note(s, ["Local project report: report/main.tex", "Local assets: report/images/onda/onda_logo.png and report/images/cyberrange/emsi_logo.png"]);
}

async function slideStakes() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "01 · Contexte", "Pourquoi la continuité réseau est stratégique", 2);
  text(s, "Dans un aéroport, le WAN relie les services qui rendent l’exploitation possible. Une coupure n’est donc pas un simple incident IT : elle devient rapidement un risque opérationnel.", 52, 150, 650, 78, { fontSize: 24, color: C.muted });
  const cards = [
    ["Opérations passagers", "Enregistrement, embarquement et échanges avec les systèmes métiers.", C.blue],
    ["Sûreté & supervision", "Vidéosurveillance, contrôle d’accès et coordination des équipes.", C.teal],
    ["Bagages & logistique", "Traçabilité, tri et circulation des informations entre sites.", C.orange],
    ["Communication", "Messagerie, support et coordination avec la direction réseau.", C.purple],
  ];
  cards.forEach((c, i) => {
    const x = 52 + (i % 2) * 326, y = 262 + Math.floor(i / 2) * 140;
    rect(s, x, y, 300, 110, C.panel, true, C.line, 1);
    rect(s, x, y, 8, 110, c[2], false);
    text(s, c[0], x + 24, y + 15, 250, 30, { fontSize: 21, bold: true, color: C.text });
    text(s, c[1], x + 24, y + 51, 252, 48, { fontSize: 16, color: C.muted });
  });
  await image(s, IMG("onda", "onda_home.png"), 760, 153, 462, 405, "contain", "ONDA Risk Intelligence executive portal");
  pill(s, "27 sites aéroportuaires · 864 incidents historiques", 764, 584, 422, C.blue);
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_home.png"]);
}

async function slideObjective() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "02 · Problématique", "Passer d’une réaction après incident à une prévention ciblée", 3);
  rect(s, 55, 169, 455, 330, C.panel, true, C.red, 1);
  text(s, "APPROCHE RÉACTIVE", 88, 200, 360, 28, { fontSize: 16, bold: true, color: C.red });
  text(s, "Incident", 88, 254, 150, 42, { fontSize: 30, bold: true, color: C.text });
  text(s, "→ Ticket\n→ Diagnostic\n→ Intervention\n→ Retour à la normale", 88, 310, 280, 145, { fontSize: 23, color: C.muted });
  rect(s, 585, 275, 108, 82, C.blue, true);
  text(s, "→", 585, 274, 108, 82, { fontSize: 48, bold: true, color: C.bg, alignment: "center" });
  rect(s, 770, 169, 455, 330, C.panel, true, C.teal, 1);
  text(s, "APPROCHE PROACTIVE", 803, 200, 360, 28, { fontSize: 16, bold: true, color: C.teal });
  text(s, "Risque", 803, 254, 150, 42, { fontSize: 30, bold: true, color: C.text });
  text(s, "→ Score 0–100\n→ Alerte priorisée\n→ Action préventive\n→ Validation par simulation", 803, 310, 330, 145, { fontSize: 23, color: C.muted });
  metric(s, 55, 545, 260, "864", "incidents analysés", C.blue);
  metric(s, 335, 545, 260, "27", "sites WAN", C.teal);
  metric(s, 615, 545, 260, "30 j", "horizon de prévision", C.orange);
  metric(s, 895, 545, 330, "0–100", "score de risque", C.purple);
  note(s, ["Local project report: report/main.tex", "Project metrics: 864 incidents, 27 sites, 30-day forecast horizon, 0–100 risk score"]);
}

async function slideSolution() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "03 · Vision intégrée", "Une chaîne de décision, de la donnée à l’action", 4);
  await image(s, IMG("diagrams", "solution_pipeline.png"), 70, 155, 720, 440, "contain", "Integrated solution pipeline");
  text(s, "Le projet ne juxtapose pas deux applications. Il relie la prédiction du risque, la prévention des erreurs humaines et la simulation défensive dans un même cycle d’amélioration.", 830, 174, 355, 115, { fontSize: 22, color: C.muted });
  const steps = [
    ["1", "Prédire", "Calculer un risque site à 30 jours", C.blue],
    ["2", "Préparer", "Appliquer les contrôles et le REX", C.teal],
    ["3", "Simuler", "Reproduire un scénario autorisé", C.orange],
    ["4", "Détecter", "Observer les traces et les alertes", C.red],
    ["5", "Capitaliser", "Transformer l’expérience en action", C.purple],
  ];
  steps.forEach((st, i) => {
    const y = 320 + i * 60;
    rect(s, 830, y, 34, 34, st[3], true);
    text(s, st[0], 830, y + 1, 34, 32, { fontSize: 17, bold: true, color: C.bg, alignment: "center" });
    text(s, st[1], 880, y - 2, 120, 26, { fontSize: 19, bold: true, color: C.text });
    text(s, st[2], 1004, y - 2, 210, 36, { fontSize: 15, color: C.muted });
  });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/diagrams/solution_pipeline.png"]);
}

async function slideDataModel() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "04 · Méthode", "Transformer l’historique de maintenance en signal prédictif", 5);
  const cols = [
    ["DONNÉES", "Historique des tickets WAN\nDurée d’indisponibilité\nCatégorie et opérateur\nDate et site", C.blue],
    ["INDICATEURS", "Récence des incidents\nFréquence 30 / 90 jours\nImpact cumulé\nSaisonnalité", C.teal],
    ["MODÈLE", "Apprentissage temporel\nClassification du risque\nScore 0–100\nAlerte priorisée", C.orange],
    ["DÉCISION", "Top sites critiques\nAction recommandée\nContrôle humain\nSuivi de mitigation", C.purple],
  ];
  cols.forEach((c, i) => {
    const x = 45 + i * 304;
    rect(s, x, 185, 270, 270, C.panel, true, c[2], 1);
    rect(s, x, 185, 270, 8, c[2], false);
    text(s, c[0], x + 22, 216, 230, 28, { fontSize: 16, bold: true, color: c[2] });
    text(s, c[1], x + 22, 264, 224, 145, { fontSize: 21, color: C.text });
  });
  text(s, "Séparation temporelle", 68, 515, 245, 28, { fontSize: 18, bold: true, color: C.light });
  text(s, "Entraînement : 2021–2023", 68, 552, 245, 28, { fontSize: 19, color: C.muted });
  text(s, "Validation : 2024", 68, 584, 245, 28, { fontSize: 19, color: C.muted });
  line(s, 335, 570, 620, C.line, 7);
  rect(s, 345, 552, 390, 42, C.blue, true); text(s, "historique utilisé pour apprendre", 360, 557, 360, 30, { fontSize: 14, bold: true, color: C.bg, alignment: "center" });
  rect(s, 745, 552, 200, 42, C.orange, true); text(s, "test temporel", 755, 557, 180, 30, { fontSize: 14, bold: true, color: C.bg, alignment: "center" });
  text(s, "La méthode vise une aide à la décision : le score indique où vérifier en priorité, il ne remplace pas l’expertise des équipes réseau.", 970, 536, 255, 72, { fontSize: 16, color: C.muted });
  note(s, ["Local project report: report/main.tex", "Methodology and temporal train/test split from the project report"]);
}

async function slideUseCases() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "05 · Utilisateurs", "Quatre familles de cas d’utilisation complémentaires", 6);
  await image(s, IMG("diagrams", "usecase_global.png"), 55, 160, 725, 440, "contain", "Global use-case diagram");
  const items = [
    ["DSI / direction réseau", "Piloter le risque global et arbitrer les priorités."],
    ["Ingénieur réseau", "Analyser un site, vérifier l’historique et tracer la mitigation."],
    ["Équipe opérationnelle", "Préparer une intervention avec une checklist de conformité."],
    ["Analyste sécurité", "Observer un scénario CyberRange et relier preuve et défense."],
  ];
  items.forEach((it, i) => {
    const y = 180 + i * 94;
    rect(s, 830, y, 360, 68, C.panel, true, C.line, 1);
    text(s, it[0], 854, y + 10, 310, 23, { fontSize: 18, bold: true, color: C.text });
    text(s, it[1], 854, y + 36, 310, 26, { fontSize: 14, color: C.muted });
  });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/diagrams/usecase_global.png"]);
}

async function slideArchitecture() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "06 · Architecture", "Une architecture orientée données, avec un laboratoire isolé", 7);
  await image(s, IMG("diagrams", "deployment_architecture.png"), 54, 159, 650, 440, "contain", "Deployment architecture");
  rect(s, 755, 160, 458, 138, C.panel, true, C.blue, 1);
  text(s, "Plateforme ONDA", 785, 180, 380, 28, { fontSize: 22, bold: true, color: C.blue });
  text(s, "Dashboards · scoring · alertes · REX\nAccès réservé aux utilisateurs autorisés", 785, 224, 360, 54, { fontSize: 18, color: C.muted });
  rect(s, 755, 326, 458, 138, C.panel, true, C.orange, 1);
  text(s, "CyberRange", 785, 346, 380, 28, { fontSize: 22, bold: true, color: C.orange });
  text(s, "Réseau Host-Only · scénario contrôlé\nSimulation séparée du réseau de production", 785, 390, 370, 54, { fontSize: 18, color: C.muted });
  rect(s, 755, 492, 458, 105, C.panel2, true, C.teal, 1);
  text(s, "Principe de sécurité", 785, 508, 370, 25, { fontSize: 18, bold: true, color: C.teal });
  text(s, "Tester, observer et documenter sans exposer l’infrastructure réelle.", 785, 544, 372, 35, { fontSize: 17, color: C.text });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/diagrams/deployment_architecture.png"]);
}

async function slideModules() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "07 · Produit", "Trois modules réunis dans une même expérience", 8);
  await image(s, IMG("onda", "onda_modules.png"), 50, 156, 1180, 330, "contain", "ONDA platform modules");
  const mods = [
    ["IA · Machine Learning", "Prédire et classer le risque WAN", C.blue],
    ["REX · Opérationnel", "Standardiser les interventions", C.teal],
    ["Prévention · Analyse", "Prioriser les actions sur 30 jours", C.orange],
  ];
  mods.forEach((m, i) => {
    const x = 68 + i * 390;
    rect(s, x, 522, 350, 90, C.panel, true, m[2], 1);
    text(s, m[0], x + 20, 536, 310, 25, { fontSize: 18, bold: true, color: m[2] });
    text(s, m[1], x + 20, 570, 310, 25, { fontSize: 16, color: C.muted });
  });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_modules.png"]);
}

async function slideExecutive() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "08 · Pilotage", "Le portail exécutif rend la priorité visible immédiatement", 9);
  await image(s, IMG("onda", "onda_overview.png"), 52, 154, 810, 468, "contain", "Risk overview dashboard");
  rect(s, 900, 174, 300, 96, C.panel, true, C.blue, 1);
  text(s, "Vue réseau", 925, 190, 240, 24, { fontSize: 21, bold: true, color: C.blue });
  text(s, "Distribution du risque sur l’ensemble des sites.", 925, 226, 245, 34, { fontSize: 16, color: C.muted });
  rect(s, 900, 300, 300, 96, C.panel, true, C.red, 1);
  text(s, "Top 5 critiques", 925, 316, 240, 24, { fontSize: 21, bold: true, color: C.red });
  text(s, "Ouarzazate, Zagora, Bens-Slimane, Bouarfa et Guelmim.", 925, 352, 245, 34, { fontSize: 16, color: C.muted });
  rect(s, 900, 426, 300, 135, C.panel, true, C.orange, 1);
  text(s, "Décision", 925, 442, 240, 24, { fontSize: 21, bold: true, color: C.orange });
  text(s, "La direction identifie d’abord où concentrer l’analyse et les moyens préventifs.", 925, 480, 245, 60, { fontSize: 17, color: C.muted });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_overview.png"]);
}

async function slideRiskAnalysis() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "09 · Analyse du risque", "Du signal global à la fiche d’un site", 10);
  await image(s, IMG("onda", "onda_alerts.png"), 48, 160, 565, 430, "contain", "Active risk alerts");
  await image(s, IMG("onda", "onda_detail.png"), 650, 160, 568, 250, "contain", "Detailed site risk sheet");
  rect(s, 666, 438, 532, 136, C.panel, true, C.line, 1);
  text(s, "Exemple de lecture", 692, 456, 460, 24, { fontSize: 20, bold: true, color: C.light });
  text(s, "129-OUARZAZATE : score 99,9/100, 5 incidents sur 30 jours et 380,8 h d’indisponibilité sur 90 jours.\n001-CASABLANCA : score 2,7/100, aucun incident sur 90 jours.", 692, 492, 480, 66, { fontSize: 16, color: C.muted });
  note(s, ["Local project report: report/main.tex", "Local assets: report/images/onda/onda_alerts.png and report/images/onda/onda_detail.png"]);
}

async function slideHuman() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "10 · Facteur humain", "La prévention commence avant la modification en production", 11);
  await image(s, IMG("onda", "onda_human.png"), 52, 158, 700, 448, "contain", "Human factor and REX checklist");
  rect(s, 812, 170, 386, 105, C.panel, true, C.teal, 1);
  text(s, "Checklist pré-intervention", 840, 190, 330, 26, { fontSize: 22, bold: true, color: C.teal });
  text(s, "Sauvegarde · intégrité firmware · fenêtre horaire · notification DSI", 840, 232, 322, 30, { fontSize: 16, color: C.muted });
  rect(s, 812, 302, 386, 105, C.panel, true, C.red, 1);
  text(s, "Signal d’alerte", 840, 322, 330, 26, { fontSize: 22, bold: true, color: C.red });
  text(s, "Une conformité faible signale un risque d’erreur humaine avant l’opération.", 840, 364, 322, 30, { fontSize: 16, color: C.muted });
  rect(s, 812, 434, 386, 126, C.panel, true, C.purple, 1);
  text(s, "REX opérationnel", 840, 454, 330, 26, { fontSize: 22, bold: true, color: C.purple });
  text(s, "Les incidents et les bonnes pratiques sont capitalisés pour éviter la répétition des mêmes erreurs.", 840, 496, 322, 44, { fontSize: 16, color: C.muted });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_human.png"]);
}

async function slidePrevention() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "11 · Prévention", "Convertir le score en plan d’intervention priorisé", 12);
  await image(s, IMG("onda", "onda_prevention.png"), 45, 150, 830, 470, "contain", "WAN outage prevention plan");
  rect(s, 914, 172, 284, 95, C.panel, true, C.orange, 1);
  text(s, "Causes & opérateurs", 934, 190, 245, 24, { fontSize: 20, bold: true, color: C.orange });
  text(s, "Liaison WAN, électricité, Orange ou IAM.", 934, 228, 235, 25, { fontSize: 16, color: C.muted });
  rect(s, 914, 294, 284, 95, C.panel, true, C.blue, 1);
  text(s, "Temporalité", 934, 312, 245, 24, { fontSize: 20, bold: true, color: C.blue });
  text(s, "Repérer les périodes et horaires plus exposés.", 934, 350, 235, 25, { fontSize: 16, color: C.muted });
  rect(s, 914, 416, 284, 144, C.panel, true, C.teal, 1);
  text(s, "Action recommandée", 934, 434, 245, 24, { fontSize: 20, bold: true, color: C.teal });
  text(s, "Vérifier l’UPS, planifier une mission technique ou escalader un ticket opérateur.", 934, 472, 235, 60, { fontSize: 16, color: C.muted });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_prevention.png"]);
}

async function slideModel() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "12 · Validation IA", "Le modèle favorise le rappel pour ne pas manquer les sites à vérifier", 13);
  await image(s, IMG("onda", "onda_model.png"), 48, 154, 835, 470, "contain", "AI model diagnostic and performance");
  metric(s, 922, 170, 260, "88,44 %", "rappel", C.teal);
  metric(s, 922, 292, 260, "54,70 %", "précision", C.orange);
  metric(s, 922, 414, 260, "67,59 %", "F1-score", C.blue);
  text(s, "Lecture métier", 922, 548, 250, 25, { fontSize: 18, bold: true, color: C.light });
  text(s, "Le rappel élevé est cohérent avec une logique de prévention : mieux vaut déclencher une vérification supplémentaire que laisser passer un site réellement exposé.", 922, 580, 260, 62, { fontSize: 15, color: C.muted });
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_model.png", "Reported metrics: accuracy 62.39%, precision 54.70%, recall 88.44%, F1 67.59%, ROC-AUC 0.777, PR-AUC 0.705"]);
}

async function slideCyberRange() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "13 · CyberRange", "Valider la posture défensive dans un périmètre explicitement isolé", 14);
  await image(s, IMG("cyberrange", "cr_network.png"), 48, 158, 550, 400, "contain", "CyberRange network");
  await image(s, IMG("cyberrange", "cr_architecture.png"), 640, 158, 570, 400, "contain", "CyberRange architecture");
  rect(s, 86, 585, 1070, 44, C.panel2, true, C.orange, 1);
  text(s, "Règle centrale : le scénario est réalisé dans un laboratoire Host-Only, séparé de la production, avec des preuves collectées à chaque étape.", 110, 592, 1020, 30, { fontSize: 18, bold: true, color: C.text, alignment: "center" });
  note(s, ["Local project report: report/main.tex", "Local assets: report/images/cyberrange/cr_network.png and report/images/cyberrange/cr_architecture.png"]);
}

async function slideAttackChain() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "14 · Simulation contrôlée", "Un scénario lisible : découvrir, observer, qualifier", 15);
  await image(s, IMG("cyberrange", "cr_killchain.png"), 50, 157, 770, 430, "contain", "CyberRange attack lifecycle");
  rect(s, 875, 170, 320, 90, C.panel, true, C.blue, 1);
  text(s, "Découverte", 900, 188, 265, 24, { fontSize: 21, bold: true, color: C.blue });
  text(s, "Cartographier les actifs du laboratoire et vérifier le périmètre.", 900, 226, 265, 30, { fontSize: 16, color: C.muted });
  rect(s, 875, 286, 320, 90, C.panel, true, C.teal, 1);
  text(s, "Observation", 900, 304, 265, 24, { fontSize: 21, bold: true, color: C.teal });
  text(s, "Capturer les flux et les traces utiles à l’analyse.", 900, 342, 265, 30, { fontSize: 16, color: C.muted });
  rect(s, 875, 402, 320, 90, C.panel, true, C.orange, 1);
  text(s, "Qualification", 900, 420, 265, 24, { fontSize: 21, bold: true, color: C.orange });
  text(s, "Relier les indices à une règle et à une action défensive.", 900, 458, 265, 30, { fontSize: 16, color: C.muted });
  pill(s, "Usage pédagogique et autorisé uniquement", 875, 528, 320, C.red);
  note(s, ["Local project report: report/main.tex", "Local asset: report/images/cyberrange/cr_killchain.png", "The simulation is presented only as an authorized, isolated defensive lab"]);
}

async function slideEvidence() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "15 · Preuves techniques", "Des traces exploitables pour passer de l’observation à la défense", 16);
  await image(s, IMG("cyberrange", "cr_nmap.png"), 50, 160, 350, 200, "contain", "Network discovery evidence");
  await image(s, IMG("cyberrange", "cr_wireshark.png"), 465, 160, 350, 200, "contain", "Traffic analysis evidence");
  await image(s, IMG("cyberrange", "cr_decompile.png"), 880, 160, 350, 200, "contain", "Decompilation evidence");
  const cards = [
    ["Nmap", "Identifier les services visibles dans le laboratoire.", C.blue],
    ["Wireshark", "Comparer les paquets et reconstruire la chronologie.", C.teal],
    ["Ghidra", "Qualifier un artefact et comprendre son comportement.", C.orange],
  ];
  cards.forEach((c, i) => {
    const x = 50 + i * 415;
    rect(s, x, 400, 350, 130, C.panel, true, c[2], 1);
    text(s, c[0], x + 20, 420, 300, 26, { fontSize: 22, bold: true, color: c[2] });
    text(s, c[1], x + 20, 460, 300, 50, { fontSize: 17, color: C.muted });
  });
  text(s, "La valeur du CyberRange est la traçabilité : chaque étape du scénario produit un élément vérifiable et réutilisable pour la formation.", 95, 578, 1090, 36, { fontSize: 19, color: C.light, alignment: "center" });
  note(s, ["Local project report: report/main.tex", "Local assets: report/images/cyberrange/cr_nmap.png, cr_wireshark.png, and cr_decompile.png"]);
}

async function slideDefence() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "16 · Réponse", "Les indicateurs deviennent des règles, puis des mesures de remédiation", 17);
  await image(s, IMG("cyberrange", "cr_ghidra_graph.png"), 52, 160, 360, 230, "contain", "Ghidra analysis graph");
  await image(s, IMG("cyberrange", "cr_yara.png"), 455, 160, 360, 230, "contain", "YARA detection rule");
  await image(s, IMG("cyberrange", "cr_snort.png"), 858, 160, 360, 230, "contain", "Snort detection rule");
  const arrows = [["Comprendre", C.blue], ["Détecter", C.orange], ["Alerter", C.red]];
  arrows.forEach((a, i) => {
    const x = 105 + i * 405;
    text(s, a[0], x, 420, 220, 30, { fontSize: 22, bold: true, color: a[1], alignment: "center" });
    rect(s, x + 105, 458, 220, 62, a[1], true);
    text(s, i === 0 ? "analyse" : i === 1 ? "règle" : "signal", x + 105, 470, 220, 36, { fontSize: 20, bold: true, color: C.bg, alignment: "center" });
  });
  text(s, "→", 390, 467, 60, 45, { fontSize: 34, bold: true, color: C.muted, alignment: "center" });
  text(s, "→", 795, 467, 60, 45, { fontSize: 34, bold: true, color: C.muted, alignment: "center" });
  rect(s, 270, 575, 740, 43, C.panel2, true, C.teal, 1);
  text(s, "Remédiation documentée : corriger, vérifier, capitaliser dans le REX", 290, 581, 700, 30, { fontSize: 18, bold: true, color: C.teal, alignment: "center" });
  note(s, ["Local project report: report/main.tex", "Local assets: report/images/cyberrange/cr_ghidra_graph.png, cr_yara.png, and cr_snort.png"]);
}

async function slideConclusion() {
  const s = pres.slides.add(); s.background.fill = C.bg; addHeader(s, "17 · Conclusion", "Une résilience réseau pilotée par le risque et l’expérience", 18);
  rect(s, 70, 180, 1140, 90, C.panel, true, C.blue, 1);
  text(s, "Le modèle répond à la question : où agir avant la prochaine coupure ?", 104, 205, 1070, 38, { fontSize: 29, bold: true, color: C.text, alignment: "center" });
  const values = [
    ["Anticiper", "Score de risque et prévision à 30 jours", C.blue],
    ["Sécuriser", "Checklist, REX et laboratoire isolé", C.teal],
    ["Prouver", "Métriques, traces et règles de détection", C.orange],
    ["Améliorer", "Actions préventives et capitalisation", C.purple],
  ];
  values.forEach((v, i) => {
    const x = 80 + i * 285;
    rect(s, x, 330, 250, 150, C.panel, true, v[2], 1);
    text(s, v[0], x + 20, 350, 210, 30, { fontSize: 24, bold: true, color: v[2], alignment: "center" });
    text(s, v[1], x + 22, 404, 206, 52, { fontSize: 17, color: C.muted, alignment: "center" });
  });
  text(s, "Perspectives : enrichir les données de maintenance, suivre les actions jusqu’à leur clôture, calibrer les seuils avec les équipes et intégrer davantage de scénarios défensifs.", 110, 548, 1060, 48, { fontSize: 20, color: C.light, alignment: "center" });
  text(s, "Merci pour votre attention", 440, 625, 400, 34, { fontSize: 25, bold: true, color: C.text, alignment: "center" });
  note(s, ["Local project report: report/main.tex", "Conclusion synthesized from the integrated ONDA Risk Intelligence and CyberRange project"]);
}

async function writeBlob(outFile, b) {
  const arr = new Uint8Array(b);
  await fs.writeFile(outFile, arr);
}

await slideCover();
await slideStakes();
await slideObjective();
await slideSolution();
await slideDataModel();
await slideUseCases();
await slideArchitecture();
await slideModules();
await slideExecutive();
await slideRiskAnalysis();
await slideHuman();
await slidePrevention();
await slideModel();
await slideCyberRange();
await slideAttackChain();
await slideEvidence();
await slideDefence();
await slideConclusion();

await fs.mkdir(path.dirname(OUT), { recursive: true });
const pptx = await PresentationFile.exportPptx(pres);
await pptx.save(OUT);

const montage = await pres.export({ format: "webp", montage: true, scale: 1 });
await writeBlob(path.join(BUILD, "deck_montage.webp"), montage);
for (let i = 0; i < pres.slides.items.length; i++) {
  const png = await pres.export({ slide: pres.slides.items[i], format: "png", scale: 1 });
  await writeBlob(path.join(BUILD, `slide-${String(i + 1).padStart(2, "0")}.png`), png);
}
console.log(`Created ${OUT}`);
console.log(`Slides ${pres.slides.items.length}`);
