import fs from "node:fs/promises";
import sharp from "sharp";

const outputPath = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/report/images/cyberrange/cr_gantt.png";

const W = 6000;
const H = 2600;
const x0 = 1050;
const x1 = 5850;
const plotWidth = x1 - x0;
const startMs = Date.UTC(2026, 6, 15);
const endMs = Date.UTC(2026, 8, 2);
const dayMs = 24 * 60 * 60 * 1000;

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function dateMs(iso) {
  const [year, month, day] = iso.split("-").map(Number);
  return Date.UTC(year, month - 1, day);
}

function xFor(iso) {
  return x0 + ((dateMs(iso) - startMs) / (endMs - startMs)) * plotWidth;
}

function taskEndX(iso) {
  return xFor(iso) + ((dayMs / (endMs - startMs)) * plotWidth);
}

function text(x, y, value, size, options = {}) {
  const {
    fill = "#1a1a1a",
    weight = 400,
    anchor = "start",
    family = "Arial, Helvetica, sans-serif",
    opacity = 1,
  } = options;
  return `<text x="${x}" y="${y}" font-family="${family}" font-size="${size}px" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}" opacity="${opacity}">${escapeXml(value)}</text>`;
}

function multiline(x, y, lines, size, options = {}) {
  const {
    fill = "#1a1a1a",
    weight = 400,
    anchor = "start",
    lineHeight = Math.round(size * 1.15),
  } = options;
  const tspans = lines.map((line, index) => `<tspan x="${x}" dy="${index === 0 ? 0 : lineHeight}">${escapeXml(line)}</tspan>`).join("");
  return `<text x="${x}" y="${y}" font-family="Arial, Helvetica, sans-serif" font-size="${size}px" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}">${tspans}</text>`;
}

const workPackages = [
  {
    label: ["WP1 Cadrage et", "Architecture de Confinement"],
    tasks: [
      ["T1.1", "2026-07-15", "2026-07-18", "Analyse de l’état de l’art et étude théorique (Azzat et Hnid)", false],
      ["T1.2", "2026-07-18", "2026-07-20", "Rédaction aspects validation du cahier (Azzat et Hnid)", false],
      ["T1.3", "2026-07-20", "2026-07-24", "Déploiement et routage réseau Host-Only / VM (Azzat)", true],
    ],
  },
  {
    label: ["WP2 Opérations Offensives", "et Reconnaissance active"],
    tasks: [
      ["T2.1", "2026-07-24", "2026-07-28", "Balayage des ports et bannières Nmap (Azzat)", false],
      ["T2.2", "2026-07-28", "2026-08-01", "Exploitation de la cible backdoor vsftpd 2.3.4 (Azzat)", false],
      ["T2.3", "2026-08-01", "2026-08-07", "Exploitation par injection de commandes Samba 3.0.20 (Azzat)", false],
    ],
  },
  {
    label: ["WP3 Payload Engineering", "et Reverse Engineering"],
    tasks: [
      ["T3.1", "2026-08-07", "2026-08-11", "Pivot distant sur Java RMI et configuration du canal C2 (Azzat)", false],
      ["T3.2", "2026-08-11", "2026-08-16", "Génération, compilation et extraction du payload (Hnid)", true],
      ["T3.3", "2026-08-16", "2026-08-23", "Analyse statique du graphe d’appels et décompilation Ghidra (Hnid)", true],
    ],
  },
  {
    label: ["WP4 Ingénierie de Détection,", "Remédiation et Défense"],
    tasks: [
      ["T4.1", "2026-08-23", "2026-08-26", "Analyse comportementale réseau et signatures Snort (Hnid)", false],
      ["T4.2", "2026-08-26", "2026-08-29", "Modélisation et tests de détection heuristique avec YARA (Hnid)", true],
    ],
  },
  {
    label: ["WP5 Clôture du Projet", "et Restitution"],
    tasks: [
      ["T5.1", "2026-08-29", "2026-09-01", "Rédaction des chapitres techniques et intégration LaTeX (Azzat et Hnid)", false],
      ["T5.2", "2026-08-30", "2026-09-01", "Création des supports visuels et simulations orales (Azzat et Hnid)", false],
    ],
  },
];

const gridDates = [
  ["2026-07-15", "15-Juil"],
  ["2026-07-22", "22-Juil"],
  ["2026-07-29", "29-Juil"],
  ["2026-08-05", "05-Août"],
  ["2026-08-12", "12-Août"],
  ["2026-08-19", "19-Août"],
  ["2026-08-26", "26-Août"],
  ["2026-09-01", "01-Sept"],
];

const svg = [];
svg.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
svg.push(`<rect width="${W}" height="${H}" fill="#ffffff"/>`);
svg.push(text(W / 2, 90, "Diagramme de Gantt - PFA CyberRange", 64, { weight: 700, anchor: "middle" }));
svg.push(text(W / 2, 155, "Période réelle : 15/07/2026 – 01/09/2026    ·    Charge estimée : 37 J-H", 38, { fill: "#444444", anchor: "middle" }));

for (const [iso, label] of gridDates) {
  const x = xFor(iso);
  svg.push(`<line x1="${x}" y1="260" x2="${x}" y2="2240" stroke="#6f6f6f" stroke-width="4"/>`);
  svg.push(text(x, 2320, label, 38, { fill: "#4c4c4c", anchor: "middle" }));
}
svg.push(`<line x1="${x0}" y1="260" x2="${x0}" y2="2240" stroke="#6f6f6f" stroke-width="4"/>`);
svg.push(`<line x1="${xFor("2026-09-02")}" y1="260" x2="${xFor("2026-09-02")}" y2="2240" stroke="#6f6f6f" stroke-width="4"/>`);
svg.push(text(x0 - 35, 305, "Lot / tâches", 38, { weight: 700, anchor: "end" }));

const rowTop = 350;
const rowHeight = 380;
const taskHeight = 60;
const taskGap = 100;
for (let row = 0; row < workPackages.length; row += 1) {
  const y = rowTop + row * rowHeight;
  if (row % 2 === 1) svg.push(`<rect x="30" y="${y - 55}" width="${W - 60}" height="${rowHeight - 8}" fill="#fafbff"/>`);
  svg.push(multiline(40, y + 95, workPackages[row].label, 36, { weight: 700, lineHeight: 44 }));
  for (let taskIndex = 0; taskIndex < workPackages[row].tasks.length; taskIndex += 1) {
    const [code, start, end, label, critical] = workPackages[row].tasks[taskIndex];
    const barX = xFor(start);
    const barW = Math.max(42, taskEndX(end) - barX);
    const barY = y + taskIndex * taskGap;
    const fill = critical ? "#ff1d1d" : "#e9e9fb";
    const stroke = critical ? "#ff1d1d" : "#b7b7b7";
    svg.push(`<rect x="${barX}" y="${barY}" width="${barW}" height="${taskHeight}" rx="8" fill="${fill}" stroke="${stroke}" stroke-width="5"/>`);
    const labelWidthEstimate = label.length * 18;
    const availableRight = x1 - (barX + barW) - 30;
    if (availableRight > Math.min(1700, labelWidthEstimate)) {
      svg.push(text(barX + barW + 16, barY + 42, `${code} ${label}`, 31, { fill: "#2a2a2a" }));
    } else {
      svg.push(text(barX - 16, barY + 42, `${code} ${label}`, 31, { fill: "#2a2a2a", anchor: "end" }));
    }
  }
}

svg.push(`<line x1="30" y1="2240" x2="${W - 30}" y2="2240" stroke="#bdbdbd" stroke-width="3"/>`);
svg.push(`<rect x="80" y="2460" width="48" height="32" rx="5" fill="#ff1d1d"/>`);
svg.push(text(145, 2490, "Tâche critique", 34, { fill: "#444444" }));
svg.push(`<rect x="500" y="2460" width="48" height="32" rx="5" fill="#e9e9fb" stroke="#b7b7b7" stroke-width="3"/>`);
svg.push(text(565, 2490, "Tâche planifiée", 34, { fill: "#444444" }));
svg.push(text(W - 80, 2490, "Les lots CyberRange couvrent la période réelle du 15 juillet au 1er septembre 2026.", 34, { fill: "#444444", anchor: "end" }));
svg.push("</svg>");

await sharp(Buffer.from(svg.join(""))).png().toFile(outputPath);
console.log(`Updated ${outputPath}`);
