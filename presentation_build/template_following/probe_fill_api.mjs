import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const presentation = await PresentationFile.importPptx(await FileBlob.load(process.argv[2]));
const slide = presentation.slides.items[2];
const frameShape = slide.shapes.items[2];
const originalFill = frameShape.fill;
const bytes = await fs.readFile(process.argv[3]);
const added = slide.images.add({
  blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
  contentType: "image/png",
  alt: "probe",
  fit: "cover",
  position: { left: 700, top: 500, width: 400, height: 300 },
});
console.log(JSON.stringify({
  shapeAid: frameShape.aid,
  shapeFrame: frameShape.frame,
  fillKeys: Object.keys(originalFill ?? {}),
  fillType: originalFill?.type,
  fillImageReference: originalFill?.imageReference,
  addedKeys: Object.keys(added ?? {}),
  addedId: added?.id,
  addedAid: added?.aid,
  addedData: added?.data,
  addedFrame: added?.frame,
}, null, 2));
console.log("ADDED_DATA_JSON", JSON.stringify(added.data));
