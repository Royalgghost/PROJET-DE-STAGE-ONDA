import fs from "node:fs/promises";
import path from "node:path";

const layoutDir = path.resolve(process.argv[2]);
const outputPath = path.resolve(process.argv[3]);
const names = (await fs.readdir(layoutDir))
  .filter((name) => /^source-slide-\d+\.layout\.json$/i.test(name))
  .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]));

const lines = [];
for (const name of names) {
  const slideNumber = Number(name.match(/\d+/)[0]);
  const layout = JSON.parse(await fs.readFile(path.join(layoutDir, name), "utf8"));
  const elements = Array.isArray(layout.elements) ? layout.elements : [];
  lines.push(JSON.stringify({
    slideNumber,
    elements: elements
      .filter((element) => element && element.aid)
      .map((element) => ({
        id: element.aid,
        text: element.textPreview ?? element.text ?? "",
        name: element.name ?? ""
      }))
  }));
}

await fs.writeFile(outputPath, `${lines.join("\n")}\n`, "utf8");
console.log(`Wrote ${lines.length} slide inventory records to ${outputPath}`);
