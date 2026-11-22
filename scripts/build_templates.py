"""Generate the five demo fillable PDF templates with ReportLab AcroForm."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from scripts.template_specs import ALL_TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
PAGE_W, PAGE_H = letter
MARGIN = 42
CONTENT_W = PAGE_W - 2 * MARGIN
GUTTER = 10
INK = Color(0.13, 0.16, 0.21)
MUTED = Color(0.40, 0.44, 0.50)
LINE = Color(0.78, 0.81, 0.85)
FIELD_BG = Color(0.965, 0.973, 0.988)


def _c(rgb, alpha=1.0):
    return Color(*rgb, alpha=alpha)


class FormBuilder:
    def __init__(self, spec: dict, out: Path):
        self.s = spec
        self.c = canvas.Canvas(str(out), pagesize=letter)
        self.c.setTitle(f"{spec['name']} - {spec['issuer']}")
        self.c.setAuthor(spec["issuer"] + " (fictional)")
        self.page = 0
        self.y = 0.0

    # ----- page furniture -------------------------------------------------
    def new_page(self):
        if self.page:
            self._footer()
            self.c.showPage()
        self.page += 1
        s, c = self.s, self.c
        brand, accent = _c(s["color"]), _c(s["accent"])
        if self.page == 1:
            if s["style"] == "band":
                c.setFillColor(brand); c.rect(0, PAGE_H - 92, PAGE_W, 92, stroke=0, fill=1)
                c.setFillColor(accent); c.rect(0, PAGE_H - 96, PAGE_W, 4, stroke=0, fill=1)
                c.setFillColor(white)
                c.setFont("Helvetica-Bold", 10); c.drawString(MARGIN, PAGE_H - 30, s["issuer"].upper())
                c.setFont("Helvetica-Bold", 19); c.drawString(MARGIN, PAGE_H - 58, s["name"])
                c.setFont("Helvetica", 8.5); c.drawString(MARGIN, PAGE_H - 76, s["form_no"])
                self.y = PAGE_H - 116
            elif s["style"] == "rail":
                c.setFillColor(brand); c.rect(0, 0, 14, PAGE_H, stroke=0, fill=1)
                c.setFillColor(accent); c.rect(14, 0, 3, PAGE_H, stroke=0, fill=1)
                c.setFillColor(brand); c.setFont("Helvetica-Bold", 9.5)
                c.drawString(MARGIN, PAGE_H - 38, s["issuer"].upper())
                c.setFillColor(INK); c.setFont("Helvetica-Bold", 20)
                c.drawString(MARGIN, PAGE_H - 64, s["name"])
                c.setFillColor(MUTED); c.setFont("Helvetica", 8.5)
                c.drawRightString(PAGE_W - MARGIN, PAGE_H - 38, s["form_no"])
                c.setStrokeColor(brand); c.setLineWidth(1.4)
                c.line(MARGIN, PAGE_H - 76, PAGE_W - MARGIN, PAGE_H - 76)
                self.y = PAGE_H - 96
            else:  # boxed
                c.setStrokeColor(brand); c.setLineWidth(2)
                c.rect(MARGIN, PAGE_H - 100, CONTENT_W, 64, stroke=1, fill=0)
                c.setFillColor(brand); c.rect(MARGIN, PAGE_H - 100, 120, 64, stroke=0, fill=1)
                c.setFillColor(white); c.setFont("Helvetica-Bold", 9)
                lines, cur = [], ""
                for word in s["issuer"].upper().split():
                    if len(cur) + len(word) > 12 and cur:
                        lines.append(cur); cur = word
                    else:
                        cur = (cur + " " + word).strip()
                lines.append(cur)
                for i, ln in enumerate(lines[:4]):
                    c.drawString(MARGIN + 10, PAGE_H - 50 - i * 11, ln)
                c.setFillColor(INK); c.setFont("Helvetica-Bold", 17)
                c.drawString(MARGIN + 134, PAGE_H - 66, s["name"])
                c.setFillColor(MUTED); c.setFont("Helvetica", 8.5)
                c.drawString(MARGIN + 134, PAGE_H - 84, s["form_no"])
                self.y = PAGE_H - 118
            c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 8.3)
            self._wrap(s["intro"], MARGIN, CONTENT_W, 11)
            self.y -= 6
        else:
            c.setFillColor(brand); c.setFont("Helvetica-Bold", 9)
            c.drawString(MARGIN, PAGE_H - 36, f"{s['issuer'].upper()}  |  {s['name']} (continued)")
            c.setStrokeColor(LINE); c.line(MARGIN, PAGE_H - 44, PAGE_W - MARGIN, PAGE_H - 44)
            self.y = PAGE_H - 64

    def _wrap(self, text, x, width, leading):
        words, line = text.split(), ""
        for w in words:
            trial = (line + " " + w).strip()
            if self.c.stringWidth(trial, "Helvetica-Oblique", 8.3) > width:
                self.c.drawString(x, self.y, line); self.y -= leading; line = w
            else:
                line = trial
        if line:
            self.c.drawString(x, self.y, line); self.y -= leading

    def _footer(self):
        c = self.c
        c.setFillColor(MUTED); c.setFont("Helvetica", 7)
        c.drawString(MARGIN, 24, "FICTIONAL DEMO FORM - all names and identifiers are mock data.")
        c.drawRightString(PAGE_W - MARGIN, 24, f"{self.s['form_no']}   Page {self.page}")

    def ensure(self, h):
        if self.y - h < 48:
            self.new_page()

    # ----- content ----------------------------------------------------------
    def section(self, title):
        self.ensure(60)
        c, brand = self.c, _c(self.s["color"])
        c.setFillColor(_c(self.s["color"], 0.08))
        c.rect(MARGIN, self.y - 16, CONTENT_W, 18, stroke=0, fill=1)
        c.setFillColor(brand); c.rect(MARGIN, self.y - 16, 3, 18, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 10); c.drawString(MARGIN + 9, self.y - 11, title)
        self.y -= 28

    def row(self, fields):
        row_h = 34
        self.ensure(row_h)
        x = MARGIN
        unit = (CONTENT_W - GUTTER * 11) / 12
        for (name, label, typ, span, options, maxlen) in fields:
            w = unit * span + GUTTER * (span - 1)
            self._field(x, w, name, label, typ, options, maxlen)
            x += w + GUTTER
        self.y -= row_h

    def _field(self, x, w, name, label, typ, options, maxlen):
        c, af = self.c, self.c.acroForm
        brand = _c(self.s["color"])
        top = self.y
        if typ == "checkbox":
            af.checkbox(name=name, tooltip=label, x=x, y=top - 22, size=12, buttonStyle="check",
                        borderColor=brand, fillColor=white, textColor=brand, forceBorder=True,
                        checked=False)
            c.setFillColor(INK); c.setFont("Helvetica", 8.8)
            text = label + "  (check if yes)"
            if c.stringWidth(text, "Helvetica", 8.8) > w - 22:
                text = label
            c.drawString(x + 18, top - 19, text)
            return
        c.setFillColor(MUTED); c.setFont("Helvetica-Bold", 7)
        c.drawString(x, top - 7, label.upper())
        if typ == "radio":
            ox = x
            for opt in options:
                af.radio(name=name, tooltip=label, value=opt, selected=False, x=ox, y=top - 25,
                         size=11, buttonStyle="circle", shape="circle", borderColor=brand,
                         fillColor=white, textColor=brand, forceBorder=True)
                c.setFillColor(INK); c.setFont("Helvetica", 8.8)
                c.drawString(ox + 15, top - 22.5, opt)
                ox += 30 + c.stringWidth(opt, "Helvetica", 8.8)
            return
        if typ == "dropdown":
            af.choice(name=name, tooltip=label, value=" ", options=[" "] + options, x=x, y=top - 28,
                      width=w, height=18, fontName="Helvetica", fontSize=9, borderColor=LINE,
                      fillColor=FIELD_BG, textColor=INK, forceBorder=True, fieldFlags="combo")
            return
        if typ == "signature":
            c.setStrokeColor(INK); c.setLineWidth(0.7)
            c.line(x, top - 28, x + w, top - 28)
            af.textfield(name=name, tooltip=label, x=x, y=top - 28, width=w, height=18,
                         fontName="Helvetica-Oblique", fontSize=10, borderWidth=0,
                         fillColor=white, textColor=INK, forceBorder=False, maxlen=250)
            return
        kwargs = {"maxlen": maxlen or 250}
        af.textfield(name=name, tooltip=label, x=x, y=top - 28, width=w, height=18,
                     fontName="Helvetica", fontSize=9, borderColor=LINE, borderWidth=0.8,
                     fillColor=FIELD_BG, textColor=INK, forceBorder=True, **kwargs)

    def build(self):
        self.new_page()
        for title, fields in self.s["sections"]:
            self.section(title)
            row, used = [], 0
            for fld in fields:
                if used + fld[3] > 12:
                    self.row(row); row, used = [], 0
                row.append(fld); used += fld[3]
            if row:
                self.row(row)
            self.y -= 4
        self._footer()
        self.c.save()


K = 0.5523


def _circle(cx: float, cy: float, r: float) -> str:
    k = K * r
    return (f"{cx + r:.2f} {cy:.2f} m {cx + r:.2f} {cy + k:.2f} {cx + k:.2f} {cy + r:.2f} {cx:.2f} {cy + r:.2f} c "
            f"{cx - k:.2f} {cy + r:.2f} {cx - r:.2f} {cy + k:.2f} {cx - r:.2f} {cy:.2f} c "
            f"{cx - r:.2f} {cy - k:.2f} {cx - k:.2f} {cy - r:.2f} {cx:.2f} {cy - r:.2f} c "
            f"{cx + k:.2f} {cy - r:.2f} {cx + r:.2f} {cy - k:.2f} {cx + r:.2f} {cy:.2f} c")


def fix_radio_appearances(path: Path, rgb) -> None:
    """Replace ReportLab's glyph-based radio appearances with vector circles that render the same
    in every viewer (empty ring when off, ring + dot when selected)."""
    import pymupdf

    doc = pymupdf.open(str(path))
    col = " ".join(f"{c:.3f}" for c in rgb)
    for page in doc:
        for w in page.widgets():
            if w.field_type != pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON:
                continue
            on = w.on_state().replace(" ", "#20")
            wd, ht = w.rect.width, w.rect.height
            cx, cy, r = wd / 2, ht / 2, min(wd, ht) / 2 - 0.7
            ring = f"q 1 1 1 rg {col} RG 1 w {_circle(cx, cy, r)} b Q\n"
            dot = f"q {col} rg {_circle(cx, cy, r * 0.48)} f Q\n"
            xrefs = []
            for content in (ring + dot, ring):
                x = doc.get_new_xref()
                doc.update_object(x, f"<< /Type /XObject /Subtype /Form /BBox [0 0 {wd:.2f} {ht:.2f}] "
                                     f"/Resources << >> >>")
                doc.update_stream(x, content.encode())
                xrefs.append(x)
            doc.xref_set_key(w.xref, "AP", f"<< /N << /{on} {xrefs[0]} 0 R /Off {xrefs[1]} 0 R >> >>")
            doc.xref_set_key(w.xref, "MK", f"<< /BC [ {col} ] /BG [ 1 1 1 ] >>")
    doc.saveIncr()
    doc.close()


def build_all(specs: list[dict] | None = None) -> list[Path]:
    paths = []
    for spec in (ALL_TEMPLATES if specs is None else specs):
        out = ROOT / spec["file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        FormBuilder(spec, out).build()
        fix_radio_appearances(out, spec["color"])
        paths.append(out)
    return paths


if __name__ == "__main__":
    for p in build_all():
        print("built", p.relative_to(ROOT))
