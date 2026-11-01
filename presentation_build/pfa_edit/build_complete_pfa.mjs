import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde";
const WORK = path.join(ROOT, "presentation_build", "pfa_edit");
const OUT = path.join(ROOT, "report", "Presentation_PFA_ONDA_CyberRange_Premium.pptx");
const STAGING = path.join(ROOT, ".codex-finalizer");
const SKILL_DIR = "C:/Users/nouam/.codex/plugins/cache/openai-primary-runtime/presentations/26.903.11726/skills/Presentations";
const RUNTIME_PYTHON = "C:/Users/nouam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
const FONT = "Arial";
const { makeNativeBulletParagraphs } = await import(pathToFileURL("C:/Users/nouam/.codex/plugins/cache/openai-primary-runtime/presentations/26.903.11726/skills/Presentations/container_tools/artifact_tool_utils.mjs").href);
const W = 1920;
const H = 1080;
const C = {
  black: "#061018",
  ink: "#091D2A",
  panel: "#102738",
  green: "#B9E45B",
  greenSoft: "#E1EBDD",
  blue: "#54C9E8",
  white: "#F6FAF5",
  muted: "#A9B9C5",
  line: "#1B4A55",
};

const ONDA = (name) => path.join(ROOT, "report", "images", "onda", name);
const CR = (name) => path.join(ROOT, "report", "images", "cyberrange", name);
const DIAGRAM = (name) => path.join(ROOT, "report", "images", "diagrams", name);

async function blob(file) {
  const bytes = await fs.readFile(file);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function addShape(slide, geometry, position, fill = "none", line = { style: "solid", fill: "none", width: 0 }, extra = {}) {
  return slide.shapes.add({ geometry, position, fill, line, ...extra });
}

function addText(slide, text, position, style = {}) {
  const shape = addShape(slide, "textbox", position, "none");
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: style.fontSize ?? 28,
    color: style.color ?? C.greenSoft,
    bold: style.bold ?? false,
    italic: style.italic ?? false,
    autoFit: "none",
    ...style,
  };
  return shape;
}

async function addImage(slide, file, position, alt, fit = "contain") {
  return slide.images.add({
    blob: await blob(file),
    contentType: file.toLowerCase().endsWith(".jpg") ? "image/jpeg" : "image/png",
    alt,
    fit,
    position,
  });
}

async function addFrameImage(slide, file, position, alt, fit = "contain") {
  const pad = 16;
  addShape(slide, "roundRect", position, C.panel, { style: "solid", fill: C.green, width: 2 }, { borderRadius: 12 });
  return addImage(slide, file, {
    left: position.left + pad,
    top: position.top + pad,
    width: position.width - 2 * pad,
    height: position.height - 2 * pad,
  }, alt, fit);
}

function addPill(slide, text, position, accent = C.blue) {
  addShape(slide, "roundRect", position, C.panel, { style: "solid", fill: accent, width: 1 }, { borderRadius: position.height / 2 });
  addText(slide, text, { left: position.left + 16, top: position.top + 7, width: position.width - 32, height: position.height - 12 }, { fontSize: 15, color: C.greenSoft, bold: true, align: "center", characterSpacing: 1 });
}

function addMetricCard(slide, value, label, position, accent = C.green) {
  addShape(slide, "roundRect", position, C.panel, { style: "solid", fill: accent, width: 2 }, { borderRadius: 16 });
  addShape(slide, "rect", { left: position.left, top: position.top, width: 8, height: position.height }, accent);
  addText(slide, value, { left: position.left + 26, top: position.top + 26, width: position.width - 44, height: 52 }, { fontSize: 34, color: accent, bold: true });
  addText(slide, label, { left: position.left + 28, top: position.top + 91, width: position.width - 46, height: 30 }, { fontSize: 18, color: C.muted, bold: true });
}

function addNode(slide, x, y, color = C.green, size = 16) {
  addShape(slide, "ellipse", { left: x, top: y, width: size, height: size }, color);
}

function addNetworkAccent(slide, left = 1280, top = 220) {
  addShape(slide, "line", { left: left, top: top + 60, width: 260, height: 0 }, "none", { style: "solid", fill: C.line, width: 2 });
  addShape(slide, "line", { left: left + 80, top: top + 60, width: 0, height: 150 }, "none", { style: "solid", fill: C.line, width: 2 });
  addShape(slide, "line", { left: left + 80, top: top + 150, width: 210, height: 0 }, "none", { style: "solid", fill: C.line, width: 2 });
  addShape(slide, "line", { left: left + 210, top: top + 150, width: 0, height: 100 }, "none", { style: "solid", fill: C.line, width: 2 });
  addNode(slide, left - 8, top + 52, C.blue, 16);
  addNode(slide, left + 72, top + 52, C.green, 16);
  addNode(slide, left + 72, top + 142, C.blue, 16);
  addNode(slide, left + 202, top + 142, C.green, 16);
  addNode(slide, left + 202, top + 242, C.blue, 16);
}

function addBullets(slide, items, position, style = {}) {
  const shape = addShape(slide, "textbox", position, "none");
  shape.text = makeNativeBulletParagraphs(items, { marginLeftPoints: 18, hangingPoints: 9, spaceAfterPoints: 7 });
  shape.text.style = {
    typeface: FONT,
    fontSize: style.fontSize ?? 27,
    color: style.color ?? C.greenSoft,
    bold: style.bold ?? false,
    autoFit: "none",
    ...style,
  };
  return shape;
}

function addFooter(slide, number, label = "ONDA · EMSI · PFA 4IIR") {
  addShape(slide, "rect", { left: 0, top: 0, width: 26, height: H }, C.line);
  addShape(slide, "line", { left: 80, top: 1015, width: 1760, height: 0 }, "none", { style: "solid", fill: C.line, width: 2 });
  addText(slide, label, { left: 82, top: 1025, width: 800, height: 28 }, { fontSize: 18, color: C.muted });
  addText(slide, String(number).padStart(2, "0"), { left: 1780, top: 1025, width: 70, height: 28 }, { fontSize: 18, color: C.green, bold: true, align: "right" });
  addShape(slide, "ellipse", { left: 86, top: 976, width: 14, height: 14 }, C.green);
  addShape(slide, "ellipse", { left: 108, top: 976, width: 14, height: 14 }, C.green);
  addShape(slide, "ellipse", { left: 130, top: 976, width: 14, height: 14 }, C.green);
}

function addHeader(slide, eyebrow, title, number) {
  addFooter(slide, number);
  addText(slide, eyebrow.toUpperCase(), { left: 84, top: 48, width: 700, height: 30 }, { fontSize: 19, color: C.greenSoft, bold: true, characterSpacing: 1 });
  addShape(slide, "roundRect", { left: 1490, top: 43, width: 340, height: 38 }, C.panel, { style: "solid", fill: C.blue, width: 1 }, { borderRadius: 19 });
  addShape(slide, "ellipse", { left: 1510, top: 55, width: 14, height: 14 }, C.green);
  addText(slide, "ONDA RISK INTELLIGENCE", { left: 1535, top: 51, width: 275, height: 24 }, { fontSize: 16, color: C.greenSoft, bold: true, align: "center" });
  addText(slide, title, { left: 84, top: 86, width: 1750, height: 90 }, { fontSize: 54, color: C.green, bold: true });
  addShape(slide, "line", { left: 84, top: 198, width: 300, height: 0 }, "none", { style: "solid", fill: C.blue, width: 3 });
}

function notes(slide, lines) {
  slide.speakerNotes.textFrame.setText(`[Sources]\n- ${lines.join("\n- ")}`);
  slide.speakerNotes.setVisible(true);
}

function makeSlide(presentation, number, eyebrow, title) {
  const slide = presentation.slides.add();
  slide.background.fill = C.black;
  addHeader(slide, eyebrow, title, number);
  return slide;
}

function sectionSlide(presentation, number, part, title, subtitle) {
  const slide = presentation.slides.add();
  slide.background.fill = C.black;
  addShape(slide, "rect", { left: 0, top: 0, width: 26, height: H }, C.line);
  addText(slide, part, { left: 90, top: 150, width: 600, height: 56 }, { fontSize: 32, color: C.greenSoft, bold: true });
  addText(slide, title, { left: 90, top: 235, width: 1550, height: 150 }, { fontSize: 78, color: C.green, bold: true });
  addText(slide, subtitle, { left: 94, top: 430, width: 1030, height: 110 }, { fontSize: 31, color: C.greenSoft });
  addShape(slide, "line", { left: 94, top: 600, width: 520, height: 0 }, "none", { style: "solid", fill: C.blue, width: 4 });
  addShape(slide, "rect", { left: 1420, top: 180, width: 290, height: 290 }, C.panel, { style: "solid", fill: C.green, width: 2 }, { borderRadius: 20 });
  addText(slide, String(number).padStart(2, "0"), { left: 1470, top: 230, width: 190, height: 170 }, { fontSize: 118, color: C.green, bold: true });
  addShape(slide, "rect", { left: 1430, top: 650, width: 170, height: 20 }, C.green);
  addShape(slide, "rect", { left: 1430, top: 690, width: 270, height: 20 }, C.green);
  addShape(slide, "rect", { left: 1430, top: 730, width: 220, height: 20 }, C.green);
  const sequence = number === 4 ? ["01 · CADRER", "02 · MODÉLISER", "03 · PRÉPARER"] : number === 10 ? ["01 · CONSTRUIRE", "02 · SIMULER", "03 · VALIDER"] : ["01 · ORGANISER", "02 · MESURER", "03 · CAPITALISER"];
  sequence.forEach((label, index) => addPill(slide, label, { left: 94 + index * 245, top: 830, width: 220, height: 38 }, index === 1 ? C.blue : C.green));
  addFooter(slide, number, "ONDA · EMSI · PRÉSENTATION PFA");
  return slide;
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } });

// 1. Cover
{
  const slide = presentation.slides.add();
  slide.background.fill = C.ink;
  addShape(slide, "rect", { left: 0, top: 0, width: 26, height: H }, C.line);
  await addImage(slide, ONDA("onda_logo.png"), { left: 115, top: 70, width: 170, height: 90 }, "Logo ONDA", "contain");
  await addImage(slide, CR("emsi_logo.png"), { left: 1570, top: 70, width: 250, height: 105 }, "Logo EMSI", "contain");
  addNetworkAccent(slide, 1080, 195);
  addText(slide, "PROJET DE FIN D’ANNÉE · 4IIR", { left: 95, top: 250, width: 620, height: 50 }, { fontSize: 25, color: C.green, bold: true });
  addText(slide, "Conception d’un modèle\nd’analyse des risques\net d’alertes prédictives", { left: 95, top: 340, width: 950, height: 240 }, { fontSize: 66, color: C.white, bold: true });
  addText(slide, "Données de maintenance · Réseaux WAN · CyberRange", { left: 100, top: 620, width: 890, height: 45 }, { fontSize: 28, color: C.green });
  addShape(slide, "line", { left: 100, top: 700, width: 900, height: 0 }, "none", { style: "solid", fill: C.blue, width: 4 });
  addText(slide, "Une plateforme intégrée pour anticiper les risques, réduire l’erreur humaine et valider la détection dans un laboratoire contrôlé.", { left: 100, top: 755, width: 920, height: 110 }, { fontSize: 28, color: C.muted });
  addPill(slide, "PRÉDIRE  /  PRÉVENIR  /  VALIDER", { left: 100, top: 900, width: 520, height: 38 }, C.blue);
  addShape(slide, "roundRect", { left: 1260, top: 290, width: 510, height: 470 }, C.panel, { style: "solid", fill: C.green, width: 2 }, { borderRadius: 18 });
  addPill(slide, "VUE EXÉCUTIVE", { left: 1285, top: 242, width: 190, height: 34 }, C.green);
  addPill(slide, "RISQUE WAN", { left: 1490, top: 242, width: 170, height: 34 }, C.blue);
  await addImage(slide, ONDA("onda_overview.png"), { left: 1282, top: 312, width: 466, height: 300 }, "Vue d’ensemble de la plateforme ONDA Risk Intelligence", "contain");
  addText(slide, "Azzat Nouamane\nHnid Aimane", { left: 1305, top: 640, width: 420, height: 70 }, { fontSize: 27, color: C.white, bold: true });
  addText(slide, "Encadrement professionnel : Mme Jaouhari Ouafaa · ONDA\nEncadrement pédagogique : Mme Khadija Bousmar · EMSI", { left: 1305, top: 730, width: 430, height: 95 }, { fontSize: 18, color: C.muted });
  addFooter(slide, 1, "ONDA · EMSI · SOUTENANCE 2026");
  notes(slide, ["Local project report: report/main.tex", "Local assets: report/images/onda/onda_overview.png and report/images/cyberrange/emsi_logo.png"]);
}

// 2. Agenda
{
  const slide = presentation.slides.add();
  slide.background.fill = C.black;
  addShape(slide, "rect", { left: 0, top: 0, width: 26, height: H }, C.line);
  addText(slide, "SOMMAIRE", { left: 90, top: 120, width: 900, height: 80 }, { fontSize: 62, color: C.green, bold: true });
  addText(slide, "Une progression en trois parties, sans partie entrepreneuriale", { left: 94, top: 215, width: 950, height: 48 }, { fontSize: 28, color: C.muted });
  const blocks = [
    ["01", "Étude et conception", "Contexte, besoins, architecture, données et modèle prédictif"],
    ["02", "Réalisation et validation", "Plateforme ONDA, prévention WAN et laboratoire CyberRange"],
    ["03", "Gestion de projet et bilan", "Méthode, répartition, résultats, limites et perspectives"],
  ];
  const xs = [90, 670, 1250];
  for (let i = 0; i < blocks.length; i += 1) {
    const [num, title, body] = blocks[i];
    addShape(slide, "roundRect", { left: xs[i], top: 390, width: 500, height: 395 }, C.panel, { style: "solid", fill: C.green, width: 2 }, { borderRadius: 18 });
    addText(slide, num, { left: xs[i] + 38, top: 425, width: 100, height: 65 }, { fontSize: 42, color: C.green, bold: true });
    addText(slide, title, { left: xs[i] + 40, top: 520, width: 420, height: 70 }, { fontSize: 31, color: C.white, bold: true });
    addText(slide, body, { left: xs[i] + 40, top: 635, width: 405, height: 110 }, { fontSize: 23, color: C.greenSoft });
    addShape(slide, "line", { left: xs[i] + 40, top: 600, width: 120, height: 0 }, "none", { style: "solid", fill: i === 1 ? C.blue : C.green, width: 3 });
  }
  addFooter(slide, 2, "ONDA · EMSI · PLAN DE SOUTENANCE");
  notes(slide, ["Internal structure of the presentation based on the supplied project scope."]);
}

// 3. Introduction
{
  const slide = makeSlide(presentation, 3, "Introduction", "Le projet en une phrase");
  addText(slide, "Notre projet propose une plateforme intelligente dédiée à l’analyse et à la prévention des risques liés aux réseaux WAN des aéroports de l’ONDA. Elle combine l’intelligence artificielle, les données de maintenance et un laboratoire CyberRange isolé permettant de simuler des attaques dans un environnement contrôlé.", { left: 100, top: 300, width: 860, height: 260 }, { fontSize: 32, color: C.greenSoft });
  addText(slide, "La solution prévoit les incidents, génère des alertes, recommande des actions préventives et permet de tester les mécanismes de détection et de remédiation.", { left: 100, top: 650, width: 820, height: 150 }, { fontSize: 30, color: C.green });
  await addFrameImage(slide, DIAGRAM("solution_pipeline.png"), { left: 1040, top: 270, width: 760, height: 500 }, "Chaîne intégrée de la plateforme ONDA et du CyberRange", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/diagrams/solution_pipeline.png"]);
}

// 4. Part 1 divider
{
  const slide = sectionSlide(presentation, 4, "PARTIE 1", "Étude et conception", "Comprendre le besoin, définir l’architecture et préparer les données avant l’implémentation.");
  notes(slide, ["Internal section divider based on the project structure."]);
}

// 5. Context and problem
{
  const slide = makeSlide(presentation, 5, "Étude et conception", "Contexte ONDA et problématique");
  addText(slide, "CONTEXTE ONDA", { left: 100, top: 285, width: 500, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addBullets(slide, ["Office National des Aéroports du Maroc", "27 aéroports reliés par des réseaux WAN", "Services critiques dépendants de la disponibilité réseau", "Maintenance et incidents comme sources de données"], { left: 100, top: 345, width: 760, height: 330 }, { fontSize: 27 });
  addText(slide, "PROBLÉMATIQUE", { left: 1030, top: 285, width: 500, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addBullets(slide, ["Intervention souvent déclenchée après la panne", "Difficulté à repérer les sites les plus vulnérables", "Risque d’interruption des opérations aéroportuaires", "Besoin d’alertes prédictives et de recommandations"], { left: 1030, top: 345, width: 740, height: 330 }, { fontSize: 27 });
  addShape(slide, "line", { left: 930, top: 290, width: 0, height: 430 }, "none", { style: "solid", fill: C.line, width: 2 });
  addMetricCard(slide, "27", "aéroports interconnectés", { left: 100, top: 770, width: 270, height: 150 }, C.green);
  addMetricCard(slide, "864", "incidents historiques", { left: 405, top: 770, width: 270, height: 150 }, C.blue);
  addMetricCard(slide, "30 j", "horizon de prévision", { left: 710, top: 770, width: 270, height: 150 }, C.green);
  addShape(slide, "roundRect", { left: 1040, top: 770, width: 720, height: 150 }, C.panel, { style: "solid", fill: C.blue, width: 2 }, { borderRadius: 16 });
  addText(slide, "Le passage du réactif au prédictif", { left: 1080, top: 800, width: 640, height: 42 }, { fontSize: 30, color: C.white, bold: true, align: "center" });
  addText(slide, "Identifier les sites prioritaires avant la coupure", { left: 1090, top: 860, width: 620, height: 35 }, { fontSize: 22, color: C.greenSoft, align: "center" });
  notes(slide, ["Local project report: report/main.tex", "Key figures consolidated from the ONDA Risk Intelligence dashboard."]);
}

// 6. Objectives and scope
{
  const slide = makeSlide(presentation, 6, "Étude et conception", "Objectifs et périmètre");
  addText(slide, "OBJECTIFS", { left: 100, top: 275, width: 500, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addBullets(slide, ["Attribuer un score de risque de 0 à 100", "Prévoir les incidents sur un horizon de 30 jours", "Prioriser les actions de maintenance et de prévention", "Réduire les erreurs grâce aux check-lists et au REX"], { left: 100, top: 340, width: 760, height: 340 }, { fontSize: 27 });
  addText(slide, "PÉRIMÈTRE CYBERRANGE", { left: 1030, top: 275, width: 600, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addBullets(slide, ["Laboratoire isolé du réseau de production", "Simulation autorisée d’une chaîne d’attaque", "Observation des traces réseau et système", "Validation des règles de détection et de remédiation"], { left: 1030, top: 340, width: 740, height: 340 }, { fontSize: 27 });
  addShape(slide, "roundRect", { left: 380, top: 770, width: 1180, height: 120 }, C.panel, { style: "solid", fill: C.blue, width: 2 }, { borderRadius: 18 });
  addText(slide, "La plateforme aide à décider. Le CyberRange aide à vérifier.", { left: 430, top: 802, width: 1080, height: 50 }, { fontSize: 34, color: C.white, bold: true, align: "center" });
  notes(slide, ["Local project report: report/main.tex", "Scope consolidated from the ONDA Risk Intelligence and CyberRange project descriptions."]);
}

// 7. Global architecture
{
  const slide = makeSlide(presentation, 7, "Étude et conception", "Architecture globale de la solution");
  addText(slide, "La conception sépare la supervision des risques et l’expérimentation offensive. Les deux espaces partagent les résultats utiles à la décision, sans exposer la production.", { left: 100, top: 280, width: 700, height: 160 }, { fontSize: 29, color: C.greenSoft });
  addBullets(slide, ["Collecte et préparation des historiques", "Modèle de scoring et moteur d’alertes", "Interfaces ONDA pour les équipes DSI", "Laboratoire virtualisé pour les tests contrôlés"], { left: 100, top: 515, width: 720, height: 260 }, { fontSize: 26 });
  await addFrameImage(slide, DIAGRAM("deployment_architecture.png"), { left: 900, top: 270, width: 900, height: 540 }, "Architecture de déploiement ONDA et CyberRange", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/diagrams/deployment_architecture.png"]);
}

// 8. Data and model
{
  const slide = makeSlide(presentation, 8, "Étude et conception", "Données et modèle prédictif");
  addText(slide, "DONNÉES D’ENTRÉE", { left: 100, top: 280, width: 500, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addBullets(slide, ["Historique des incidents et dates de panne", "Durée d’indisponibilité et récence", "Catégorie, cause et opérateur", "Nombre d’incidents sur 30 et 90 jours"], { left: 100, top: 345, width: 730, height: 280 }, { fontSize: 27 });
  addText(slide, "CHAÎNE DE TRAITEMENT", { left: 100, top: 700, width: 600, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  const stages = ["NETTOYAGE", "VARIABLES", "ENTRAÎNEMENT", "SCORE 0–100", "ALERTE 30 J"];
  stages.forEach((label, index) => addPill(slide, label, { left: 100 + index * 160, top: 755, width: 145, height: 38 }, index === 2 ? C.blue : C.green));
  await addFrameImage(slide, DIAGRAM("data_model.png"), { left: 990, top: 280, width: 760, height: 490 }, "Modèle de données de la solution", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/diagrams/data_model.png"]);
}

// 9. CyberRange architecture
{
  const slide = makeSlide(presentation, 9, "Étude et conception", "Architecture du laboratoire CyberRange");
  addText(slide, "Le laboratoire repose sur un réseau Host-Only isolé. Une machine attaquante et une machine victime communiquent uniquement à l’intérieur du périmètre de test.", { left: 100, top: 280, width: 700, height: 160 }, { fontSize: 29, color: C.greenSoft });
  addBullets(slide, ["Kali Linux comme machine d’analyse", "Metasploitable 2 comme cible volontairement vulnérable", "VirtualBox et réseau privé Host-Only", "Aucun accès Internet nécessaire au scénario"], { left: 100, top: 515, width: 730, height: 260 }, { fontSize: 26 });
  await addFrameImage(slide, CR("cr_architecture.png"), { left: 900, top: 300, width: 900, height: 500 }, "Architecture isolée du laboratoire CyberRange", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/cyberrange/cr_architecture.png"]);
}

// 10. Part 2 divider
{
  const slide = sectionSlide(presentation, 10, "PARTIE 2", "Réalisation et validation", "Mettre en œuvre les modules, conduire la simulation et vérifier les résultats obtenus.");
  notes(slide, ["Internal section divider based on the project structure."]);
}

// 11. Platform modules
{
  const slide = makeSlide(presentation, 11, "Réalisation et validation", "Plateforme ONDA Risk Intelligence");
  addText(slide, "La plateforme centralise la supervision du risque WAN et transforme les historiques de maintenance en décisions opérationnelles.", { left: 100, top: 275, width: 760, height: 120 }, { fontSize: 30, color: C.greenSoft });
  addBullets(slide, ["Portail exécutif pour la vision globale", "Analyse IA, alertes et fiches détaillées", "Facteur humain, check-lists et REX", "Prévention des coupures et plan d’action"], { left: 100, top: 460, width: 750, height: 290 }, { fontSize: 27 });
  await addFrameImage(slide, ONDA("onda_modules.png"), { left: 980, top: 270, width: 770, height: 520 }, "Modules principaux de la plateforme ONDA Risk Intelligence", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_modules.png"]);
}

// 12. AI analytics and alerts
{
  const slide = makeSlide(presentation, 12, "Réalisation et validation", "Analyse IA et alertes prédictives");
  addText(slide, "La plateforme classe les sites selon leur exposition et fournit aux équipes une première liste de priorités.", { left: 100, top: 275, width: 760, height: 110 }, { fontSize: 30, color: C.greenSoft });
  addBullets(slide, ["864 incidents historiques analysés", "11 sites classés à risque élevé", "Score moyen affiché sur 100", "Alerte enrichie par la récence et l’indisponibilité"], { left: 100, top: 450, width: 650, height: 280 }, { fontSize: 27 });
  await addFrameImage(slide, ONDA("onda_alerts.png"), { left: 850, top: 275, width: 980, height: 545 }, "Écran des alertes de risque actives", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_alerts.png"]);
}

// 13. Human factor and prevention
{
  const slide = makeSlide(presentation, 13, "Réalisation et validation", "Prévention opérationnelle");
  addText(slide, "Le risque ne vient pas uniquement de la technologie. La plateforme encadre l’intervention humaine et transforme les incidents en règles réutilisables.", { left: 100, top: 275, width: 760, height: 140 }, { fontSize: 29, color: C.greenSoft });
  addText(slide, "FACTEUR HUMAIN & REX", { left: 100, top: 490, width: 650, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addBullets(slide, ["Sauvegarde de configuration avant modification", "Vérification de l’intégrité et du rollback", "Validation de la connectivité après intervention", "Capitalisation des erreurs et bonnes pratiques"], { left: 100, top: 550, width: 760, height: 280 }, { fontSize: 25 });
  await addFrameImage(slide, ONDA("onda_human.png"), { left: 980, top: 270, width: 370, height: 520 }, "Checklist du facteur humain et module REX", "contain");
  await addFrameImage(slide, ONDA("onda_prevention.png"), { left: 1380, top: 270, width: 450, height: 520 }, "Plan de prévention des coupures WAN", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local assets: report/images/onda/onda_human.png and report/images/onda/onda_prevention.png"]);
}

// 14. Attack chain
{
  const slide = makeSlide(presentation, 14, "Réalisation et validation", "Simulation d’une chaîne d’attaque");
  addText(slide, "Le CyberRange reproduit une chaîne complète dans le laboratoire : reconnaissance, exploitation, payload, canal de commande, analyse et détection.", { left: 100, top: 275, width: 800, height: 130 }, { fontSize: 30, color: C.greenSoft });
  await addFrameImage(slide, CR("cr_killchain.png"), { left: 120, top: 480, width: 1660, height: 360 }, "Chaîne d’attaque simulée dans le CyberRange", "contain");
  addText(slide, "Cadre : environnement autorisé, isolé et destiné à la validation défensive", { left: 260, top: 890, width: 1400, height: 50 }, { fontSize: 25, color: C.blue, bold: true, align: "center" });
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/cyberrange/cr_killchain.png"]);
}

// 15. Evidence and detection
{
  const slide = makeSlide(presentation, 15, "Réalisation et validation", "Preuves techniques et détection");
  addText(slide, "Chaque étape produit des traces exploitables pour expliquer l’incident et améliorer la réponse.", { left: 100, top: 270, width: 840, height: 90 }, { fontSize: 30, color: C.greenSoft });
  const cards = [
    ["01", "cr_nmap.png", "Découverte des services", 100, 430],
    ["02", "cr_wireshark.png", "Observation du trafic", 1040, 430],
    ["03", "cr_yara.png", "Signature du payload", 100, 710],
    ["04", "cr_snort.png", "Alerte réseau", 1040, 710],
  ];
  for (const [num, file, label, left, top] of cards) {
    addText(slide, `${num}  ${label}`, { left, top: top - 45, width: 780, height: 34 }, { fontSize: 22, color: C.green, bold: true });
    await addFrameImage(slide, CR(file), { left, top, width: 780, height: 205 }, label, "contain");
  }
  addText(slide, "Les résultats convergent vers une remédiation documentée et réutilisable.", { left: 330, top: 955, width: 1260, height: 40 }, { fontSize: 24, color: C.blue, bold: true, align: "center" });
  notes(slide, ["Local project report: report/main.tex", "Local assets: report/images/cyberrange/cr_nmap.png, cr_wireshark.png, cr_yara.png and cr_snort.png"]);
}

// 16. Validation results
{
  const slide = makeSlide(presentation, 16, "Réalisation et validation", "Résultats de validation");
  addText(slide, "Le modèle atteint un rappel élevé, ce qui correspond à l’objectif de repérer les situations nécessitant une vérification.", { left: 100, top: 270, width: 820, height: 130 }, { fontSize: 30, color: C.greenSoft });
  const metrics = [["62,39 %", "Accuracy"], ["54,70 %", "Précision"], ["88,44 %", "Rappel"], ["67,59 %", "F1-score"]];
  const mx = [100, 330, 560, 790];
  for (let i = 0; i < metrics.length; i += 1) {
    addShape(slide, "roundRect", { left: mx[i], top: 480, width: 200, height: 150 }, C.panel, { style: "solid", fill: C.green, width: 2 }, { borderRadius: 14 });
    addText(slide, metrics[i][0], { left: mx[i] + 14, top: 510, width: 172, height: 50 }, { fontSize: 29, color: C.green, bold: true, align: "center" });
    addText(slide, metrics[i][1], { left: mx[i] + 10, top: 575, width: 180, height: 30 }, { fontSize: 19, color: C.muted, align: "center" });
  }
  await addFrameImage(slide, ONDA("onda_model.png"), { left: 1030, top: 270, width: 800, height: 540 }, "Diagnostic et métriques du modèle IA", "contain");
  addText(slide, "Les alertes restent une aide à la décision. L’équipe réseau conserve la validation opérationnelle.", { left: 130, top: 770, width: 760, height: 80 }, { fontSize: 25, color: C.blue, bold: true });
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_model.png"]);
}

// 17. Part 3 divider
{
  const slide = sectionSlide(presentation, 17, "PARTIE 3", "Gestion de projet et bilan", "Organiser le binôme, suivre les tâches et tirer les enseignements de la réalisation.");
  notes(slide, ["Internal section divider based on the project structure."]);
}

// 18. Method and team
{
  const slide = makeSlide(presentation, 18, "Gestion de projet et bilan", "Méthode et répartition du travail");
  addText(slide, "MÉTHODE", { left: 100, top: 275, width: 400, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addBullets(slide, ["Approche agile avec validations progressives", "Découpage en lots techniques", "Réunions et suivi régulier", "Tests réalisés au fur et à mesure"], { left: 100, top: 340, width: 700, height: 300 }, { fontSize: 27 });
  addText(slide, "BINÔME", { left: 1030, top: 275, width: 400, height: 40 }, { fontSize: 25, color: C.green, bold: true });
  addText(slide, "Azzat Nouamane\nAnalyse réseau, architecture, modèle IA et intégration\n\nHnid Aimane\nCyberRange, détection, analyse des traces et documentation", { left: 1030, top: 340, width: 720, height: 300 }, { fontSize: 27, color: C.greenSoft });
  addShape(slide, "line", { left: 930, top: 290, width: 0, height: 420 }, "none", { style: "solid", fill: C.line, width: 2 });
  addShape(slide, "roundRect", { left: 380, top: 760, width: 1190, height: 110 }, C.panel, { style: "solid", fill: C.blue, width: 2 }, { borderRadius: 18 });
  addText(slide, "Responsabilité partagée sur l’intégration, le rapport LaTeX et la soutenance", { left: 420, top: 795, width: 1110, height: 44 }, { fontSize: 28, color: C.white, bold: true, align: "center" });
  notes(slide, ["Local project report: report/main.tex", "Team and supervision information supplied by the project authors."]);
}

// 19. Planning and balance
{
  const slide = makeSlide(presentation, 19, "Gestion de projet et bilan", "Planification et livrables");
  addText(slide, "Le travail a été organisé autour de cinq lots : cadrage, opérations offensives, ingénierie du payload, détection et défense, puis restitution.", { left: 100, top: 270, width: 760, height: 150 }, { fontSize: 29, color: C.greenSoft });
  addBullets(slide, ["Cadrage et architecture du laboratoire", "Reconnaissance et exploitation contrôlée", "Analyse statique et rétro-ingénierie", "Règles Snort/YARA et remédiation", "Rapport, supports et simulation orale"], { left: 100, top: 500, width: 720, height: 320 }, { fontSize: 25 });
  await addFrameImage(slide, CR("cr_gantt.png"), { left: 900, top: 300, width: 900, height: 520 }, "Planning et diagramme de Gantt du projet", "contain");
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/cyberrange/cr_gantt.png"]);
}

// 20. Conclusion
{
  const slide = makeSlide(presentation, 20, "Conclusion", "Une approche unifiée du risque");
  addText(slide, "Le projet relie la prédiction des incidents WAN, la prévention des erreurs humaines et la validation technique dans un environnement CyberRange isolé.", { left: 100, top: 290, width: 850, height: 150 }, { fontSize: 34, color: C.white, bold: true });
  addBullets(slide, ["Décider plus tôt grâce au score de risque", "Préparer l’intervention avec des procédures", "Vérifier la détection sur des traces concrètes", "Capitaliser les résultats pour les équipes"], { left: 100, top: 545, width: 780, height: 270 }, { fontSize: 28 });
  await addFrameImage(slide, CR("cr_remediation.png"), { left: 1050, top: 300, width: 680, height: 430 }, "Exemple de remédiation dans le CyberRange", "contain");
  addText(slide, "Merci pour votre attention", { left: 1060, top: 800, width: 660, height: 55 }, { fontSize: 35, color: C.green, bold: true, align: "center" });
  addText(slide, "Questions", { left: 1060, top: 860, width: 660, height: 45 }, { fontSize: 27, color: C.muted, align: "center" });
  notes(slide, ["Local project report: report/main.tex", "Local asset: report/images/cyberrange/cr_remediation.png"]);
}

await fs.mkdir(STAGING, { recursive: true });
await fs.mkdir(path.dirname(OUT), { recursive: true });
const candidatePath = path.join(STAGING, "Presentation_PFA_ONDA_CyberRange_Premium.candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href);
const result = await finalizePresentation({
  workspaceDir: ROOT,
  candidatePath,
  finalPath: OUT,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "18288000,10287000", "--validate-bullet-geometry", "--validate-heading-fit"],
  fontPolicy: { basis: "design", families: [FONT] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(STAGING, "Presentation_PFA_ONDA_CyberRange_Premium.validation.json"),
});
console.log(JSON.stringify(result, null, 2));
console.log(`Created ${OUT}`);
console.log(`Slides ${presentation.slides.items.length}`);
