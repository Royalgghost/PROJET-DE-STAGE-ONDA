from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


BASE_DIR = Path(r"C:\Users\nouam\Downloads\ONDA_Projet_Sauvegarde")
SOURCE_PDF = Path(r"C:\Users\nouam\Downloads\Rapport de stage Azzat Nouamane et Hnid Aimane.pdf")
QR_IMAGE = Path(r"C:\Users\nouam\AppData\Local\Temp\codex-clipboard-f9b465f5-3a8e-491f-880d-412542859195.png")
OVERLAY_PDF = BASE_DIR / "tmp" / "pdfs" / "qr-overlay.pdf"
OUTPUT_PDF = BASE_DIR / "output" / "pdf" / "Rapport_de_stage_Azzat_Nouamane_Hnid_Aimane_avec_QR.pdf"


def create_overlay(width: float, height: float) -> None:
    OVERLAY_PDF.parent.mkdir(parents=True, exist_ok=True)
    qr_size = 62
    qr_x = (width - qr_size) / 2
    qr_y = 154

    pdf = canvas.Canvas(str(OVERLAY_PDF), pagesize=(width, height))
    pdf.drawImage(
        ImageReader(str(QR_IMAGE)),
        qr_x,
        qr_y,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    pdf.save()


def main() -> None:
    if not SOURCE_PDF.exists():
        raise FileNotFoundError(SOURCE_PDF)
    if not QR_IMAGE.exists():
        raise FileNotFoundError(QR_IMAGE)

    reader = PdfReader(str(SOURCE_PDF))
    if not reader.pages:
        raise ValueError("Le PDF source ne contient aucune page.")
    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    create_overlay(width, height)

    overlay_reader = PdfReader(str(OVERLAY_PDF))
    page.merge_page(overlay_reader.pages[0])

    writer = PdfWriter()
    for source_page in reader.pages:
        writer.add_page(source_page)
    if reader.metadata:
        writer.add_metadata({str(key): str(value) for key, value in reader.metadata.items() if value is not None})

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PDF.open("wb") as output:
        writer.write(output)

    print(f"Created: {OUTPUT_PDF}")
    print(f"Pages: {len(writer.pages)}")
    print(f"Page size: {width:.3f} x {height:.3f} pt")


if __name__ == "__main__":
    main()
