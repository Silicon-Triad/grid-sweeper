"""Fill the group members into the grading rubric (REQ-RPT-10, issue #30).

The rubric sheet is the report's title page (spec §8.2). The names are drawn
on top of the frozen spec PDF, which is read but never changed (AGENTS.md).
Members, roll numbers and order come from docs/plan.md §1. Usage:

    python tools/fill_rubric.py   # writes report/latex/figures/rubric_filled.pdf
"""

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
RUBRIC = ROOT / "docs" / "spec" / "CS-323_AI_CEP_Grading_Rubric.pdf"
OUT = ROOT / "report" / "latex" / "figures" / "rubric_filled.pdf"

# (name, roll no.) for S1…S4, in roll-number order.
MEMBERS = [
    ("Muhammad Ashar Khan", "CS-24035"),
    ("Huzaifa Hanif", "CS-24039"),
    ("Muhammad Ahmed Qazi", "CS-24045"),
    ("Mujtaba Jawaid Rao", "CS-24047"),
]

# Column centres (x) and row baselines (y from the top), in PDF points,
# measured with `pdftotext -bbox` on the rubric: S1/S2 left, S3/S4 right.
NAME_X = (288.0, 607.0)
ROLL_X = (411.5, 722.0)
ROW_Y = (154.0, 167.0)


def overlay(height: float, width: float) -> PdfReader:
    """Draw the member names and roll numbers on a blank page of the rubric's size.

    Args:
        height: Page height in points.
        width: Page width in points.

    Returns:
        A one-page PDF holding only the text.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    c.setFont("Times-Roman", 9)
    for i, (name, roll) in enumerate(MEMBERS):
        side, row = divmod(i, 2)
        y = height - ROW_Y[row]
        c.drawCentredString(NAME_X[side], y, name)
        c.drawCentredString(ROLL_X[side], y, roll)
    c.save()
    buf.seek(0)
    return PdfReader(buf)


def main() -> None:
    """Write the filled rubric next to the LaTeX report."""
    page = PdfReader(RUBRIC).pages[0]
    box = page.mediabox
    page.merge_page(overlay(float(box.height), float(box.width)).pages[0])
    writer = PdfWriter()
    writer.add_page(page)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("wb") as f:
        writer.write(f)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
