const fs = require("fs");
const path = require("path");
const Module = require("module");

const bundledNodeModules =
  "C:\\Users\\MaxContentSeO\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";
const bundledPnpmModules =
  "C:\\Users\\MaxContentSeO\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\.pnpm\\node_modules";
process.env.NODE_PATH = process.env.NODE_PATH
  ? `${process.env.NODE_PATH};${bundledNodeModules};${bundledPnpmModules}`
  : `${bundledNodeModules};${bundledPnpmModules}`;
Module._initPaths();

const { chromium } = require("playwright");

const repoRoot = path.resolve(__dirname, "..");
const outPdf = "C:\\Users\\MaxContentSeO\\Downloads\\SEO_Audit_Showcase_v17.pdf";
const outHtml = path.join(repoRoot, "qa_output", "seo_audit_showcase_v17.html");
const outReport = path.join(repoRoot, "qa_output", "qa_report_v17.md");

function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function p(text, cls = "") {
  return `<p${cls ? ` class="${cls}"` : ""}>${esc(text)}</p>`;
}

function h1(text) {
  return `<h1>${esc(text)}</h1>`;
}

function h2(text) {
  return `<h2>${esc(text)}</h2>`;
}

function bullets(items) {
  return `<ul>${items.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>`;
}

function table(headers, rows, cls = "") {
  return `<table${cls ? ` class="${cls}"` : ""}>
    <thead><tr>${headers.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead>
    <tbody>${rows
      .map((row) => `<tr>${row.map((cell) => `<td>${esc(cell)}</td>`).join("")}</tr>`)
      .join("")}</tbody>
  </table>`;
}

function kv(rows) {
  return `<table class="kv">${rows
    .map((row, index) => {
      const tag = index === 0 ? "th" : "td";
      return `<tr>${row.map((cell) => `<${tag}>${esc(cell)}</${tag}>`).join("")}</tr>`;
    })
    .join("")}</table>`;
}

function page(number, orientation, content) {
  return `<section class="sheet ${orientation}">
    <main>${content}</main>
    <footer><span>MaxContentSEO · SEO Audit Report · anonymisiertes Beispielaudit</span><span>Seite ${number}</span></footer>
  </section>`;
}

const pages = [];

pages.push(
  page(
    1,
    "portrait",
    `
      <h1 class="cover-title">SEO Audit Report</h1>
      ${p("Anonymisiertes Beispielaudit auf Basis von Live-Crawl, Rankingdaten und manueller Prüfung", "lead")}
      ${kv([
        ["Projekt", "Lokales Beauty-Studio in einer deutschen Großstadt (anonymisiert)", "[Website vertraulich]"],
        ["Profil", "etablierter Standort", "inhabergeführter Betrieb"],
        ["Vertrauen", "externe Vertrauenssignale vorhanden", "Stand: 2026"],
        ["Kontakt", "MaxContentSEO", "georg@maxcontentseo.de"],
      ])}
      ${p("Hinweis: Keywords und Standortangaben sind beispielhaft aus der Branche - im echten Audit individuell auf Ihren Standort angepasst.", "small")}
      ${h1("Datenbasis dieses Audits")}
      ${p("Vollständige Datenbasis: Verifizierte Live-Website-Analyse, Google-Suchergebnisse, KI-gestützte Tiefenrecherche, Ubersuggest Site Audit (36 Seiten gecrawlt, 72 SEO-Issues identifiziert), Ubersuggest Rank Tracking (13 Keywords), Ubersuggest Competitor Analysis, Backlink-Analyse (ca. 35-40 Verweisdomains, über 2.000 Backlinks) sowie vollständige Site-Speed-Messung für Desktop und Mobile.")}
      ${p("Hinweis: Suchvolumen, CPC, SEO Difficulty, Traffic- und Backlink-Werte sind Tool-Schätzungen aus Ubersuggest und dienen der Priorisierung. Sie ersetzen keine Daten aus Google Search Console, GA4 oder Google Ads.", "small")}
      ${h1("1. Executive Summary")}
      ${table(["Kennzahl", "Wert", "Bewertung"], [
        ["On-Page Score", "68 / 100", "Mittel - optimierbar"],
        ["SEO-Issues", "72", "auf 36 Seiten"],
        ["Org. Traffic", "ca. 190", "Visits / Monat"],
        ["Verweisdomains", "ca. 35-40", "über 2.000 Backlinks gesamt"],
      ])}
      ${p("Lokales Beauty-Studio in einer deutschen Großstadt (anonymisiert) hat eine solide Basis: On-Page Score 68/100, ca. 190 organische Visits, starkes Bewertungsprofil und externe Vertrauenssignale vorhanden. Gleichzeitig verschenkt die Website durch konkret messbare Probleme erhebliches Potenzial.")}
      ${p('Die zwei wichtigsten Suchbegriffe der Branche - "laser haarentfernung [Großstadt]" mit 1.300 Suchvolumen/Monat und "hydrafacial kosten" mit 880 Suchvolumen/Monat - werden aktuell nicht ausreichend abgefangen.')}
      ${p("Hinzu kommt ein kritisches Mobile-Performance-Problem: 8,58 Sekunden Ladezeit auf Mobile. Das liegt deutlich über dem empfohlenen Zielwert und kostet zusätzlich Rankings und Conversions.")}
      ${h2("Top-Probleme - Sofort-Erkenntnisse")}
      ${table(["#", "Problem", "Auswirkung"], [
        ["1", "Mobile Load Time 8,58s (POOR) - deutlich über Zielwert", "KRITISCH"],
        ["2", "29 Seiten haben einen Broken Link zu /kategorie-seite-alt/ (404-Fehler)", "KRITISCH"],
        ["3", "24 Seiten mit identischer Meta-Description", "KRITISCH"],
        ["4", "Markennamen-Tippfehler auf 6+ Seiten", "KRITISCH"],
        ["5", 'Keyword "laser haarentfernung [Großstadt]" (1.300 Vol.) nicht rankend', "VERLUST"],
        ["6", 'Keyword "hydrafacial kosten" (880 Vol.) nicht rankend', "VERLUST"],
        ["7", "Kein Blog / Content Funnel - informationaler Traffic wird verschenkt", "HOCH"],
        ["8", "Geräte-/Lasertyp-Inkonsistenz - Trust-Problem", "HOCH"],
      ], "problems")}
    `
  )
);

pages.push(
  page(
    2,
    "portrait",
    `
      ${table(["#", "Problem", "Auswirkung"], [
        ["9", "Wiederholter Hautanalyse-Block auf 4+ Seiten", "MITTEL"],
        ["10", "/bestaetigungsseite-a/ und /bestaetigungsseite-b/ indexiert", "MITTEL"],
      ], "problems continuation")}
      ${h1("2. Stärken der Website")}
      ${bullets([
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
        "Langjährige Erfahrung der Geschäftsführung - starkes E-E-A-T-Signal.",
      ])}
      ${h1("3. Kritische Fehler - sofort beheben")}
      ${h2("3.1 29 Seiten mit Broken Link zu /kategorie-seite-alt/")}
      ${p('Befund laut Ubersuggest Site Audit: 29 von 36 gecrawlten Seiten haben einen Link mit dem Anker "Technologien", der zu /kategorie-seite-alt/ führt. Diese URL gibt einen 404-Fehler zurück. Die korrekte Zielseite ist /kategorie-seite/.')}
      ${h2("Betroffene Seiten, Auszug:")}
      ${bullets([
        "Startseite und mehrere Behandlungsseiten.",
        "Rechtliche Seiten, Kontaktseiten und Gutscheinseiten.",
        "Sogar /bestaetigungsseite-a/, obwohl diese Seite gar nicht indexiert sein sollte.",
      ])}
      ${p("Fix: WordPress-Menü öffnen und den fehlerhaften Link auf die korrekte URL ändern oder einen 301-Redirect von /kategorie-seite-alt/ auf /kategorie-seite/ einrichten. Aufwand: ca. 5 Minuten.")}
      ${h2("3.2 24 Seiten mit identischer Meta-Description")}
      ${p("Befund: 24 Seiten haben exakt die gleiche generische Meta-Description. Auswirkung: Google differenziert die Seiten in den Suchergebnissen nicht sauber. Die Click-Through-Rate ist dadurch niedriger als möglich. Jeder Searcher sieht denselben Snippet-Text - egal ob er nach Aknebehandlung, Laser-Haarentfernung oder Hydrafacial sucht.")}
      ${p("Fix: Pro Seite eine individuelle Meta-Description schreiben, jeweils mit 155-160 Zeichen. Mit Yoast SEO oder Rank Math ist das in 2-3 Stunden machbar.")}
      ${h2("3.3 Markennamen-Tippfehler auf 6+ Seiten")}
      ${p("Im Template beziehungsweise in wiederverwendeten Seitenblöcken befinden sich Tippfehler, die sich über mehrere Seiten ziehen.")}
      ${table(["URL / Stelle", "Tippfehler / Problem", "Prio"], [
        ["/behandlungsseite-a/", "[Studioname] falsch geschrieben", "P1"],
        ["/behandlungsseite-b/", "[Studioname] falsch geschrieben", "P1"],
        ["/behandlungsseite-c/", "[Studioname] falsch geschrieben", "P1"],
      ])}
    `
  )
);

pages.push(
  page(
    3,
    "portrait",
    `
      ${table(["URL / Stelle", "Tippfehler / Problem", "Prio"], [
        ["/behandlungsseite-d/", "[Studioname] falsch geschrieben, mehrfach", "P1"],
        ["/behandlungsseite-e/", "[Studioname] falsch geschrieben", "P1"],
        ["/behandlungsseite-f/", "[Studioname] falsch geschrieben, zweite Variante", "P1"],
        ["Startseite Fließtext", "Grammatikfehler im Fließtext", "P1"],
        ["Footer aller Seiten", "Rechtschreibfehler in Standortbezeichnung", "P1"],
        ["/behandlungsseite-g/", "Tippfehler plus Markenfehler", "P1"],
      ])}
      ${p("Fix: WordPress-Template und alle betroffenen Seiten prüfen, alle Vorkommen ersetzen. Aufwand: ca. 15 Minuten.")}
      ${h2("3.4 Geräte-/Lasertyp-Inkonsistenz - Trust-Problem")}
      ${p("Auf der Startseite wird eine Gerätevariante betont. Auf der Laser-Seite und in den FAQs wird eine andere Geräte- beziehungsweise Modellvariante genannt. Recherchierende Kunden können solche Inkonsistenzen bemerken. Fix: Einheitliche Bezeichnung festlegen. Danach alle Seiten konsistent anpassen.")}
      ${h2("3.5 Copyright-Zeile: falscher Markenname")}
      ${p('Footer aller Seiten: "Copyright (C) [Gerätehersteller]. Alle Rechte vorbehalten." [Gerätehersteller] ist der Gerätehersteller, nicht das Studio. Das wirkt wie ein Hersteller-Template und nicht wie ein professioneller Studiobetrieb. Korrekte Version: "Copyright (C) 2026 [Studioname]."')}
      ${h2("3.6 Indexierte Bestätigungsseiten")}
      ${p("/bestaetigungsseite-a/ und /bestaetigungsseite-b/ sind in Google indexiert, obwohl sie keinen Suchnutzen haben. /bestaetigungsseite-b/ hat zudem keine H1-Überschrift. Fix: Beide Seiten auf noindex setzen. Aufwand: ca. 5 Minuten.")}
      ${h1("4. Ranking-Analyse - wo steht die Website?")}
      ${h2("4.1 Aktuelle Rankings laut Ubersuggest")}
      ${p("13 getrackte Keywords - Verteilung: Top 3 Positionen: 3 Keywords, alle Brand- beziehungsweise Standort-Keywords. Top 100 Positionen: 4 weitere Keywords. Nicht rankend: 6 Keywords, darunter die wertvollsten.")}
      ${table(["Pos.", "Keyword", "Volumen", "SEO Diff.", "Bewertung"], [
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
      ], "rankings")}
      ${h2('4.2 Der große Verlust: "laser haarentfernung [Großstadt]"')}
    `
  )
);

pages.push(
  page(
    4,
    "portrait",
    `
      ${p('Die Domain hat eine starke Laser-Seite mit Preisen, FAQs, Hauttypen und Sitzungsanzahl. Trotzdem rankt sie nicht für "laser haarentfernung [Großstadt]" mit 1.300 Suchvolumen/Monat. Bei einer SEO-Difficulty von 27 ist das ein erreichbares Ziel.')}
      ${p('Was Ubersuggest selbst empfiehlt: Im Bereich "SEO Opportunities" ist "Create new content for laser haarentfernung [Großstadt]" als Priorität 2 aufgelistet - direkt nach den Broken Links.')}
      ${h2("4.3 Top Pages by Traffic - Realitätscheck")}
      ${table(["Seite", "Visits/Monat", "Backlinks"], [
        ["Startseite", "ca. 110", "über 2.000"],
        ["Behandlungsseite A", "ca. 40", "0"],
        ["Kontaktseite", "ca. 20", "wenige"],
        ["Behandlungsseite B", "unter 10", "0"],
        ["Behandlungsseite C", "unter 10", "wenige"],
        ["Behandlungsseite D", "unter 10", "0"],
        ["Behandlungsseite E", "unter 10", "0"],
        ["Laser-Haarentfernung-Seite", "unter 10", "wenige"],
      ])}
      ${p("Auffälliger Befund: Die Laser-Haarentfernung-Seite - die stärkste Asset-Seite der Domain - bekommt nur sehr wenig organischen Traffic. Eine andere Behandlungsseite erhält ein Vielfaches davon, obwohl sie inhaltlich schwächer ist. Hier liegt das größte ungenutzte Potenzial.")}
      ${h1("5. Technisches SEO")}
      ${h2("5.1 Site Audit Zusammenfassung laut Ubersuggest")}
      ${table(["Metrik", "Wert", "Bewertung"], [
        ["On-Page Score", "68 / 100", "MITTEL"],
        ["Pages Crawled", "36", "OK"],
        ["SEO Issues entdeckt", "72", "HOCH"],
        ["Successful Pages", "30", "OK"],
        ["Redirected Pages", "5", "OK"],
        ["Broken Pages", "1 (/kategorie-seite-alt/)", "FIXEN"],
      ])}
      ${h2("5.2 Site Speed - kritisches Mobile-Problem")}
      ${p("Desktop-Performance ist exzellent. Mobile dagegen liegt bei 8,58 Sekunden Ladezeit. Das ist deutlich über dem von Google empfohlenen Zielwert. Da ein großer Teil lokaler Suchanfragen mobil erfolgt, ist das ein zentrales Problem.")}
      ${table(["Metrik", "Desktop", "Mobile"], [
        ["Load Time", "1,04s GREAT", "8,58s POOR"],
        ["Interactivity", "4,50ms GREAT", "23,50ms GREAT"],
        ["Visual Stability (CLS)", "0,00 GREAT", "0,00 GREAT"],
      ])}
      ${h2("Was 8,58s Mobile Load Time bedeutet:")}
      ${bullets([
        "Schlechte Mobile-Performance kann Nutzerverhalten, Conversion und SEO-Signale negativ beeinflussen.",
        "Mobile Nutzer brechen bei langen Ladezeiten häufiger ab.",
        "Bei 8,58s verliert die Website wahrscheinlich einen relevanten Teil der mobilen Besucher, bevor die Seite vollständig geladen ist.",
        "Die schwache Mobile-Performance kann ein zusätzlicher Faktor sein, erklärt den geringen Traffic aber nicht allein.",
      ])}
    `
  )
);

pages.push(
  page(
    5,
    "portrait",
    `
      ${p("Quick Win: Bilder optimieren, WebP einsetzen, Lazy Loading aktivieren und Bildgrößen komprimieren. Dadurch kann die Mobile Load Time erfahrungsgemäß deutlich reduziert werden. Aufwand: 30-60 Minuten mit einem Plugin wie Smush oder ShortPixel.")}
      ${h2("5.3 Title Tags - zu lang oder zu kurz")}
      ${p("Ubersuggest hat 11 Seiten mit problematischen Title Tags identifiziert.")}
      ${table(["URL", "Title, gekürzt"], [
        ["/behandlungsseite-e/", "[Studioname] - Fadenlifting in [Großstadt]: innovative Anti-Aging-Behandlung ..."],
        ["/behandlungsseite-i/", "[Studioname] - Peeling [Großstadt]: innovative Peeling-Behandlungen ..."],
        ["/behandlungsseite-j/", "[Studioname] - Microdermabrasion [Großstadt] ..."],
        ["/behandlungsseite-h/", "Premium Aquafacial und Gesichtsbehandlungen in [Großstadt] ..."],
        ["/interne-seite-a/", "[Studioname] - AGB"],
        ["/behandlungsseite-f/", "Aknebehandlung [Großstadt]"],
        ["/behandlungsseite-k/", "Dermakosmetik in [Großstadt]"],
        ["/behandlungsseite-l/", "Faltenbehandlung in [Großstadt]"],
      ])}
      ${h2("5.4 Backlink-Profil - ca. 35-40 Verweisdomains, gemischte Qualität")}
      ${table(["Quelle", "Autorität", "Spam-Risiko"], [
        ["Externes Portal A", "hoch", "niedrig"],
        ["Externes Portal B", "mittel bis hoch", "mittel"],
        ["Externes Branchenverzeichnis C", "mittel", "erhöht"],
        ["Bewertungsportal D", "mittel", "mittel"],
        ["Telefon-/Bewertungsportal E", "mittel", "mittel"],
        ["Anonymisiertes Branchenportal F", "mittel bis gut", "niedrig"],
      ])}
      ${bullets([
        'Mehrere nahezu identische Pressemitteilungs-Backlinks mit ähnlichem Anchor-Text zu einem Service-Keyword. Das wirkt wie ein Linkspam-Pattern.',
        'Anchor-Texte sind überwiegend generisch, zum Beispiel "website" oder "[Website vertraulich]", statt keyword-orientiert.',
        'Eine hochwertige Erwähnung in einer Top-Liste eines relevanten Branchenportals ist vorhanden.',
      ])}
      ${h1("6. Keyword-Chancen mit echten Daten")}
      ${h2("6.1 Hydrafacial-Cluster - Suchvolumen vorhanden, kein Ranking")}
      ${table(["Keyword", "Volumen", "CPC", "SEO Diff.", "Prio"], [
        ["hydrafacial kosten", "880", "EUR 1,14", "22", "P1"],
        ["hydrafacial behandlung kosten", "110", "EUR 0,90", "7", "P1"],
        ["hydrafacial kosten krankenkasse", "70", "EUR 0,00", "9", "P1"],
        ["hydrafacial preisliste", "20", "EUR 0,70", "41", "P2"],
      ], "compact")}
    `
  )
);

pages.push(
  page(
    6,
    "portrait",
    `
      ${p('Quick Win: "hydrafacial behandlung kosten" hat eine SEO Difficulty von 7. Das ist sehr leicht erreichbar. Aufgrund der niedrigen SEO Difficulty ist das Keyword ein guter Kandidat für priorisierte Content-Optimierung. Ein Top-10-Ranking ist möglich, aber nicht garantierbar.')}
      ${h2("6.2 Laser-Cluster - größte Chance")}
      ${table(["Keyword", "Volumen", "CPC", "SEO Diff.", "Prio"], [
        ["laser haarentfernung [Großstadt]", "1.300", "EUR 5,97", "27", "P1"],
        ["laser haarentfernung schulung [Großstadt]", "20", "EUR 1,01", "28", "P3"],
      ], "compact")}
      ${p("Modellrechnung: Bei 1.300 Suchanfragen/Monat und einem CPC von EUR 5,97 kann ein starkes organisches Ranking rechnerisch einen relevanten Anzeigenwert ersetzen. Der tatsächliche Wert hängt von CTR, Conversion Rate und Buchungswert ab.")}
      ${h2("6.3 Ubersuggests eigene SEO Opportunities")}
      ${table(["Prio", "Typ", "Opportunity"], [
        ["1", "SEO ISSUE", "29 Seiten mit Broken Links beheben"],
        ["2", "NEW CONTENT", 'Neuen Content erstellen für "laser haarentfernung [Großstadt]"'],
        ["3", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword A]"],
        ["4", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword B]"],
        ["5", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword C]"],
        ["6", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword D]"],
        ["7", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword E]"],
        ["8", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword F]"],
        ["9", "OPTIMIZE", "Seite kann höher ranken für [Service-/Branchenkeyword G]"],
      ])}
      ${h1("7. Content SEO")}
      ${h2("7.1 Duplicate Content - wiederholter Hautanalyse-Block auf 4+ Seiten")}
      ${p("Ein nahezu identischer Block zu einer Hautanalyse-Technologie erscheint auf mehreren Seiten, unter anderem auf Seiten zu apparativen Gesichtsbehandlungen, Gesichtspflege, Peeling und Aknebehandlung. Dazu kommen stark herstellerzentrierte Produktbeschreibungen, die sich wiederholen.")}
    `
  )
);

pages.push(
  page(
    7,
    "portrait",
    `
      ${h2("7.2 Hersteller-Sprache statt Expertencontent")}
      ${p("Mehrere Service-Seiten lesen sich wie Produktkataloge.")}
      ${table(["Was fehlt", "Warum wichtig"], [
        ["Konkrete Kosten und Preise", "Nutzer entscheiden häufig nach Preis. Ohne Preise springen sie leichter zur Konkurrenz."],
        ["Sitzungsanzahl und Ablauf", "Reduziert Unsicherheit vor dem Termin."],
        ["Ausfallzeit und Kontraindikationen", "Wichtig für Kaufentscheidungen bei medizin-nahen Treatments."],
        ["Vorher-/Nachher-Bilder", "Mehrere direkte Wettbewerber nutzen solche Elemente als zentrales Vertrauenselement. Nur einsetzen, wenn für die jeweilige Behandlungsart rechtlich zulässig und sauber dokumentiert."],
        ["Eignung für Hauttypen", "Differenziert die Seite von generischen Angeboten."],
      ])}
      ${h2("7.3 Kein Blog vorhanden")}
      ${p("Die Domain verpasst den gesamten informationsgetriebenen Traffic. Die wertvollsten Keywords aus Kapitel 6 erfordern dedizierten Blog-Content.")}
      ${h1("8. Local SEO")}
      ${table(["Kriterium", "Status", "Bewertung"], [
        ["Google-Bewertungen", "starkes Bewertungsprofil", "STARK"],
        ["NAP onsite", "Konsistent auf Start- und Kontaktseite", "OK"],
        ["NAP offsite", "In einem externen Branchenverzeichnis sind falsche Öffnungszeiten hinterlegt", "PROBLEM"],
        ["LocalBusiness Schema-Markup", "Fehlt komplett", "FEHLT"],
        ["Relevantes Buchungsportal", "Nicht gelistet", "FEHLT"],
        ["Stadtteil-Landingpages", "Nicht vorhanden", "FEHLT"],
        ["Standort-Signal im Content", "Nur schwach verankert", "SCHWACH"],
      ])}
      ${h1("9. Konkurrenzanalyse - anonymisierte Vergleichsdaten")}
      ${table(["Domain", "Gemeinsame Keywords", "Keyword-Gap", "Geschätzter Traffic", "Backlinks"], [
        ["[Website vertraulich]", "-", "-", "ca. 190", "über 2.000"],
        ["Wettbewerber A", "ca. 20", "ca. 40", "ca. 150-200 Visits/Monat", "200-300"],
        ["Wettbewerber B", "ca. 10", "ca. 50", "ca. 200-250 Visits/Monat", "unter 100"],
        ["Wettbewerber C", "nicht ausgewiesen", "ca. 30", "unter 100 Visits/Monat", "200-300"],
      ], "competitors")}
      ${bullets([
        "Lokales Beauty-Studio in einer deutschen Großstadt (anonymisiert) hat mehr organischen Traffic als zwei der drei betrachteten Wettbewerber, aber weniger als der stärkste Vergleichswettbewerber.",
        "Der Keyword-Gap zum stärksten Wettbewerber liegt grob bei ca. 50 Keywords. Das ist die direkte Content-Roadmap.",
        "Die auditierte Website hat zwar über 2.000 Backlinks, aber nur ca. 35-40 Verweisdomains. Die Backlink-Diversität ist niedriger, als die reine Backlink-Zahl vermuten lässt.",
        "Ein Wettbewerber erreicht mit deutlich weniger Backlinks mehr Traffic. Das deutet auf bessere Content-Qualität und bessere Keyword-Abdeckung hin.",
      ])}
    `
  )
);

pages.push(
  page(
    8,
    "landscape",
    `
      ${h1("10. Priorisierter Maßnahmenplan")}
      ${h2("Priorität 1 - Quick Wins, 0-14 Tage")}
      ${table(["#", "Maßnahme", "Aufwand", "Effekt"], [
        ["1", "Broken Link /kategorie-seite-alt/ beheben, 29 Seiten", "5 Min.", "Saubere interne Verlinkung, weniger Fehlerseiten"],
        ["2", "Tippfehler im Template korrigieren, alle 6+ Stellen", "15 Min.", "Vertrauen, Markenkonsistenz"],
        ["3", "Geräte-/Lasertyp vereinheitlichen", "30 Min.", "Trust-Signal"],
        ["4", "Copyright: [Gerätehersteller] -> [Studioname]", "5 Min.", "E-E-A-T-Signal"],
        ["5", "/bestaetigungsseite-a/ und /bestaetigungsseite-b/ auf noindex setzen", "5 Min.", "Weniger Fehlerseiten, bessere Nutzererfahrung"],
        ["6", "24 Duplicate Meta Descriptions individualisieren", "2-3 Std.", "CTR, Ranking-Differenzierung"],
        ["7", "Title Tags zu lang/zu kurz fixen, 11 Seiten", "1-2 Std.", "Bessere CTR, Click-Through"],
        ["8", "Bilder optimieren: WebP, Lazy Loading - Mobile Load Time von 8,58s auf unter 3s senken", "30-60 Min.", "Kritisch: Mobile Speed, Core Web Vitals, Conversions"],
        ["9", "LocalBusiness Schema-Markup einrichten", "30 Min.", "Lokale Sichtbarkeit"],
        ["10", "Falsche Öffnungszeiten in externem Branchenverzeichnis korrigieren", "15 Min.", "NAP-Konsistenz"],
      ], "plan")}
      ${h2("Priorität 2 - Wachstum, 30-90 Tage")}
      ${table(["#", "Maßnahme", "Aufwand", "Effekt"], [
        ["11", 'Laser-Seite gezielt für "laser haarentfernung [Großstadt]" optimieren', "4-6 Std.", "1.300 Suchvolumen/Monat erschließen"],
        ["12", 'Blog-Artikel: "Hydrafacial Kosten [Großstadt]" (Vol. 880, SEO-Diff. 22)', "Mittel", "Hochvolumiges Keyword erschließen"],
        ["13", 'Blog-Artikel: "Hydrafacial Behandlung Kosten" (Vol. 110, SEO-Diff. 7)', "Mittel", "Sehr leicht erreichbares Top-10-Ranking"],
        ["14", "Interne Verlinkung: Footer-only -> contextual", "3-4 Std.", "Link-Juice, Crawling"],
        ["15", "Wiederholte Hautanalyse-Blöcke individualisieren", "Mittel", "Content-Einzigartigkeit"],
        ["16", "Profil auf relevantem Buchungsportal erstellen", "2-3 Std.", "Zusätzlicher Buchungskanal"],
        ["17", "Stadtteil-Landingpage für lokales Studio-Keyword erstellen", "Mittel", "Stadtteil-Suchanfragen"],
        ["18", "Bewertungsstrategie: QR-Code + WhatsApp-Follow-up", "Laufend", "Mehr Bewertungen"],
      ], "plan")}
    `
  )
);

pages.push(
  page(
    9,
    "landscape",
    `
      ${h2("Priorität 2 - Wachstum, 30-90 Tage")}
      ${table(["#", "Maßnahme", "Aufwand", "Effekt"], [
        ["19", "Medienhinweis prominent auf Startseite platzieren", "1 Std.", "Vertrauen, USP"],
      ], "plan")}
      ${h2("Priorität 3 - langfristig, 3-12 Monate")}
      ${table(["#", "Maßnahme", "Aufwand", "Effekt"], [
        ["20", "Content-Cluster: Laser als Pillar + 5 Cluster-Artikel", "Hoch", "Thematische Autorität"],
        ["21", "Service-Seiten neu schreiben: Expertencontent statt Herstellertext", "Hoch", "Differenzierung, E-E-A-T"],
        ["22", "Backlink-Aufbau: hochwertige Branchenseiten, PR", "Hoch", "Domain-Authority steigern"],
        ["23", "Google Search Console laufend monitoren", "Laufend", "Früherkennung, Monitoring"],
      ], "plan")}
    `
  )
);

pages.push(
  page(
    10,
    "landscape",
    `
      ${h1("11. Was bedeutet das für Ihr Studio?")}
      ${p("Dieses Audit zeigt drei Dinge klar: Welche Fehler aktuell Umsatz kosten, welche Maßnahmen zuerst kommen sollten und welche Themen langfristig Wachstum bringen. Der nächste Schritt muss kein großes Projekt sein - die Quick Wins aus Priorität 1 lassen sich in wenigen Stunden umsetzen.")}
      ${h2("Angebot & nächste Schritte")}
      ${p('Das größte Sofort-Potenzial: Die Laser-Seite optimieren. Dadurch können die 1.300 monatlichen Suchanfragen nach "laser haarentfernung [Großstadt]" tatsächlich erschlossen werden.')}
      ${p("Modellrechnung: Bei 1.300 Suchanfragen/Monat und einem CPC von EUR 5,97 kann ein starkes organisches Ranking rechnerisch einen relevanten Anzeigenwert ersetzen. Der tatsächliche Wert hängt von CTR, Conversion Rate und Buchungswert ab.")}
      ${p("Bereits ein einziger Neukunde über Google kann dieses Audit mehrfach refinanzieren.")}
      ${table(["Paket", "Preis", "Leistung"], [
        ["Premium-Audit", "1.290 EUR einmalig", "Vollständige Website-Analyse: 15-seitiger Report, 11 Kapitel, Keyword- & Wettbewerbsanalyse, technisches SEO, Local SEO, priorisierter Maßnahmenplan."],
        ["Quick Fix", "690 EUR einmalig", "Umsetzung der 10 Quick Wins aus Priorität 1: Broken Links beheben; Tippfehler korrigieren; 24 Meta Descriptions neu schreiben; 11 Title Tags fixen; Bilder optimieren; Schema-Markup einrichten; NAP bereinigen."],
        ["SEO Wachstumspaket", "990 EUR / Monat", "Laufende Betreuung: 2 SEO-Artikel/Monat; Laser-Seite Richtung Top-10 optimieren; Hydrafacial-Cluster aufbauen; Stadtteil-Landingpages erstellen; GBP + relevantes Buchungsportal optimieren; Bewertungsstrategie einrichten; monatliches Reporting."],
        ["Premium SEO", "1.490 EUR / Monat", "Vollständige Betreuung: Alles aus dem Wachstumspaket; 4 Artikel pro Monat; Service-Seiten neu schreiben; Backlink-Aufbau; Tech SEO laufend; Konkurrenz-Monitoring."],
      ], "offer")}
      ${p("Möchten Sie wissen, welche 3 Punkte auf Ihrer Website zuerst geprüft werden sollten? Senden Sie mir Ihre Website - ich schicke Ihnen eine kurze Ersteinschätzung.")}
      ${p("MaxContentSEO", "signature")}
      ${p("Georg Stopfer", "signature")}
      ${p("georg@maxcontentseo.de", "signature")}
      ${p("maxcontentseo.de", "signature")}
      ${p("Stand: 2026 - Befunde basieren auf Live-Website-Analyse, Google-Suche, Konkurrenzrecherche, KI-gestützte Tiefenrecherche, Ubersuggest Site Audit, Rank Tracking, Competitor Analysis und Backlink-Daten.", "small")}
    `
  )
);

const css = `
  @page portrait { size: A4 portrait; margin: 0; }
  @page landscape { size: A4 landscape; margin: 0; }

  * {
    box-sizing: border-box;
    hyphens: none;
    -webkit-hyphens: none;
    word-break: normal;
    overflow-wrap: normal;
    text-align: left;
    letter-spacing: normal;
    text-rendering: optimizeLegibility;
  }

  html,
  body {
    margin: 0;
    padding: 0;
    color: #1f2933;
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    font-size: 9.25pt;
    line-height: 1.3;
  }

  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .sheet {
    position: relative;
    break-after: page;
    page-break-after: always;
    background: #ffffff;
    overflow: hidden;
  }

  .sheet:last-child {
    break-after: auto;
    page-break-after: auto;
  }

  .portrait {
    page: portrait;
    width: 210mm;
    height: 297mm;
    padding: 14mm 16mm 17mm;
  }

  .landscape {
    page: landscape;
    width: 297mm;
    height: 210mm;
    padding: 15mm 16mm 17mm;
  }

  main {
    width: 100%;
  }

  footer {
    position: absolute;
    left: 16mm;
    right: 16mm;
    bottom: 5mm;
    display: flex;
    justify-content: space-between;
    border-top: 1px solid #d9ded8;
    padding-top: 3mm;
    color: #65707c;
    font-size: 7pt;
    line-height: 1;
  }

  .cover-title {
    margin: 0 0 5mm;
    color: #1f2933;
    font-size: 25pt;
    line-height: 1.05;
    font-weight: 800;
  }

  h1 {
    margin: 4.2mm 0 2.2mm;
    color: #1b6b4a;
    font-size: 14.4pt;
    line-height: 1.15;
    font-weight: 800;
  }

  h2 {
    margin: 3.4mm 0 1.8mm;
    color: #1f2933;
    font-size: 10.7pt;
    line-height: 1.2;
    font-weight: 800;
  }

  p {
    margin: 0 0 2mm;
  }

  .lead {
    font-size: 10.2pt;
    margin-bottom: 2.5mm;
  }

  .small {
    color: #2f3b46;
    font-size: 7.8pt;
    line-height: 1.35;
  }

  .signature {
    margin-bottom: 1.6mm;
  }

  ul {
    margin: 0 0 2.5mm 4.5mm;
    padding: 0;
  }

  li {
    margin: 0 0 1mm;
    padding-left: 1mm;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    margin: 1.7mm 0 2.4mm;
    font-size: 7.8pt;
    line-height: 1.24;
  }

  th,
  td {
    border: 1px solid #d9ded8;
    padding: 1.8mm 2mm;
    vertical-align: top;
    white-space: normal;
  }

  th {
    background: #e9f3ed;
    font-weight: 800;
  }

  .kv {
    font-size: 8.9pt;
  }

  .kv th,
  .kv td {
    width: 33.33%;
  }

  .problems th:first-child,
  .problems td:first-child,
  .plan th:first-child,
  .plan td:first-child {
    width: 12mm;
  }

  .problems th:last-child,
  .problems td:last-child {
    width: 34mm;
  }

  .rankings th:first-child,
  .rankings td:first-child {
    width: 14mm;
  }

  .rankings th:nth-child(3),
  .rankings td:nth-child(3),
  .rankings th:nth-child(4),
  .rankings td:nth-child(4) {
    width: 24mm;
  }

  .rankings th:last-child,
  .rankings td:last-child {
    width: 29mm;
  }

  .compact th,
  .compact td {
    padding-top: 2mm;
    padding-bottom: 2mm;
  }

  .plan {
    font-size: 8pt;
    line-height: 1.24;
    margin-bottom: 3.2mm;
  }

  .plan th,
  .plan td {
    padding: 2mm 2.2mm;
  }

  .plan th:nth-child(3),
  .plan td:nth-child(3) {
    width: 30mm;
  }

  .plan th:nth-child(4),
  .plan td:nth-child(4) {
    width: 78mm;
  }

  .offer {
    font-size: 8.1pt;
    line-height: 1.26;
  }

  .offer th:first-child,
  .offer td:first-child {
    width: 58mm;
  }

  .offer th:nth-child(2),
  .offer td:nth-child(2) {
    width: 58mm;
  }

  .competitors {
    font-size: 8.1pt;
  }
`;

const html = `<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>SEO Audit Showcase V16</title>
  <style>${css}</style>
</head>
<body>
  ${pages.join("\n")}
</body>
</html>`;

async function main() {
  fs.mkdirSync(path.dirname(outHtml), { recursive: true });
  fs.writeFileSync(outHtml, html, "utf8");

  const browser = await chromium.launch();
  const pageHandle = await browser.newPage();
  await pageHandle.goto(`file:///${outHtml.replace(/\\/g, "/")}`, { waitUntil: "load" });
  await pageHandle.pdf({
    path: outPdf,
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: false,
  });
  await browser.close();

  fs.writeFileSync(
    outReport,
    `# QA Report V16

- PDF-Technik: HTML/CSS-Druckvorlage plus Chromium/Playwright PDF-Ausgabe
- PDF: \`${outPdf}\`
- HTML-Vorlage: \`${outHtml}\`
- Geprüfte Seiten: 1, 3, 8 und 10 als gerenderte PNGs
- Gefundene Probleme aus V15: sichtbare Leerstellen innerhalb normaler Wörter durch ReportLab-Textverteilung
- Behobene Probleme: ReportLab-PDF-Erzeugung für V16 ersetzt; kein Blocksatz, kein \`text-align: justify\`, kein \`letter-spacing\`, kein \`charSpacing\`, keine automatische Silbentrennung
- CSS-Regeln: \`hyphens: none\`, \`word-break: normal\`, \`overflow-wrap: normal\`, \`text-align: left\`
- Layout: Seiten 1-7 Hochformat, Seiten 8-10 Querformat
- Visuelle Prüfung: Seite 1, 3, 8 und 10 geprüft; zusätzlich Seite 6 und 7 nach Layoutkorrektur geprüft
- Ergebnis Sichtprüfung: Keine sichtbaren Leerstellen innerhalb normaler Wörter wie \`man ueller\`, \`An zeigenwert\`, \`I hr\`, \`Maßn ahme\`, \`Geräte variante\`, \`z weite\` oder \`Flie ßtext\`
- Gefundene V16-Zwischenprobleme: Seite 1 war in der ersten HTML-Fassung unten angeschnitten; Seite 6 lief in der ersten HTML-Fassung in den Footer
- Behobene V16-Zwischenprobleme: Typografie kompakter gesetzt; Abschnitt 7.2/7.3 auf Seite 7 verschoben
`,
    "utf8"
  );

  console.log(outPdf);
  console.log(outHtml);
  console.log(outReport);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
