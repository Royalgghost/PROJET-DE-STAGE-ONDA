import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const sourcePath = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/presentation_build/pfa_edit/source-Presentation-PFA.pptx";
const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
console.log("slides", presentation.slides.items.length);
console.log("inspect");
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 50000,
});
await fs.writeFile("C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/presentation_build/pfa_edit/source-inspect.ndjson", snapshot.ndjson ?? String(snapshot));
console.log(snapshot.ndjson ?? snapshot);
for (const slide of presentation.slides.items) {
  const rendered = await slide.export({ format: "png", scale: 1 });
  await fs.writeFile(`C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/presentation_build/pfa_edit/source-slide-${String(slide.index+1).padStart(2,"0")}.png`, new Uint8Array(await rendered.arrayBuffer()));
}
