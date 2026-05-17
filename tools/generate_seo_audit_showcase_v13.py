from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUT = Path(r"C:\Users\MaxContentSeO\Downloads\SEO_Audit_Showcase_v13.pdf")

ACCENT = colors.HexColor("#1B6B4A")
TEXT = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#65707C")
BORDER = colors.HexColor("#D9DED8")
SOFT = colors.HexColor("#F5F7F4")
HEADER = colors.HexColor("#E9F3ED")


def make_doc(path: Path) -> BaseDocTemplate:
    portrait = A4
    land = landscape(A4)
    margin_x = 16 * mm
    margin_y = 15 * mm

    doc = BaseDocTemplate(
        str(path),
        pagesize=portrait,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=margin_y,
        bottomMargin=margin_y,
        title="SEO Audit Showcase v13",
        author="MaxContentSEO",
    )
    portrait_frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        portrait[0] - doc.leftMargin - doc.rightMargin,
        portrait[1] - doc.topMargin - doc.bottomMargin,
        id="portrait",
    )
    landscape_frame = Frame(
        margin_y,
        margin_x,
        land[0] - 2 * margin_y,
        land[1] - 2 * margin_x,
        id="landscape",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="Portrait", frames=[portrait_frame], pagesize=portrait, onPage=footer),
            PageTemplate(id="Landscape", frames=[landscape_frame], pagesize=land, onPage=footer),
        ]
    )
    return doc


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(doc.leftMargin, 10 * mm, doc.pagesize[0] - doc.leftMargin, 10 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(doc.leftMargin, 6 * mm, "MaxContentSEO · SEO Audit Report · anonymisiertes Beispielaudit")
    canvas.drawRightString(doc.pagesize[0] - doc.leftMargin, 6 * mm, f"Seite {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=TEXT,
        alignment=TA_LEFT,
        spaceAfter=10,
        splitLongWords=0,
    )
)
styles.add(
    ParagraphStyle(
        name="H1x",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=ACCENT,
        spaceBefore=14,
        spaceAfter=8,
        splitLongWords=0,
    )
)
styles.add(
    ParagraphStyle(
        name="H2x",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=TEXT,
        spaceBefore=10,
        spaceAfter=5,
        splitLongWords=0,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyX",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=12.4,
        textColor=TEXT,
        spaceAfter=5,
        splitLongWords=0,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.1,
        leading=10.5,
        textColor=TEXT,
        splitLongWords=0,
    )
)
styles.add(
    ParagraphStyle(
        name="TableCell",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.6,
        leading=9.8,
        textColor=TEXT,
        splitLongWords=0,
        wordWrap="LTR",
    )
)
styles.add(
    ParagraphStyle(
        name="TableHead",
        parent=styles["TableCell"],
        fontName="Helvetica-Bold",
        textColor=TEXT,
        alignment=TA_LEFT,
    )
)

for style_name in [
    "CoverTitle",
    "H1x",
    "H2x",
    "BodyX",
    "Small",
    "TableCell",
    "TableHead",
]:
    style = styles[style_name]
    style.alignment = TA_LEFT
    style.splitLongWords = 0
    style.hyphenationLang = ""
    style.embeddedHyphenation = 0
    style.justifyBreaks = 0
    style.justifyLastLine = 0
    style.spaceShrinkage = 0
    style.wordWrap = "LTR"


def p(text: str, style: str = "BodyX") -> Paragraph:
    return Paragraph(text, styles[style])


def bullet(text: str) -> Paragraph:
    return Paragraph("• " + text, styles["BodyX"])


def cell(text, style="TableCell"):
    return p(str(text), style)


def table(data, widths, repeat=1, font_size=None, header=True):
    rows = []
    for r, row in enumerate(data):
        rows.append([cell(x, "TableHead" if header and r == 0 else "TableCell") for x in row])
    tbl = Table(rows, colWidths=widths, repeatRows=repeat, hAlign="LEFT", splitByRow=1)
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), HEADER if header else colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tbl


def simple_kv(rows):
    return table(rows, [45 * mm, 65 * mm, 58 * mm])


def story():
    s = []
    s.append(p("SEO Audit Report", "CoverTitle"))
    s.append(p("Anonymisiertes Beispielaudit auf Basis von Live-Crawl, Rankingdaten und manueller Prüfung"))
    s.append(
        simple_kv(
            [
                ["Projekt", "Lokales Beauty-Studio in einer deutschen Großstadt (anonymisiert)", "[Website vertraulich]"],
                ["Profil", "etablierter Standort", "inhabergeführter Betrieb"],
                ["Vertrauen", "externe Vertrauenssignale vorhanden", "Stand: 2026"],
                ["Kontakt", "MaxContentSEO", "georg@maxcontentseo.de"],
            ]
        )
    )
    s.append(Spacer(1, 6))
    s.append(p("Hinweis: Keywords und Standortangaben sind beispielhaft aus der Branche — im echten Audit individuell auf Ihren Standort angepasst.", "Small"))
    s.append(p("Datenbasis dieses Audits", "H1x"))
    s.append(p("Vollständige Datenbasis: Verifizierte Live-Website-Analyse, Google-Suchergebnisse, KI-gestützte Tiefenrecherche, Ubersuggest Site Audit (36 Seiten gecrawlt, 72 SEO-Issues identifiziert), Ubersuggest Rank Tracking (13 Keywords), Ubersuggest Competitor Analysis, Backlink-Analyse (ca. 35-40 Verweisdomains, über 2.000 Backlinks) sowie vollständige Site-Speed-Messung für Desktop und Mobile."))
    s.append(p("Hinweis: Suchvolumen, CPC, SEO Difficulty, Traffic- und Backlink-Werte sind Tool-Schätzungen aus Ubersuggest und dienen der Priorisierung. Sie ersetzen keine Daten aus Google Search Console, GA4 oder Google Ads.", "Small"))

    s.append(p("1. Executive Summary", "H1x"))
    s.append(
        table(
            [
                ["Kennzahl", "Wert", "Bewertung"],
                ["On-Page Score", "68 / 100", "Mittel - optimierbar"],
                ["SEO-Issues", "72", "auf 36 Seiten"],
                ["Org. Traffic", "ca. 190", "Visits / Monat"],
                ["Verweisdomains", "ca. 35-40", "über 2.000 Backlinks gesamt"],
            ],
            [45 * mm, 40 * mm, 83 * mm],
        )
    )
    s.append(p("Lokales Beauty-Studio in einer deutschen Großstadt (anonymisiert) hat eine solide Basis: On-Page Score 68/100, ca. 190 organische Visits, starkes Bewertungsprofil und externe Vertrauenssignale vorhanden. Gleichzeitig verschenkt die Website durch konkret messbare Probleme erhebliches Potenzial."))
    s.append(p('Die zwei wichtigsten Suchbegriffe der Branche - "laser haarentfernung [Großstadt]" mit 1.300 Suchvolumen/Monat und "hydrafacial kosten" mit 880 Suchvolumen/Monat - werden aktuell nicht ausreichend abgefangen.'))
    s.append(p("Hinzu kommt ein kritisches Mobile-Performance-Problem: 8,58 Sekunden Ladezeit auf Mobile. Das liegt deutlich über dem empfohlenen Zielwert und kostet zusätzlich Rankings und Conversions."))
    s.append(p("Top-Probleme - Sofort-Erkenntnisse", "H2x"))
    s.append(
        table(
            [
                ["#", "Problem", "Auswirkung"],
                ["1", "Mobile Load Time 8,58s (POOR) - deutlich über Zielwert", "KRITISCH"],
                ["2", "29 Seiten haben einen Broken Link zu /kategorie-seite-alt/ (404-Fehler)", "KRITISCH"],
                ["3", "24 Seiten mit identischer Meta-Description", "KRITISCH"],
                ["4", "Markennamen-Tippfehler auf 6+ Seiten", "KRITISCH"],
                ["5", 'Keyword "laser haarentfernung [Großstadt]" (1.300 Vol.) nicht rankend', "VERLUST"],
                ["6", 'Keyword "hydrafacial kosten" (880 Vol.) nicht rankend', "VERLUST"],
                ["7", "Kein Blog / Content Funnel - informationaler Traffic wird verschenkt", "HOCH"],
                ["8", "Geräte-/Lasertyp-Inkonsistenz - Trust-Problem", "HOCH"],
                ["9", "Wiederholter Hautanalyse-Block auf 4+ Seiten", "MITTEL"],
                ["10", "/bestaetigungsseite-a/ und /bestaetigungsseite-b/ indexiert", "MITTEL"],
            ],
            [12 * mm, 115 * mm, 41 * mm],
        )
    )

    s.append(p("2. Stärken der Website", "H1x"))
    for item in [
        "On-Page SEO Score von 68/100 - solide Ausgangsbasis.",
        "Ca. 190 organische Visits/Monat laut Ubersuggest.",
        "Domain-Authority basiert auf ca. 35-40 Verweisdomains, darunter eine besonders starke Verweisquelle.",
        "Desktop Site Speed: Load Time 1,04s, Interactivity 4,50ms, CLS 0,00 - alles stark.",
        "Dreistelliges Bewertungsprofil mit Spitzenbewertung - starker Social Proof.",
        "Externe Vertrauenssignale vorhanden - starkes Vertrauenssignal.",
        "Breite Leistungsstruktur: 30+ erfolgreich gecrawlte Seiten.",
        "Laser-Haarentfernung-Seite: stärkste Asset-Seite mit Preisliste, FAQ, Sitzungsanzahl und Hauttypen.",
        "Top-3 Rankings für Brand- und Standort-Keywords: [Brand-Keyword] (Pos. 1), [Service-Keyword A] (Pos. 2), [lokales Studio-Keyword] (Pos. 3).",
        "Relevante Top-Liste eines Branchenportals enthält Backlink mit mittlerer bis guter Autorität.",
        "Langjährige Erfahrung der Geschäftsführung — starkes E-E-A-T-Signal.",
    ]:
        s.append(bullet(item))

    s.append(p("3. Kritische Fehler - sofort beheben", "H1x"))
    s.append(p("3.1 29 Seiten mit Broken Link zu /kategorie-seite-alt/", "H2x"))
    s.append(p('Befund laut Ubersuggest Site Audit: 29 von 36 gecrawlten Seiten haben einen Link mit dem Anker "Technologien", der zu /kategorie-seite-alt/ führt. Diese URL gibt einen 404-Fehler zurück. Die korrekte Zielseite ist /kategorie-seite/.'))
    s.append(p("Betroffene Seiten, Auszug:", "H2x"))
    for item in ["Startseite und mehrere Behandlungsseiten.", "Rechtliche Seiten, Kontaktseiten und Gutscheinseiten.", "Sogar /bestaetigungsseite-a/, obwohl diese Seite gar nicht indexiert sein sollte."]:
        s.append(bullet(item))
    s.append(p("Fix: WordPress-Menü öffnen und den fehlerhaften Link auf die korrekte URL ändern oder einen 301-Redirect von /kategorie-seite-alt/ auf /kategorie-seite/ einrichten. Aufwand: ca. 5 Minuten."))
    s.append(p("3.2 24 Seiten mit identischer Meta-Description", "H2x"))
    s.append(p("Befund: 24 Seiten haben exakt die gleiche generische Meta-Description. Auswirkung: Google differenziert die Seiten in den Suchergebnissen nicht sauber. Die Click-Through-Rate ist dadurch niedriger als möglich. Jeder Searcher sieht denselben Snippet-Text - egal ob er nach Aknebehandlung, Laser-Haarentfernung oder Hydrafacial sucht."))
    s.append(p("Fix: Pro Seite eine individuelle Meta-Description schreiben, jeweils mit 155-160 Zeichen. Mit Yoast SEO oder Rank Math ist das in 2-3 Stunden machbar."))
    s.append(p("3.3 Markennamen-Tippfehler auf 6+ Seiten", "H2x"))
    s.append(p("Im Template beziehungsweise in wiederverwendeten Seitenblöcken befinden sich Tippfehler, die sich über mehrere Seiten ziehen."))
    s.append(
        table(
            [
                ["URL / Stelle", "Tippfehler / Problem", "Prio"],
                ["/behandlungsseite-a/", "[Studioname] falsch geschrieben", "P1"],
                ["/behandlungsseite-b/", "[Studioname] falsch geschrieben", "P1"],
                ["/behandlungsseite-c/", "[Studioname] falsch geschrieben", "P1"],
                ["/behandlungsseite-d/", "[Studioname] falsch geschrieben, mehrfach", "P1"],
                ["/behandlungsseite-e/", "[Studioname] falsch geschrieben", "P1"],
                ["/behandlungsseite-f/", "[Studioname] falsch geschrieben, zweite Variante", "P1"],
                ["Startseite Fließtext", "Grammatikfehler im Fließtext", "P1"],
                ["Footer aller Seiten", "Rechtschreibfehler in Standortbezeichnung", "P1"],
                ["/behandlungsseite-g/", "Tippfehler plus Markenfehler", "P1"],
            ],
            [48 * mm, 96 * mm, 24 * mm],
        )
    )
    s.append(p("Fix: WordPress-Template und alle betroffenen Seiten prüfen, alle Vorkommen ersetzen. Aufwand: ca. 15 Minuten."))
    s.append(p("3.4 Geräte-/Lasertyp-Inkonsistenz - Trust-Problem", "H2x"))
    s.append(p("Auf der Startseite wird eine Gerätevariante betont. Auf der Laser-Seite und in den FAQs wird eine andere Geräte- beziehungsweise Modellvariante genannt. Recherchierende Kunden können solche Inkonsistenzen bemerken. Fix: Einheitliche Bezeichnung festlegen. Danach alle Seiten konsistent anpassen."))
    s.append(p("3.5 Copyright-Zeile: falscher Markenname", "H2x"))
    s.append(p('Footer aller Seiten: "Copyright (C) [Gerätehersteller]. Alle Rechte vorbehalten." [Gerätehersteller] ist der Gerätehersteller, nicht das Studio. Das wirkt wie ein Hersteller-Template und nicht wie ein professioneller Studiobetrieb. Korrekte Version: "Copyright (C) 2026 [Studioname]."'))
    s.append(p("3.6 Indexierte Bestätigungsseiten", "H2x"))
    s.append(p("/bestaetigungsseite-a/ und /bestaetigungsseite-b/ sind in Google indexiert, obwohl sie keinen Suchnutzen haben. /bestaetigungsseite-b/ hat zudem keine H1-Überschrift. Fix: Beide Seiten auf noindex setzen. Aufwand: ca. 5 Minuten."))

    s.append(p("4. Ranking-Analyse - wo steht die Website?", "H1x"))
    s.append(p("4.1 Aktuelle Rankings laut Ubersuggest", "H2x"))
    s.append(p("13 getrackte Keywords - Verteilung: Top 3 Positionen: 3 Keywords, alle Brand- beziehungsweise Standort-Keywords. Top 100 Positionen: 4 weitere Keywords. Nicht rankend: 6 Keywords, darunter die wertvollsten."))
    s.append(
        table(
            [
                ["Pos.", "Keyword", "Volumen", "SEO Diff.", "Bewertung"],
                ["1", "[Brand-Keyword]", "0", "12", "BRAND"],
                ["2", "[Service-Keyword A]", "0", "17", "BRAND"],
                ["3", "[lokales Studio-Keyword]", "0", "12", "BRAND"],
                ["11", "[lokales Hautpflege-Keyword]", "0", "12", "OK"],
                ["12", "[Laser-Service-Keyword]", "70", "26", "POTENZIAL"],
                ["18", "[Medical-Beauty-Standortkeyword]", "0", "12", "OK"],
                ["35", "medical beauty", "1.900", "39", "HEBEL"],
                ["-", "laser haarentfernung [Großstadt]", "1.300", "27", "KRITISCH"],
                ["-", "laser haarentfernung kosten [Großstadt]", "10", "28", "VERLOREN"],
                ["-", "[Behandlungskeyword A]", "0", "12", "VERLOREN"],
                ["-", "[lokales Studio-Keyword B]", "10", "41", "VERLOREN"],
            ],
            [15 * mm, 78 * mm, 24 * mm, 25 * mm, 26 * mm],
        )
    )
    s.append(p('4.2 Der große Verlust: "laser haarentfernung [Großstadt]"', "H2x"))
    s.append(p('Die Domain hat eine starke Laser-Seite mit Preisen, FAQs, Hauttypen und Sitzungsanzahl. Trotzdem rankt sie nicht für "laser haarentfernung [Großstadt]" mit 1.300 Suchvolumen/Monat. Bei einer SEO-Difficulty von 27 ist das ein erreichbares Ziel.'))
    s.append(p('Was Ubersuggest selbst empfiehlt: Im Bereich "SEO Opportunities" ist "Create new content for laser haarentfernung [Großstadt]" als Priorität 2 aufgelistet - direkt nach den Broken Links.'))
    s.append(p("4.3 Top Pages by Traffic - Realitätscheck", "H2x"))
    s.append(
        table(
            [
                ["Seite", "Visits/Monat", "Backlinks"],
                ["Startseite", "ca. 110", "über 2.000"],
                ["Behandlungsseite A", "ca. 40", "0"],
                ["Kontaktseite", "ca. 20", "wenige"],
                ["Behandlungsseite B", "unter 10", "0"],
                ["Behandlungsseite C", "unter 10", "wenige"],
                ["Behandlungsseite D", "unter 10", "0"],
                ["Behandlungsseite E", "unter 10", "0"],
                ["Laser-Haarentfernung-Seite", "unter 10", "wenige"],
            ],
            [75 * mm, 45 * mm, 48 * mm],
        )
    )
    s.append(p("Auffälliger Befund: Die Laser-Haarentfernung-Seite - die stärkste Asset-Seite der Domain - bekommt nur sehr wenig organischen Traffic. Eine andere Behandlungsseite erhält ein Vielfaches davon, obwohl sie inhaltlich schwächer ist. Hier liegt das größte ungenutzte Potenzial."))

    s.append(p("5. Technisches SEO", "H1x"))
    s.append(p("5.1 Site Audit Zusammenfassung laut Ubersuggest", "H2x"))
    s.append(
        table(
            [
                ["Metrik", "Wert", "Bewertung"],
                ["On-Page Score", "68 / 100", "MITTEL"],
                ["Pages Crawled", "36", "OK"],
                ["SEO Issues entdeckt", "72", "HOCH"],
                ["Successful Pages", "30", "OK"],
                ["Redirected Pages", "5", "OK"],
                ["Broken Pages", "1 (/kategorie-seite-alt/)", "FIXEN"],
            ],
            [58 * mm, 55 * mm, 55 * mm],
        )
    )
    s.append(p("5.2 Site Speed - kritisches Mobile-Problem", "H2x"))
    s.append(p("Desktop-Performance ist exzellent. Mobile dagegen liegt bei 8,58 Sekunden Ladezeit. Das ist deutlich über dem von Google empfohlenen Zielwert. Da ein großer Teil lokaler Suchanfragen mobil erfolgt, ist das ein zentrales Problem."))
    s.append(
        table(
            [
                ["Metrik", "Desktop", "Mobile"],
                ["Load Time", "1,04s GREAT", "8,58s POOR"],
                ["Interactivity", "4,50ms GREAT", "23,50ms GREAT"],
                ["Visual Stability (CLS)", "0,00 GREAT", "0,00 GREAT"],
            ],
            [58 * mm, 55 * mm, 55 * mm],
        )
    )
    s.append(p("Was 8,58s Mobile Load Time bedeutet:", "H2x"))
    for item in [
        "Google bewertet langsame Mobile-Seiten schlechter.",
        "Mobile Nutzer brechen bei langen Ladezeiten häufiger ab.",
        "Bei 8,58s verliert die Website wahrscheinlich einen relevanten Teil der mobilen Besucher, bevor die Seite vollständig geladen ist.",
        "Das erklärt teilweise, warum die Laser-Seite trotz starkem Content kaum organischen Traffic bekommt.",
    ]:
        s.append(bullet(item))
    s.append(p("Quick Win: Bilder optimieren, WebP einsetzen, Lazy Loading aktivieren und Bildgrößen komprimieren. Dadurch kann die Mobile Load Time erfahrungsgemäß deutlich reduziert werden. Aufwand: 30-60 Minuten mit einem Plugin wie Smush oder ShortPixel."))
    s.append(p("5.3 Title Tags - zu lang oder zu kurz", "H2x"))
    s.append(p("Ubersuggest hat 11 Seiten mit problematischen Title Tags identifiziert."))
    s.append(
        table(
            [
                ["URL", "Title, gekürzt"],
                ["/behandlungsseite-e/", "[Studioname] - Fadenlifting in [Großstadt]: innovative Anti-Aging-Behandlung ..."],
                ["/behandlungsseite-i/", "[Studioname] - Peeling [Großstadt]: innovative Peeling-Behandlungen ..."],
                ["/behandlungsseite-j/", "[Studioname] - Microdermabrasion [Großstadt] ..."],
                ["/behandlungsseite-h/", "Premium Aquafacial und Gesichtsbehandlungen in [Großstadt] ..."],
                ["/interne-seite-a/", "[Studioname] - AGB"],
                ["/behandlungsseite-f/", "Aknebehandlung [Großstadt]"],
                ["/behandlungsseite-k/", "Dermakosmetik in [Großstadt]"],
                ["/behandlungsseite-l/", "Faltenbehandlung in [Großstadt]"],
            ],
            [48 * mm, 120 * mm],
        )
    )
    s.append(p("5.4 Backlink-Profil - ca. 35-40 Verweisdomains, gemischte Qualität", "H2x"))
    s.append(
        table(
            [
                ["Quelle", "Autorität", "Spam-Risiko"],
                ["Externes Portal A", "hoch", "niedrig"],
                ["Externes Portal B", "mittel bis hoch", "mittel"],
                ["Externes Branchenverzeichnis C", "mittel", "erhöht"],
                ["Bewertungsportal D", "mittel", "mittel"],
                ["Telefon-/Bewertungsportal E", "mittel", "mittel"],
                ["Anonymisiertes Branchenportal F", "mittel bis gut", "niedrig"],
            ],
            [68 * mm, 50 * mm, 50 * mm],
        )
    )
    for item in [
        "Mehrere nahezu identische Pressemitteilungs-Backlinks mit ähnlichem Anchor-Text zu einem Service-Keyword. Das wirkt wie ein Linkspam-Pattern.",
        'Anchor-Texte sind überwiegend generisch, zum Beispiel "website" oder "[Website vertraulich]", statt keyword-orientiert.',
        "Eine hochwertige Erwähnung in einer Top-Liste eines relevanten Branchenportals ist vorhanden.",
    ]:
        s.append(bullet(item))

    s.append(p("6. Keyword-Chancen mit echten Daten", "H1x"))
    s.append(p("6.1 Hydrafacial-Cluster - Suchvolumen vorhanden, kein Ranking", "H2x"))
    s.append(
        table(
            [
                ["Keyword", "Volumen", "CPC", "SEO Diff.", "Prio"],
                ["hydrafacial kosten", "880", "EUR 1,14", "22", "P1"],
                ["hydrafacial behandlung kosten", "110", "EUR 0,90", "7", "P1"],
                ["hydrafacial kosten krankenkasse", "70", "EUR 0,00", "9", "P1"],
                ["hydrafacial preisliste", "20", "EUR 0,70", "41", "P2"],
            ],
            [68 * mm, 24 * mm, 28 * mm, 28 * mm, 20 * mm],
        )
    )
    s.append(p("Quick Win: \"hydrafacial behandlung kosten\" hat eine SEO Difficulty von 7. Das ist sehr leicht erreichbar. Aufgrund der niedrigen SEO Difficulty ist das Keyword ein guter Kandidat für priorisierte Content-Optimierung. Ein Top-10-Ranking ist möglich, aber nicht garantierbar."))
    s.append(p("6.2 Laser-Cluster - größte Chance", "H2x"))
    s.append(
        table(
            [
                ["Keyword", "Volumen", "CPC", "SEO Diff.", "Prio"],
                ["laser haarentfernung [Großstadt]", "1.300", "EUR 5,97", "27", "P1"],
                ["laser haarentfernung schulung [Großstadt]", "20", "EUR 1,01", "28", "P3"],
            ],
            [68 * mm, 24 * mm, 28 * mm, 28 * mm, 20 * mm],
        )
    )
    s.append(p("Wert-Analyse: Bei 1.300 Suchvolumen/Monat und CPC EUR 5,97 würde Position 1 einen Äquivalentwert von ca. EUR 1.500-2.500/Monat an Google Ads sparen. Das rechtfertigt eine intensive Optimierung der Laser-Seite."))
    s.append(p("6.3 Ubersuggests eigene SEO Opportunities", "H2x"))
    opportunities = [["Prio", "Typ", "Opportunity"]]
    opportunities += [
        ["1", "SEO ISSUE", "29 Seiten mit Broken Links beheben"],
        ["2", "NEW CONTENT", 'Neuen Content erstellen für "laser haarentfernung [Großstadt]"'],
        ["3", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword A]"],
        ["4", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword B]"],
        ["5", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword C]"],
        ["6", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword D]"],
        ["7", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword E]"],
        ["8", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword F]"],
        ["9", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword G]"],
    ]
    s.append(table(opportunities, [20 * mm, 38 * mm, 110 * mm]))

    s.append(p("7. Content SEO", "H1x"))
    s.append(p("7.1 Duplicate Content - wiederholter Hautanalyse-Block auf 4+ Seiten", "H2x"))
    s.append(p("Ein nahezu identischer Block zu einer Hautanalyse-Technologie erscheint auf mehreren Seiten, unter anderem auf Seiten zu apparativen Gesichtsbehandlungen, Gesichtspflege, Peeling und Aknebehandlung. Dazu kommen stark herstellerzentrierte Produktbeschreibungen, die sich wiederholen."))
    s.append(p("7.2 Hersteller-Sprache statt Expertencontent", "H2x"))
    s.append(p("Mehrere Service-Seiten lesen sich wie Produktkataloge."))
    s.append(
        table(
            [
                ["Was fehlt", "Warum wichtig"],
                ["Konkrete Kosten und Preise", "Nutzer entscheiden häufig nach Preis. Ohne Preise springen sie leichter zur Konkurrenz."],
                ["Sitzungsanzahl und Ablauf", "Reduziert Unsicherheit vor dem Termin."],
                ["Ausfallzeit und Kontraindikationen", "Wichtig für Kaufentscheidungen bei medizin-nahen Treatments."],
                ["Vorher-/Nachher-Bilder", "Mehrere direkte Wettbewerber nutzen solche Elemente als zentrales Vertrauenselement."],
                ["Eignung für Hauttypen", "Differenziert die Seite von generischen Angeboten."],
            ],
            [58 * mm, 110 * mm],
        )
    )
    s.append(p("7.3 Kein Blog vorhanden", "H2x"))
    s.append(p("Die Domain verpasst den gesamten informationsgetriebenen Traffic. Die wertvollsten Keywords aus Kapitel 6 erfordern dedizierten Blog-Content."))

    s.append(p("8. Local SEO", "H1x"))
    s.append(
        table(
            [
                ["Kriterium", "Status", "Bewertung"],
                ["Google-Bewertungen", "starkes Bewertungsprofil", "STARK"],
                ["NAP onsite", "Konsistent auf Start- und Kontaktseite", "OK"],
                ["NAP offsite", "In einem externen Branchenverzeichnis sind falsche Öffnungszeiten hinterlegt", "PROBLEM"],
                ["LocalBusiness Schema-Markup", "Fehlt komplett", "FEHLT"],
                ["Relevantes Buchungsportal", "Nicht gelistet", "FEHLT"],
                ["Stadtteil-Landingpages", "Nicht vorhanden", "FEHLT"],
                ["Standort-Signal im Content", "Nur schwach verankert", "SCHWACH"],
            ],
            [50 * mm, 84 * mm, 34 * mm],
        )
    )

    s.append(p("9. Konkurrenzanalyse - anonymisierte Vergleichsdaten", "H1x"))
    s.append(
        table(
            [
                ["Domain", "Gemeinsame Keywords", "Keyword-Gap", "Geschätzter Traffic", "Backlinks"],
                ["[Website vertraulich]", "-", "-", "ca. 190", "über 2.000"],
                ["Wettbewerber A", "ca. 20", "ca. 40", "ca. 150-200 Visits/Monat", "200-300"],
                ["Wettbewerber B", "ca. 10", "ca. 50", "ca. 200-250 Visits/Monat", "unter 100"],
                ["Wettbewerber C", "nicht ausgewiesen", "ca. 30", "unter 100 Visits/Monat", "200-300"],
            ],
            [45 * mm, 37 * mm, 30 * mm, 38 * mm, 18 * mm],
        )
    )
    for item in [
        "Lokales Beauty-Studio in einer deutschen Großstadt (anonymisiert) hat mehr organischen Traffic als zwei der drei betrachteten Wettbewerber, aber weniger als der stärkste Vergleichswettbewerber.",
        "Der Keyword-Gap zum stärksten Wettbewerber liegt grob bei ca. 50 Keywords. Das ist die direkte Content-Roadmap.",
        "Die auditierte Website hat zwar über 2.000 Backlinks, aber nur ca. 35-40 Verweisdomains. Die Backlink-Diversität ist niedriger, als die reine Backlink-Zahl vermuten lässt.",
        "Ein Wettbewerber erreicht mit deutlich weniger Backlinks mehr Traffic. Das deutet auf bessere Content-Qualität und bessere Keyword-Abdeckung hin.",
    ]:
        s.append(bullet(item))

    s.append(NextPageTemplate("Landscape"))
    s.append(PageBreak())
    s.append(p("10. Priorisierter Maßnahmenplan", "H1x"))
    s.append(p("Priorität 1 - Quick Wins, 0-14 Tage", "H2x"))
    plan1 = [
        ["#", "Maßnahme", "Aufwand", "Effekt"],
        ["1", "Broken Link /kategorie-seite-alt/ beheben, 29 Seiten", "5 Min.", "Crawl-Budget, User-Erfahrung"],
        ["2", "Tippfehler im Template korrigieren, alle 6+ Stellen", "15 Min.", "Vertrauen, Markenkonsistenz"],
        ["3", "Geräte-/Lasertyp vereinheitlichen", "30 Min.", "Trust-Signal"],
        ["4", "Copyright: [Gerätehersteller] -> [Studioname]", "5 Min.", "E-E-A-T-Signal"],
        ["5", "/bestaetigungsseite-a/ und /bestaetigungsseite-b/ auf noindex setzen", "5 Min.", "Crawl-Budget"],
        ["6", "24 Duplicate Meta Descriptions individualisieren", "2-3 Std.", "CTR, Ranking-Differenzierung"],
        ["7", "Title Tags zu lang/zu kurz fixen, 11 Seiten", "1-2 Std.", "Bessere CTR, Click-Through"],
        ["8", "Bilder optimieren: WebP, Lazy Loading - Mobile Load Time von 8,58s auf unter 3s senken", "30-60 Min.", "Kritisch: Mobile Speed, Core Web Vitals, Conversions"],
        ["9", "LocalBusiness Schema-Markup einrichten", "30 Min.", "Lokale Sichtbarkeit"],
        ["10", "Falsche Öffnungszeiten in externem Branchenverzeichnis korrigieren", "15 Min.", "NAP-Konsistenz"],
    ]
    s.append(table(plan1, [12 * mm, 143 * mm, 31 * mm, 82 * mm]))
    s.append(p("Priorität 2 - Wachstum, 30-90 Tage", "H2x"))
    plan2 = [
        ["#", "Maßnahme", "Aufwand", "Effekt"],
        ["11", 'Laser-Seite gezielt für "laser haarentfernung [Großstadt]" optimieren', "4-6 Std.", "1.300 Suchvolumen/Monat erschließen"],
        ["12", 'Blog-Artikel: "Hydrafacial Kosten [Großstadt]" (Vol. 880, SEO-Diff. 22)', "Mittel", "Hochvolumiges Keyword erschließen"],
        ["13", 'Blog-Artikel: "Hydrafacial Behandlung Kosten" (Vol. 110, SEO-Diff. 7)', "Mittel", "Sehr leicht erreichbares Top-10-Ranking"],
        ["14", "Interne Verlinkung: Footer-only -> contextual", "3-4 Std.", "Link-Juice, Crawling"],
        ["15", "Wiederholte Hautanalyse-Blöcke individualisieren", "Mittel", "Content-Einzigartigkeit"],
        ["16", "Profil auf relevantem Buchungsportal erstellen", "2-3 Std.", "Zusätzlicher Buchungskanal"],
        ["17", "Stadtteil-Landingpage für lokales Studio-Keyword erstellen", "Mittel", "Stadtteil-Suchanfragen"],
        ["18", "Bewertungsstrategie: QR-Code + WhatsApp-Follow-up", "Laufend", "Mehr Bewertungen"],
        ["19", "Medienhinweis prominent auf Startseite platzieren", "1 Std.", "Vertrauen, USP"],
    ]
    s.append(table(plan2, [12 * mm, 143 * mm, 31 * mm, 82 * mm]))
    s.append(p("Priorität 3 - langfristig, 3-12 Monate", "H2x"))
    plan3 = [
        ["#", "Maßnahme", "Aufwand", "Effekt"],
        ["20", "Content-Cluster: Laser als Pillar + 5 Cluster-Artikel", "Hoch", "Thematische Autorität"],
        ["21", "Service-Seiten neu schreiben: Expertencontent statt Herstellertext", "Hoch", "Differenzierung, E-E-A-T"],
        ["22", "Backlink-Aufbau: hochwertige Branchenseiten, PR", "Hoch", "Domain-Authority steigern"],
        ["23", "Google Search Console laufend monitoren", "Laufend", "Früherkennung, Monitoring"],
    ]
    s.append(table(plan3, [12 * mm, 143 * mm, 31 * mm, 82 * mm]))

    s.append(PageBreak())
    s.append(p("11. Was bedeutet das für Ihr Studio?", "H1x"))
    s.append(p("Dieses Audit zeigt drei Dinge klar: Welche Fehler aktuell Umsatz kosten, welche Maßnahmen zuerst kommen sollten und welche Themen langfristig Wachstum bringen. Der nächste Schritt muss kein großes Projekt sein — die Quick Wins aus Priorität 1 lassen sich in wenigen Stunden umsetzen."))
    s.append(p("Angebot & nächste Schritte", "H2x"))
    s.append(p('Das größte Sofort-Potenzial: Die Laser-Seite optimieren. Dadurch können die 1.300 monatlichen Suchanfragen nach "laser haarentfernung [Großstadt]" tatsächlich erschlossen werden.'))
    s.append(p("Modellrechnung: Bei 1.300 Suchanfragen/Monat und einem CPC von EUR 5,97 kann ein starkes organisches Ranking rechnerisch einen relevanten Anzeigenwert ersetzen. Der tatsächliche Wert hängt von CTR, Conversion Rate und Buchungswert ab."))
    s.append(p("Bereits ein einziger Neukunde über Google kann dieses Audit mehrfach refinanzieren."))
    offer = [
        ["Paket", "Preis", "Leistung"],
        ["Premium-Audit + Quick Fix", "490 EUR (Audit) + 200 EUR Umsetzung*", "10 Quick Wins (Prio 1): Broken Links beheben; Tippfehler korrigieren; Geräte-/Lasertyp vereinheitlichen; 24 Meta Descriptions neu schreiben; 11 Title Tags fixen; Bilder optimieren; Schema-Markup einrichten; NAP bereinigen."],
        ["SEO Wachstumspaket", "990 EUR / Monat", "Laufende Betreuung: 2 SEO-Artikel/Monat; Laser-Seite Richtung Top-10 optimieren; Hydrafacial-Cluster aufbauen; Stadtteil-Landingpages erstellen; GBP + relevantes Buchungsportal optimieren; Bewertungsstrategie einrichten; monatliches Reporting."],
        ["Premium SEO", "1.490 EUR / Monat", "Vollständige Betreuung: Alles aus dem Wachstumspaket; 4 Artikel pro Monat; Service-Seiten neu schreiben; Backlink-Aufbau; Tech SEO laufend; Konkurrenz-Monitoring."],
    ]
    s.append(table(offer, [58 * mm, 58 * mm, 152 * mm]))
    s.append(p("*Der Audit-Betrag (490 EUR) wird vollständig auf das Quick Fix Paket angerechnet. Effektiver Gesamtpreis: 690 EUR.", "Small"))
    s.append(p("Möchten Sie wissen, welche 3 Punkte auf Ihrer Website zuerst geprüft werden sollten? Senden Sie mir Ihre Website — ich schicke Ihnen eine kurze Ersteinschätzung."))
    s.append(p("MaxContentSEO", "BodyX"))
    s.append(p("Georg Stopfer", "BodyX"))
    s.append(p("georg@maxcontentseo.de", "BodyX"))
    s.append(p("maxcontentseo.de", "BodyX"))
    s.append(p("Stand: 2026 - Befunde basieren auf Live-Website-Analyse, Google-Suche, Konkurrenzrecherche, KI-gestützte Tiefenrecherche, Ubersuggest Site Audit, Rank Tracking, Competitor Analysis und Backlink-Daten.", "Small"))
    return s


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = make_doc(OUT)
    doc.build(story())
    print(OUT)


if __name__ == "__main__":
    main()
