import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const finalPath = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/report/Presentation_PFA_ONDA_CyberRange_Premium.pptx";
const outDir = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/presentation_build/pfa_edit/premium-render";
await fs.mkdir(outDir, { recursive: true });
const p = await PresentationFile.importPptx(await FileBlob.load(finalPath));
console.log("slides", p.slides.items.length);
for (const slide of p.slides.items) {
  const png = await slide.export({ format: "png", scale: 1 });
  await fs.writeFile(`${outDir}/slide-${String(slide.index + 1).padStart(2, "0")}.png`, new Uint8Array(await png.arrayBuffer()));
}
const montage = await p.export({ format: "png", montage: { columns: 4, slideWidth: 420, padding: 18, gap: 18, background: "#202020" }, scale: 1 });
await fs.writeFile(`${outDir}/montage.png`, new Uint8Array(await montage.arrayBuffer()));
const snapshot = await p.inspect({ kind: "slide,textbox,image,notes", maxChars: 30000 });
await fs.writeFile(`${outDir}/inspect.ndjson`, snapshot.ndjson ?? String(snapshot));
