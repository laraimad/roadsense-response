from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "RoadSense_Response_Documentation.pdf"
PAGE_W, PAGE_H = A4

INK = HexColor("#10201B")
GREEN = HexColor("#236C4D")
DARK = HexColor("#143F31")
LIME = HexColor("#C8F45D")
MUTED = HexColor("#69766F")
PAPER = HexColor("#F5F7F3")
LINE = HexColor("#DCE3DC")
WHITE = HexColor("#FFFFFF")


def paragraph(c: canvas.Canvas, text: str, x: float, y: float, width: float, style: ParagraphStyle) -> float:
    item = Paragraph(text, style)
    _, height = item.wrap(width, PAGE_H)
    item.drawOn(c, x, y - height)
    return y - height


def footer(c: canvas.Canvas, page: int) -> None:
    c.setStrokeColor(LINE)
    c.line(18 * mm, 14 * mm, PAGE_W - 18 * mm, 14 * mm)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, 9.5 * mm, "RoadSense Response - Shortcut Asia Internship Challenge 2026")
    c.drawRightString(PAGE_W - 18 * mm, 9.5 * mm, f"Page {page} of 2")


def title_block(c: canvas.Canvas, kicker: str, title: str, subtitle: str) -> float:
    c.setFillColor(DARK)
    c.rect(0, PAGE_H - 70 * mm, PAGE_W, 70 * mm, fill=1, stroke=0)
    c.setFillColor(LIME)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(18 * mm, PAGE_H - 19 * mm, kicker.upper())
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(18 * mm, PAGE_H - 35 * mm, title)
    style = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=10, leading=15, textColor=HexColor("#CBD6D0"))
    paragraph(c, subtitle, 18 * mm, PAGE_H - 43 * mm, 150 * mm, style)
    return PAGE_H - 80 * mm


def section_label(c: canvas.Canvas, text: str, x: float, y: float) -> None:
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, text.upper())


def card(c: canvas.Canvas, x: float, y: float, w: float, h: float, number: str, title: str, body: str) -> None:
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - h, w, h, 4 * mm, fill=1, stroke=1)
    c.setFillColor(LIME)
    c.circle(x + 11 * mm, y - 12 * mm, 5 * mm, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + 11 * mm, y - 14 * mm, number)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 20 * mm, y - 11 * mm, title)
    style = ParagraphStyle("card", fontName="Helvetica", fontSize=8.5, leading=12, textColor=MUTED)
    paragraph(c, body, x + 8 * mm, y - 22 * mm, w - 16 * mm, style)


def flow_box(c: canvas.Canvas, x: float, y: float, w: float, title: str, caption: str) -> None:
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.roundRect(x, y - 22 * mm, w, 22 * mm, 3 * mm, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + w / 2, y - 8 * mm, title)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawCentredString(x + w / 2, y - 14 * mm, caption)


def arrow(c: canvas.Canvas, x1: float, y: float, x2: float) -> None:
    c.setStrokeColor(GREEN)
    c.setFillColor(GREEN)
    c.setLineWidth(1.3)
    c.line(x1, y, x2, y)
    c.line(x2, y, x2 - 2.3 * mm, y + 1.8 * mm)
    c.line(x2, y, x2 - 2.3 * mm, y - 1.8 * mm)


def bullet_list(c: canvas.Canvas, items: list[str], x: float, y: float, width: float) -> float:
    style = ParagraphStyle("bullet", fontName="Helvetica", fontSize=8.6, leading=12.3, textColor=INK, leftIndent=9, firstLineIndent=-7)
    for item in items:
        y = paragraph(c, f"<font color='#236C4D'><b>+</b></font>&nbsp;&nbsp;{item}", x, y, width, style) - 2.2 * mm
    return y


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("RoadSense Response Documentation")

    body = ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=13.2, textColor=INK, alignment=TA_LEFT)
    small = ParagraphStyle("small", fontName="Helvetica", fontSize=8.2, leading=12, textColor=MUTED)

    y = title_block(
        c,
        "Product documentation",
        "RoadSense Response",
        "An explainable incident triage and repair workflow built as a standalone product layer for a pothole-detection FYP.",
    )
    section_label(c, "Problem and approach", 18 * mm, y)
    y = paragraph(c, "Vehicle detection can create hundreds of images and sensor events, but detection alone does not repair a road. RoadSense Response helps an operator understand uncertain evidence, decide what needs attention, and hand the work to a repair team.", 18 * mm, y - 5 * mm, 174 * mm, body)
    y = paragraph(c, "The prototype goes deep on two features: <b>evidence-based incident triage</b> and a <b>persistent repair workflow</b>. It uses prepared demo records and copied screenshots, while remaining independent from the original FYP source, models, labels, logs, configuration, and live hardware.", 18 * mm, y - 3 * mm, 174 * mm, body)

    y -= 8 * mm
    section_label(c, "Two focused features", 18 * mm, y)
    card(c, 18 * mm, y - 5 * mm, 84 * mm, 42 * mm, "1", "Triage", "Searchable map and severity queue, camera evidence, visual confidence, impact strength, recurrence, and a recommended action.")
    card(c, 108 * mm, y - 5 * mm, 84 * mm, 42 * mm, "2", "Respond", "Verify, assign a team, update repair status, preserve audit history, dismiss false positives, and export CSV.")

    flow_y = y - 58 * mm
    section_label(c, "Architecture", 18 * mm, flow_y)
    box_y = flow_y - 7 * mm
    box_w = 37 * mm
    gap = 7 * mm
    labels = [("Web UI", "Responsive browser"), ("Flask API", "REST endpoints"), ("JSON store", "Isolated state"), ("CSV export", "Repair queue")]
    for index, (title, caption) in enumerate(labels):
        x = 18 * mm + index * (box_w + gap)
        flow_box(c, x, box_y, box_w, title, caption)
        if index < len(labels) - 1:
            arrow(c, x + box_w + 1 * mm, box_y - 11 * mm, x + box_w + gap - 1 * mm)

    tech_y = box_y - 33 * mm
    section_label(c, "Tech stack", 18 * mm, tech_y)
    c.setFillColor(PAPER)
    c.roundRect(18 * mm, tech_y - 25 * mm, 174 * mm, 20 * mm, 3 * mm, fill=1, stroke=0)
    items = ["Python 3", "Flask", "HTML/CSS", "Vanilla JavaScript", "JSON", "unittest"]
    x = 24 * mm
    for item in items:
        width = stringWidth(item, "Helvetica-Bold", 8) + 9 * mm
        c.setFillColor(WHITE)
        c.roundRect(x, tech_y - 19 * mm, width, 9 * mm, 4.5 * mm, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + width / 2, tech_y - 16 * mm, item)
        x += width + 3 * mm

    footer(c, 1)
    c.showPage()

    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.rect(0, PAGE_H - 34 * mm, PAGE_W, 34 * mm, fill=1, stroke=0)
    c.setFillColor(LIME)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(18 * mm, PAGE_H - 15 * mm, "DECISIONS, FLOW, AND LEARNING")
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(18 * mm, PAGE_H - 25 * mm, "How the product was shaped")

    y = PAGE_H - 46 * mm
    section_label(c, "Main technical decisions", 18 * mm, y)
    y = bullet_list(c, [
        "Flask and vanilla JavaScript keep reviewer setup fast and match the stack I can explain confidently.",
        "Explainability comes before automation: each priority exposes visual, impact, and recurrence evidence.",
        "Atomic local JSON persistence and timestamped history prove the workflow without production infrastructure.",
        "A relative map avoids API keys and keeps the demo reliable offline.",
        "Authentication, live ingestion, and municipal integrations were deferred to protect the two core workflows.",
    ], 18 * mm, y - 6 * mm, 174 * mm)

    flow_y = y - 3 * mm
    section_label(c, "Operator flow", 18 * mm, flow_y)
    box_y = flow_y - 7 * mm
    flow_labels = [("Detect", "Vehicle evidence"), ("Prioritize", "Score and group"), ("Verify", "Human decision"), ("Respond", "Assign and close")]
    for index, (title, caption) in enumerate(flow_labels):
        x = 18 * mm + index * (box_w + gap)
        flow_box(c, x, box_y, box_w, title, caption)
        if index < len(flow_labels) - 1:
            arrow(c, x + box_w + 1 * mm, box_y - 11 * mm, x + box_w + gap - 1 * mm)

    y = box_y - 34 * mm
    section_label(c, "Challenges and learning", 18 * mm, y)
    y = paragraph(c, "The central design challenge was showing uncertain AI and sensor signals without implying that the severity score is a validated engineering measurement. The interface keeps a human in the loop, shows the underlying evidence, and supports dismissal of false positives. The second challenge was protecting the academic project, solved through a self-contained app and prepared demo data.", 18 * mm, y - 5 * mm, 174 * mm, body)

    y -= 8 * mm
    section_label(c, "What I would improve next", 18 * mm, y)
    y = bullet_list(c, [
        "Authenticated operator and repair-crew roles with an audit trail.",
        "A spatial database, real map, and route-level clustering.",
        "Mobile updates with before-and-after repair photos.",
        "API ingestion from the detection device instead of prepared demo records.",
        "Field validation against road-condition measurements and maintenance outcomes.",
    ], 18 * mm, y - 6 * mm, 174 * mm)

    c.setFillColor(LIME)
    c.roundRect(18 * mm, 28 * mm, 174 * mm, 25 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, 43 * mm, "Outcome")
    paragraph(c, "RoadSense Response turns a detection project into an operational product: understand the evidence, make a decision, and close the repair loop.", 25 * mm, 39 * mm, 154 * mm, small)

    footer(c, 2)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
