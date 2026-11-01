import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const file = process.argv[2];
const presentation = await PresentationFile.importPptx(await FileBlob.load(file));
const slideNumber = Number(process.argv[4] || 2);
const slide = presentation.slides.items[slideNumber - 1];
const layout = JSON.parse(await fs.readFile(process.argv[3], "utf8"));
const textIndex = layout.elements.findIndex((element) => element.textPreview === "CYBERSECURITY");
const imageIndex = layout.elements.findIndex((element) => element.aid === "sh/8zeh8rqt");
const shape = slide.shapes.items[textIndex];
const imgShape = slide.shapes.items[imageIndex];
console.log(JSON.stringify({
  slideCount: presentation.slides.items.length,
  textIndex,
  textAid: shape?.aid,
  textKeys: Object.keys(shape ?? {}),
  textValue: shape?.text,
  textFrame: shape?.frame,
  imageIndex,
  imageAid: imgShape?.aid,
  imageKeys: Object.keys(imgShape ?? {}),
  imageFrame: imgShape?.frame,
  imageFill: imgShape?.fill,
  slideKeys: Object.keys(slide ?? {}),
  shapes: slide.shapes.items.map((item, i) => ({i, aid: item.aid, text: typeof item.text === "string" ? item.text : String(item.text ?? ""), frame: item.frame})).slice(0, 25),
  images: slide.images.items.map((item, i) => ({i, aid: item.aid, alt: item.alt, frame: item.frame}))
}, null, 2));
