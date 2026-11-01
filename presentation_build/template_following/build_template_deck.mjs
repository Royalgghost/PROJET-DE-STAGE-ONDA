import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde";
const WORK = path.join(ROOT, "presentation_build", "template_following");
const STARTER = path.join(WORK, "template-starter.pptx");
const OUT = path.join(ROOT, "report", "ONDA_Risk_Intelligence_CyberRange_GreenBlack_Template.pptx");
const SOURCE_LAYOUT_DIR = path.join(WORK, "template-inspect", "layouts");
const ONDA = (name) => path.join(ROOT, "report", "images", "onda", name);
const CR = (name) => path.join(ROOT, "report", "images", "cyberrange", name);
const DIAGRAM = (name) => path.join(ROOT, "report", "images", "diagrams", name);

async function blob(file) {
  const bytes = await fs.readFile(file);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function layoutFor(sourceSlide) {
  const file = path.join(SOURCE_LAYOUT_DIR, `source-slide-${String(sourceSlide).padStart(2, "0")}.layout.json`);
  return JSON.parse(await fs.readFile(file, "utf8"));
}

function indexMap(layout) {
  const map = new Map();
  for (const [index, element] of layout.elements.entries()) map.set(element.aid, index);
  return map;
}

async function rewrite(slide, layout, values) {
  const byAid = indexMap(layout);
  for (const [aid, value] of Object.entries(values)) {
    const index = byAid.get(aid);
    if (index === undefined) throw new Error(`Could not map source element ${aid}`);
    const shape = slide.shapes.items[index];
    if (!shape || !shape.text || typeof shape.text.set !== "function") {
      throw new Error(`Source element ${aid} is not an editable text shape on slide ${slide.index + 1}`);
    }
    shape.text.set(value);
  }
}

async function replaceImageFill(slide, layout, shapeAid, imagePath, alt) {
  const byAid = indexMap(layout);
  const index = byAid.get(shapeAid);
  if (index === undefined) throw new Error(`Could not map image slot ${shapeAid}`);
  const frameShape = slide.shapes.items[index];
  if (!frameShape?.frame) throw new Error(`Image slot ${shapeAid} has no frame`);
  const added = slide.images.add({
    blob: await blob(imagePath),
    contentType: "image/png",
    alt,
    fit: "cover",
    position: { ...frameShape.frame },
  });
  const imageId = added?.data?.imageReference?.id;
  if (!imageId) throw new Error(`Could not resolve image resource for ${shapeAid}`);
  frameShape.fill = { type: "image", imageReference: { id: imageId } };
  added.position = { left: -10000, top: -10000, width: 1, height: 1 };
}

async function coverSvg() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <rect x="0" y="0" width="1280" height="720" fill="#000000"/>
  <path d="M70 330 H1210 M70 482 H1210" stroke="#26331B" stroke-width="1"/>
  <path d="M132 360 H205 M132 370 H190 M132 380 H175 M1075 360 H1148 M1090 370 H1148 M1105 380 H1148" stroke="#A5D63C" stroke-width="4"/>
  <rect x="74" y="600" width="58" height="58" fill="#A5D63C" opacity="0.92"/>
  <rect x="1148" y="600" width="58" height="58" fill="#A5D63C" opacity="0.92"/>
  <rect x="1128" y="577" width="25" height="25" fill="#D7E7C6" opacity="0.8" transform="rotate(45 1140 589)"/>
  <text x="640" y="143" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#F2F2F2">PROJET DE FIN D’ANNÉE · ONDA</text>
  <text x="640" y="188" text-anchor="middle" font-family="Arial, sans-serif" font-size="36" font-style="italic" fill="#A5D63C">Conception d’un modèle d’analyse</text>
  <text x="640" y="230" text-anchor="middle" font-family="Arial, sans-serif" font-size="36" font-style="italic" fill="#A5D63C">des risques et d’alertes</text>
  <text x="640" y="272" text-anchor="middle" font-family="Arial, sans-serif" font-size="36" font-style="italic" fill="#A5D63C">prédictives</text>
  <text x="640" y="302" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#D7E7C6">RISK INTELLIGENCE · CYBERRANGE</text>
  <rect x="463" y="380" width="363" height="282" fill="#111111" stroke="#A5D63C" stroke-width="2"/>
  </svg>`;
}

async function replaceCoverImage(slide) {
  const fullBackground = slide.images.items.find((image) => image.frame?.width > 1800 && image.frame?.height > 900);
  if (!fullBackground) throw new Error("Could not locate the inherited full-slide cover image");
  fullBackground.replace({ svg: await coverSvg(), alt: "ONDA Risk Intelligence and CyberRange cover" });
}

function clearShapeFill(slide, layout, shapeAid) {
  const index = indexMap(layout).get(shapeAid);
  if (index === undefined) throw new Error(`Could not map image slot ${shapeAid}`);
  const frameShape = slide.shapes.items[index];
  frameShape.fill = { type: "none" };
}

function note(slide, sources) {
  slide.speakerNotes.textFrame.setText(`[Sources]\n- ${sources.join("\n- ")}`);
  slide.speakerNotes.setVisible(true);
}

const copy = {
  1: {
    "sh/dgzetcfa": "Conception d’un modèle d’analyse\ndes risques et d’alertes\nprédictives",
    "sh/1cvuxc7e": "PROJET DE FIN D’ANNÉE · ONDA",
  },
  2: {
    "sh/q5wjelsz": "ENJEU DU PROJET",
    "sh/ove9o7yd": "CONTINUITÉ RÉSEAU",
    "sh/9wnqhczy": "2025–2026",
    "sh/mtwrmxg7": "Dans un aéroport, le WAN relie l’enregistrement, la sûreté, les bagages et les communications. Une coupure réseau devient rapidement un risque opérationnel.",
    "sh/nu58f2hs": "27 sites · 864 incidents",
    "sh/wjy9sry9": "L’historique de maintenance constitue une base commune pour mesurer l’exposition et prioriser les vérifications.",
    "sh/xk7qlczu": "Pourquoi être proactif ?",
    "sh/ahwrqhgj": "Identifier les sites à vérifier avant la prochaine coupure.",
    "sh/bip8jmho": "OBJECTIF",
    "sh/65kfmpor": "ONDA · RISK INTELLIGENCE",
  },
  3: {
    "sh/n2l4fq98": "UNE VISION",
    "sh/m1c3mlsn": "INTÉGRÉE",
    "sh/943mhgre": "DU RISQUE À LA DÉFENSE",
    "sh/83ulovat": "Le projet réunit prévision WAN, prévention des erreurs humaines et simulation défensive dans un cycle unique : prédire, préparer, simuler, détecter et capitaliser.",
    "sh/v6l4jq94": "Prédire le risque",
    "sh/a5c3ql8z": "Préparer l’intervention",
    "sh/x8nml0ra": "Score 0–100 · alerte à 30 jours",
    "sh/w7ulsvqp": "Checklist · REX · actions priorisées",
    "sh/f29gbyx0": "ONDA · RISK INTELLIGENCE",
  },
  4: {
    "sh/kbm987y5": "ARCHITECTURE",
    "sh/5cva1cfq": "ONDA + CYBERRANGE",
    "sh/i94r6xgz": "PRINCIPE D’ISOLATION",
    "sh/jadsz2xk": "Deux espaces complémentaires : la plateforme pilote les risques réels ; le laboratoire valide les scénarios de détection et de remédiation sans exposer la production.",
    "sh/w72947yt": "Plateforme ONDA",
    "sh/x8vaxsfe": "Dashboards, scoring, alertes, prévention et REX.",
    "sh/a5kr2xg3": "Laboratoire isolé",
    "sh/v6tsv2xo": "Tester avant d’agir",
    "sh/g36tgryd": "Les traces issues du CyberRange — réseau, capture, analyse et règles — rendent la décision défensive vérifiable et réutilisable.",
    "sh/3ytsrmpw": "ONDA · RISK INTELLIGENCE",
  },
  5: {
    "sh/ahkvi1cb": "RISQUE",
    "sh/v2twb6dw": "PRÉDICTIF",
    "sh/k7mxovud": "MODÈLE MACHINE LEARNING",
    "sh/58vehgvy": "Comment le score est construit",
    "sh/i54fmlc7": "Le modèle exploite les incidents, leur récence, la durée d’indisponibilité, les catégories de panne et l’opérateur afin d’estimer le risque sur les 30 prochains jours.",
    "sh/j6dwfqds": "Exemple de priorité",
    "sh/sb6xsvu9": "CAS RÉEL",
    "sh/tcfel0vu": "Une aide à la décision",
    "sh/hgrmpwj2": "129-OUARZAZATE atteint 99,9/100 : 5 incidents sur 30 jours et 380,8 h d’indisponibilité sur 90 jours. L’équipe valide ensuite l’action.",
    "sh/pkr6tgjy": "ONDA · RISK INTELLIGENCE",
  },
  6: {
    "sh/yhg7epsj": "FACTEUR",
    "sh/zi98nu94": "HUMAIN & REX",
    "sh/87ipkzal": "PRÉVENIR L’ERREUR OPÉRATIONNELLE",
    "sh/w32twb6l": "Avant toute modification",
    "sh/v2tcn650": "Sauvegarder la configuration, vérifier l’intégrité du firmware, choisir une fenêtre de faible impact, notifier la DSI et préparer le rollback.",
    "sh/u1kbu1ov": "Après l’intervention",
    "sh/5svutgni": "Vérifier les services critiques, confirmer la connectivité et documenter le résultat.",
    "sh/47mt0b6x": "Prévention durable",
    "sh/j6dcr65c": "Le REX transforme un incident ou une erreur en règle de travail réutilisable par les équipes.",
    "sh/qpwnet0b": "ONDA · RISK INTELLIGENCE",
  },
  7: {
    "sh/a9ojq5kz": "PRÉVENTION",
    "sh/xcz2l03q": "PLAN · 30 JOURS",
    "sh/cbq1sv25": "ACTIONS PRIORISÉES",
    "sh/n6x0fqlo": "Vérifier l’alimentation UPS",
    "sh/25ojml43": "Cibler les sites dont la durée d’indisponibilité est critique.",
    "sh/p8fih03e": "Escalader l’opérateur",
    "sh/o761ov2t": "Documenter le lien instable et suivre le ticket Orange ou IAM.",
    "sh/f2d0b6lc": "Planifier une mission technique",
    "sh/eh4jil4r": "Associer score, historique et disponibilité des équipes.",
    "sh/id4ju1oz": "Renforcer la supervision",
    "sh/jedkn654": "Surveiller les sites récemment touchés jusqu’à stabilisation.",
    "sh/r2dkrq5g": "ONDA · RISK INTELLIGENCE",
  },
  8: {
    "sh/18byd4zy": "DÉTECTION",
    "sh/g72x4zyd": "& RÉPONSE",
    "sh/sjix0zy1": "Découvrir",
    "sh/je9g3ahk": "Nmap identifie les services visibles et prépare la cartographie du laboratoire.",
    "sh/m5gvmhwn": "Observer",
    "sh/n6pwfmd8": "Wireshark conserve les flux et la chronologie nécessaires à l’analyse.",
    "sh/zipwbmdc": "Qualifier",
    "sh/kfixwbe1": "Ghidra, YARA et Snort relient les indices techniques à une règle de détection.",
    "sh/5sne5wne": "ONDA · CYBERRANGE",
  },
  9: {
    "sh/2xsjepgb": "CULTURE",
    "sh/3y107axw": "DE RÉSILIENCE",
    "sh/cnu1kzyd": "APPRENDRE · DÉTECTER · AMÉLIORER",
    "sh/do3id4fy": "Former et simuler",
    "sh/qlcjipgn": "Des scénarios isolés entraînent les équipes à reconnaître les preuves utiles.",
    "sh/bml0buxs": "Responsabiliser",
    "sh/0ru1ozyp": "Les checklists et le REX rendent les contrôles visibles et transmissibles.",
    "sh/lsn2h4fa": "Ancrer le workflow",
    "sh/98ji147e": "Les preuves et les actions reviennent dans la prévention WAN.",
    "sh/hcji5o7a": "ONDA · RISK INTELLIGENCE",
  },
  10: {
    "sh/m1cnetkj": "BILAN",
    "sh/s7yt4b21": "",
    "sh/d87uxg3m": "ONDA · EMSI",
    "sh/q5gb21kb": "Valeur du projet",
    "sh/r6pcv6lw": "Anticiper les sites exposés avant la coupure.",
    "sh/0bit8b2d": "Relier prédiction, procédure et preuve technique.",
    "sh/1cru1g3y": "Pour aller plus loin",
    "sh/e9gb61k7": "Enrichir les données, suivre les actions jusqu’à leur clôture et recalibrer les seuils avec les équipes.",
    "sh/fapcz6ls": "Auteurs : Azzat Nouamane & Hnid Aimane\nEncadrement : Mme Jaouhari Ouafaa · Mme Khadija Bousmar",
    "sh/ozitcv29": "Projet ONDA · PFA 4IIR",
    "sh/bu5cnqd8": "ONDA · RISK INTELLIGENCE",
  },
};

const imageSlots = {
  1: ["sh/fu94fe98", ONDA("onda_overview.png"), "ONDA Risk Intelligence overview"],
  2: ["sh/x4r21kru", ONDA("onda_home.png"), "ONDA executive risk portal"],
  3: ["sh/obq90bml", CR("cr_architecture.png"), "Isolated CyberRange architecture"],
  4: ["sh/3ihk3et8", DIAGRAM("deployment_architecture.png"), "ONDA and CyberRange deployment architecture"],
  5: ["sh/l4bupwny", ONDA("onda_alerts.png"), "ONDA active risk alerts"],
  6: ["sh/pc76hkr2", ONDA("onda_human.png"), "ONDA human factor and REX module"],
  7: ["sh/fi9c369c", ONDA("onda_prevention.png"), "ONDA 30-day WAN prevention plan"],
  9: ["sh/ah8nu54b", CR("cr_remediation.png"), "CyberRange remediation evidence"],
  10: ["sh/725onyl4", DIAGRAM("solution_pipeline.png"), "Integrated ONDA risk and CyberRange workflow"],
};

const notes = {
  1: ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_overview.png"],
  2: ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_home.png"],
  3: ["Local project report: report/main.tex", "Local asset: report/images/cyberrange cr_architecture.png"],
  4: ["Local project report: report/main.tex", "Local asset: report/images/diagrams/deployment_architecture.png"],
  5: ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_alerts.png"],
  6: ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_human.png"],
  7: ["Local project report: report/main.tex", "Local asset: report/images/onda/onda_prevention.png"],
  8: ["Local project report: report/main.tex", "Local assets: report/images/cyberrange cr_nmap.png, cr_wireshark.png, cr_yara.png, cr_snort.png"],
  9: ["Local project report: report/main.tex", "Local asset: report/images/cyberrange cr_remediation.png"],
  10: ["Local project report: report/main.tex", "Local asset: report/images/diagrams/solution_pipeline.png"],
};

const presentation = await PresentationFile.importPptx(await FileBlob.load(STARTER));
const layouts = new Map();
for (let sourceSlide = 1; sourceSlide <= 10; sourceSlide += 1) {
  layouts.set(sourceSlide, await layoutFor(sourceSlide));
}

for (let outputSlide = 1; outputSlide <= 10; outputSlide += 1) {
  const slide = presentation.slides.items[outputSlide - 1];
  const layout = layouts.get(outputSlide);
  await rewrite(slide, layout, copy[outputSlide]);
  if (outputSlide === 1) {
    await replaceCoverImage(slide);
    clearShapeFill(slide, layout, "sh/fu94fe98");
    slide.images.add({
      blob: await blob(ONDA("onda_overview.png")),
      contentType: "image/png",
      alt: "ONDA Risk Intelligence overview",
      fit: "cover",
      position: { left: 700, top: 575, width: 525, height: 405 },
    });
    slide.images.add({
      blob: await blob(CR("emsi_logo.png")),
      contentType: "image/png",
      alt: "EMSI logo",
      fit: "contain",
      position: { left: 20, top: 20, width: 370, height: 99 },
    });
  } else if (imageSlots[outputSlide]) {
    const [shapeAid, imagePath, alt] = imageSlots[outputSlide];
    await replaceImageFill(slide, layout, shapeAid, imagePath, alt);
  }
  note(slide, notes[outputSlide]);
}

await fs.mkdir(path.dirname(OUT), { recursive: true });
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUT);
console.log(`Created ${OUT}`);
console.log(`Slides ${presentation.slides.items.length}`);
