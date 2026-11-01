import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const deckPath = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/report/Presentation_PFA_ONDA_CyberRange_Complet_Gantt_Corrige_v2.pptx";
const outputDir = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/presentation_build/pfa_edit/gantt-corrected-render";
await fs.mkdir(outputDir, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(deckPath));
const slide23 = presentation.slides.items[22];
const rendered = await slide23.export({ format: "png", scale: 1 });
await fs.writeFile(`${outputDir}/slide-23.png`, new Uint8Array(await rendered.arrayBuffer()));
const montage = await presentation.export({ format: "png", montage: { columns: 4, slideWidth: 420, padding: 18, gap: 18, background: "#202020" }, scale: 1 });
await fs.writeFile(`${outputDir}/montage.png`, new Uint8Array(await montage.arrayBuffer()));
const snapshot = await presentation.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 20000 });
await fs.writeFile(`${outputDir}/inspect.ndjson`, snapshot.ndjson ?? String(snapshot));
console.log(`slides=${presentation.slides.items.length}`);
console.log(`slide23=${outputDir}/slide-23.png`);
