import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "C:/Users/nouam/Downloads/ONDA_Projet_Sauvegarde";
const sourcePath = "C:/Users/nouam/Downloads/Presentation_PFA_ONDA_CyberRange_Complet.pptx";
const replacementPath = path.join(workspaceDir, "report", "images", "cyberrange", "cr_gantt.png");
const finalPath = path.join(workspaceDir, "report", "Presentation_PFA_ONDA_CyberRange_Complet_Gantt_Corrige_v2.pptx");
const stagingDir = path.join(workspaceDir, ".codex-finalizer");
const skillDir = "C:/Users/nouam/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/Presentations";
const runtimePython = "C:/Users/nouam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";

const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
if (presentation.slides.items.length !== 24) {
  throw new Error(`Unexpected source slide count: ${presentation.slides.items.length}`);
}

const slide23 = presentation.slides.items[22];
const ganttImage = presentation.resolve("im/twvmpw7q");
if (!ganttImage) {
  throw new Error("Could not resolve the Gantt image on slide 23.");
}

const oldFrame = ganttImage.frame;
const oldCrop = ganttImage.crop;
const oldFit = ganttImage.fit;
const oldAlt = ganttImage.alt;
const oldGeometry = ganttImage.geometry;
const oldBorderRadius = ganttImage.borderRadius;
const oldRotation = ganttImage.rotation;
const oldFlipHorizontal = ganttImage.flipHorizontal;
const oldFlipVertical = ganttImage.flipVertical;
const oldLockAspectRatio = ganttImage.lockAspectRatio;
const replacementBytes = await fs.readFile(replacementPath);

ganttImage.replace({
  blob: replacementBytes,
  contentType: "image/png",
  alt: oldAlt ?? "Diagramme de Gantt CyberRange, période du 15 juillet au 1er septembre 2026",
  ...(oldFit ? { fit: oldFit } : {}),
});
ganttImage.frame = oldFrame;
ganttImage.crop = oldCrop;
ganttImage.geometry = oldGeometry;
ganttImage.borderRadius = oldBorderRadius;
ganttImage.rotation = oldRotation;
ganttImage.flipHorizontal = oldFlipHorizontal;
ganttImage.flipVertical = oldFlipVertical;
ganttImage.lockAspectRatio = oldLockAspectRatio;
ganttImage.frame = { left: 916, top: 360, width: 868, height: 400 };

await fs.mkdir(stagingDir, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });
const candidatePath = path.join(stagingDir, "Presentation_PFA_ONDA_CyberRange_Complet_Gantt_Corrige_v2.candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href);
const result = await finalizePresentation({
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "18288000,10287000", "--validate-bullet-geometry", "--validate-heading-fit"],
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "Presentation_PFA_ONDA_CyberRange_Complet_Gantt_Corrige_v2.validation.json"),
});
console.log(JSON.stringify(result, null, 2));
console.log(`Created ${finalPath}`);
