"""Extract images from report-2.pdf.

Produces two folders next to the PDF:
  - embedded_images/  raw images embedded in the PDF (best quality, original assets)
  - page_renders/     full-page PNGs at 200 DPI (use if figures are vector/multi-part)
"""

from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
PDF_PATH = HERE / "report-2.pdf"
EMBEDDED_DIR = HERE / "embedded_images"
RENDER_DIR = HERE / "page_renders"
RENDER_DPI = 200


def extract_embedded(doc: pymupdf.Document) -> int:
    EMBEDDED_DIR.mkdir(exist_ok=True)
    seen: set[int] = set()
    count = 0
    for page_index in range(doc.page_count):
        page = doc[page_index]
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            pix = pymupdf.Pixmap(doc, xref)
            if pix.n - pix.alpha >= 4:  # CMYK/other -> convert to RGB
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            out = EMBEDDED_DIR / f"p{page_index + 1:02d}_x{xref}.png"
            pix.save(out)
            count += 1
    return count


def render_pages(doc: pymupdf.Document) -> int:
    RENDER_DIR.mkdir(exist_ok=True)
    matrix = pymupdf.Matrix(RENDER_DPI / 72, RENDER_DPI / 72)
    for page_index in range(doc.page_count):
        pix = doc[page_index].get_pixmap(matrix=matrix)
        pix.save(RENDER_DIR / f"page_{page_index + 1:02d}.png")
    return doc.page_count


def main() -> None:
    doc = pymupdf.open(PDF_PATH)
    n_embedded = extract_embedded(doc)
    n_pages = render_pages(doc)
    print(f"Extracted {n_embedded} embedded image(s) -> {EMBEDDED_DIR}")
    print(f"Rendered {n_pages} page(s) -> {RENDER_DIR}")


if __name__ == "__main__":
    main()
