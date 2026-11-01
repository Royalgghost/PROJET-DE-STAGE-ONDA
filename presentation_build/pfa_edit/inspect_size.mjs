import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const p = await PresentationFile.importPptx(await FileBlob.load("C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde/presentation_build/pfa_edit/source-Presentation-PFA.pptx"));
console.log(p.slides.items[0].frame);
console.log(Object.keys(p.toProto() ?? {}));
console.log(JSON.stringify(p.toProto(), null, 2).slice(0, 1200));
