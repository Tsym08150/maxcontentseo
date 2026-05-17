from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


try:
    import fitz  # PyMuPDF
except ModuleNotFoundError:
    fallback = Path.home() / "Downloads" / "codex_tmp_pymupdf"
    if fallback.exists():
        sys.path.insert(0, str(fallback))
        import fitz  # type: ignore
    else:
        raise SystemExit(
            "PyMuPDF is required. Install it with: py -m pip install pymupdf"
        )

from PIL import Image, ImageDraw


DEFAULT_PDF = Path(r"C:\Users\MaxContentSeO\Downloads\SEO_Audit_Showcase_v13.pdf")
DEFAULT_OUT = Path("qa_output")

BAD_LOCATION_TERMS = ["münchen", "München"]
BAD_SPACING_TERMS = [
    "Erfahru ng",
    "Markenkonsisten z",
    "Ranking-Differenzieru ng",
    "Click-Throug h",
    "Branchenverzeich nis",
    "Hautanalyse-Bl öcke",
    "man ueller",
    "ind ividuell",
    "k onkret",
    "Per formance",
    "deut lich",
    "opt imierbar",
    "I hrer",
    "An zeigenwert",
]
BAD_RISK_TERMS = [
    "Google bewertet langsame Mobile-Seiten schlechter",
    "Das erklärt teilweise, warum",
    "würde Position 1 einen Äquivalentwert",
    "an Google Ads sparen",
]
LEGAL_TERMS = ["Vorher-/Nachher-Bilder"]
BAD_URL_TERMS = ["/kategorie-seite\ufffealt/"]
LEGAL_MITIGATION = "Nur einsetzen, wenn für die jeweilige Behandlungsart rechtlich zulässig und sauber dokumentiert."
RISK_REPLACEMENTS = [
    (
        "Google bewertet langsame Mobile-Seiten schlechter",
        "Schlechte Mobile-Performance kann Nutzerverhalten, Conversion und SEO-Signale negativ beeinflussen.",
    ),
    (
        "Das erklärt teilweise, warum",
        "Die schwache Mobile-Performance kann ein zusätzlicher Faktor sein, erklärt den geringen Traffic aber nicht allein.",
    ),
    (
        "würde Position 1 einen Äquivalentwert",
        "Modellrechnung: Bei 1.300 Suchanfragen/Monat und einem CPC von EUR 5,97 kann ein starkes organisches Ranking rechnerisch einen relevanten Anzeigenwert ersetzen.",
    ),
    (
        "an Google Ads sparen",
        "Der tatsächliche Wert hängt von CTR, Conversion Rate und Buchungswert ab.",
    ),
]


def prefix_from_pdf(pdf: Path) -> str:
    match = re.search(r"_v(\d+)\.pdf$", pdf.name, re.IGNORECASE)
    if match:
        return f"v{match.group(1)}"
    return pdf.stem


def render_pages(doc: "fitz.Document", pages_dir: Path, zoom: float) -> list[Path]:
    pages_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    matrix = fitz.Matrix(zoom, zoom)
    for index, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        path = pages_dir / f"page-{index:02d}.png"
        pix.save(path)
        rendered.append(path)
    return rendered


def make_contactsheet(page_paths: list[Path], output: Path, thumb_width: int = 260) -> None:
    thumbs = []
    for page_path in page_paths:
        image = Image.open(page_path).convert("RGB")
        ratio = thumb_width / image.width
        thumb = image.resize((thumb_width, int(image.height * ratio)), Image.Resampling.LANCZOS)
        thumbs.append((page_path, thumb))

    cols = 5 if len(thumbs) >= 5 else max(1, len(thumbs))
    label_h = 24
    gap = 18
    rows = (len(thumbs) + cols - 1) // cols
    cell_w = thumb_width + gap
    cell_h = max(t.height for _, t in thumbs) + label_h + gap
    sheet = Image.new("RGB", (cols * cell_w + gap, rows * cell_h + gap), "white")
    draw = ImageDraw.Draw(sheet)

    for idx, (page_path, thumb) in enumerate(thumbs):
        row = idx // cols
        col = idx % cols
        x = gap + col * cell_w
        y = gap + row * cell_h
        sheet.paste(thumb, (x, y + label_h))
        draw.text((x, y), page_path.stem, fill=(30, 30, 30))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def extract_text(doc: "fitz.Document") -> str:
    chunks = []
    for index, page in enumerate(doc, start=1):
        chunks.append(f"\n\n--- PAGE {index:02d} ---\n")
        chunks.append(page.get_text("text"))
    return "".join(chunks)


def control_char_findings(text: str) -> list[str]:
    findings = []
    for pos, char in enumerate(text):
        code = ord(char)
        if char in "\n\r\t":
            continue
        if code < 32 or code in {0xFFFE, 0xFFFF}:
            snippet = text[max(0, pos - 20) : pos + 20].replace("\n", " ")
            findings.append(f"U+{code:04X} near `{snippet}`")
    return findings


def find_terms(text: str, terms: list[str]) -> dict[str, int]:
    return {term: text.count(term) for term in terms if text.count(term)}


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def write_report(
    report: Path,
    pdf: Path,
    prefix: str,
    rendered: list[Path],
    text_path: Path,
    contactsheet: Path,
    text: str,
) -> None:
    sections = {
        "München-Reste": find_terms(text, BAD_LOCATION_TERMS),
        "Spacing-Artefakte": find_terms(text, BAD_SPACING_TERMS),
        "Kaputte URL-Darstellungen": find_terms(text, BAD_URL_TERMS),
        "Harte fachliche Formulierungen": find_terms(text, BAD_RISK_TERMS),
    }
    legal_findings = find_terms(text, LEGAL_TERMS)
    normalized_text = normalize_space(text)
    legal_mitigated = bool(legal_findings) and normalize_space(LEGAL_MITIGATION) in normalized_text
    controls = control_char_findings(text)

    lines = [
        f"# PDF QA Report — {prefix}",
        "",
        f"- PDF: `{pdf}`",
        f"- Gerenderte Seiten: `{Path('qa_output') / f'{prefix}_pages'}` ({len(rendered)} Dateien)",
        f"- Kontaktübersicht: `{contactsheet}`",
        f"- Extrahierter Text: `{text_path}`",
        "",
        "## Automatische Prüfungen",
        "",
    ]
    for title, findings in sections.items():
        lines.append(f"### {title}")
        if findings:
            for term, count in findings.items():
                lines.append(f"- ❌ `{term}` — {count} Treffer")
        else:
            lines.append("- ✅ Keine Treffer")
        lines.append("")

    lines.append("### Rechtlich sensible Formulierungen")
    if legal_findings and legal_mitigated:
        for term, count in legal_findings.items():
            lines.append(f"- ⚠️ `{term}` — {count} Treffer, mit Zulässigkeitshinweis entschärft")
        lines.append(f"- ✅ Hinweis vorhanden: `{LEGAL_MITIGATION}`")
    elif legal_findings:
        for term, count in legal_findings.items():
            lines.append(f"- ❌ `{term}` — {count} Treffer ohne Zulässigkeitshinweis")
    else:
        lines.append("- ✅ Keine Treffer")
    lines.append("")

    lines.append("### Korrekturstatus harter Formulierungen")
    for old, new in RISK_REPLACEMENTS:
        old_count = text.count(old)
        new_present = normalize_space(new) in normalized_text
        if old_count:
            lines.append(f"- ❌ Altformulierung noch vorhanden: `{old}` — {old_count} Treffer")
        elif new_present:
            lines.append(f"- ✅ Ersetzt durch: `{new}`")
        else:
            lines.append(f"- ⚠️ Altformulierung nicht gefunden, Ersatzformulierung ebenfalls nicht gefunden: `{old}`")
    lines.append("")

    lines.append("### Ungewöhnliche Steuerzeichen")
    if controls:
        for item in controls[:30]:
            lines.append(f"- ❌ {item}")
        if len(controls) > 30:
            lines.append(f"- … {len(controls) - 30} weitere")
    else:
        lines.append("- ✅ Keine ungewöhnlichen Steuerzeichen")
    lines.append("")

    unmitigated_legal = 1 if legal_findings and not legal_mitigated else 0
    total_issues = sum(len(v) for v in sections.values()) + len(controls) + unmitigated_legal
    lines.append("## Ergebnis")
    lines.append("")
    if total_issues:
        lines.append(f"- ❌ {total_issues} Prüfpunkte mit Treffern. Siehe Liste oben.")
    else:
        lines.append("- ✅ Keine automatischen Treffer in den definierten Problemklassen.")
    lines.append("")
    lines.append("## Manuelle Sichtprüfung")
    lines.append("")
    lines.append("- [ ] Contactsheet geprüft")
    lines.append("- [ ] Seite 1 geprüft")
    lines.append("- [ ] Seite 8 geprüft")
    lines.append("- [ ] Seite 9 geprüft")
    lines.append("- [ ] Seite 10 geprüft")

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")


def run(pdf: Path, out_dir: Path, prefix: str | None, zoom: float) -> None:
    if not pdf.exists():
        raise SystemExit(f"PDF not found: {pdf}")
    prefix = prefix or prefix_from_pdf(pdf)
    doc = fitz.open(pdf)
    pages_dir = out_dir / f"{prefix}_pages"
    rendered = render_pages(doc, pages_dir, zoom)
    contactsheet = out_dir / f"{prefix}_contactsheet.png"
    make_contactsheet(rendered, contactsheet)
    text = extract_text(doc)
    text_path = out_dir / f"{prefix}_extracted_text.txt"
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(text, encoding="utf-8")
    report = out_dir / f"{prefix}_qa_report.md"
    write_report(report, pdf, prefix, rendered, text_path, contactsheet, text)
    print(f"Rendered pages: {pages_dir}")
    print(f"Contactsheet: {contactsheet}")
    print(f"Text: {text_path}")
    print(f"Report: {report}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render PDF pages and run text QA checks.")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--prefix", default=None)
    parser.add_argument("--zoom", type=float, default=1.6)
    args = parser.parse_args()
    run(args.pdf, args.out_dir, args.prefix, args.zoom)


if __name__ == "__main__":
    main()
