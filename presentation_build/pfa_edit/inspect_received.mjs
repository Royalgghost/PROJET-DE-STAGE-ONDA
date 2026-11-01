import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const sourcePath = "C:/Users/nouam/Downloads/Presentation_PFA_ONDA_CyberRange_Complet.pptx";
const outDir = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/presentation_build/pfa_edit/received-render";
await fs.mkdir(outDir, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
console.log("slides", presentation.slides.items.length);
const snapshot = await presentation.inspect({ kind: "slide,textbox,shape,image,table,chart,notes,layout", maxChars: 80000 });
await fs.writeFile(`${outDir}/inspect.ndjson`, snapshot.ndjson ?? String(snapshot));
console.log(snapshot.ndjson ?? snapshot);
for (const slide of presentation.slides.items) {
  const rendered = await slide.export({ format: "png", scale: 1 });
  await fs.writeFile(`${outDir}/slide-${String(slide.index + 1).padStart(2, "0")}.png`, new Uint8Array(await rendered.arrayBuffer()));
}
const montage = await presentation.export({ format: "png", montage: { columns: 4, slideWidth: 420, padding: 18, gap: 18, background: "#202020" }, scale: 1 });
await fs.writeFile(`${outDir}/montage.png`, new Uint8Array(await montage.arrayBuffer()));
