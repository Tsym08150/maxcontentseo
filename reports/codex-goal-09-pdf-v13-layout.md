# Goal 09 — SEO_Audit_Showcase_v13 PDF Layout, 17.05.2026

## Geänderte Dateien

- `tools/generate_seo_audit_showcase_v13.py`
- `reports/codex-goal-09-pdf-v13-layout.md`

## Untracked Dateien

- `tools/generate_seo_audit_showcase_v13.py`
- `reports/codex-goal-09-pdf-v13-layout.md`

## Erzeugte Dateien außerhalb des Repos

- `C:\Users\MaxContentSeO\Downloads\SEO_Audit_Showcase_v13.pdf`
- `C:\Users\MaxContentSeO\Downloads\SEO_Audit_Showcase_v13.txt`
- `C:\Users\MaxContentSeO\Downloads\SEO_Audit_Showcase_v13_pages\*.png`
- `C:\Users\MaxContentSeO\Downloads\codex_tmp_pymupdf\` (temporäre Rendering-Bibliothek für PNG-QA)

## Was wurde geändert

- Es wurde keine separate HTML-/Markdown-Vorlage zur V12 gefunden. Die V12-PDF-Metadaten nennen `ReportLab PDF Library`; V13 wurde deshalb als reproduzierbarer ReportLab-Generator neu aufgebaut.
- Inhalt, Preise, Daten und Struktur wurden weitgehend aus V12 übernommen.
- Kapitel 10 und Kapitel 11 wurden als Landscape-Seiten mit breiteren Tabellen gesetzt.
- Tabellenzellen nutzen feste Spaltenbreiten, kleinere Tabellenschrift, mehr Padding und deaktiviertes Wort-Splitting.
- Alle Absatz- und Tabellenstyles wurden explizit linksbündig gesetzt.
- Künstliche Textjustierung, Word-Shrinkage, Hyphenation und manuelle `<br/>`-Zeilenumbrüche wurden deaktiviert bzw. entfernt.
- Die bekannten unsauberen Worttrennungen im Maßnahmenplan und in der Angebotstabelle wurden beseitigt.
- München-Reste in den angeforderten Keywords wurden anonymisiert:
  - `laser haarentfernung kosten [Großstadt]`
  - `laser haarentfernung schulung [Großstadt]`
- Der kaputte Pfad wurde als `/kategorie-seite-alt/` gesetzt.

## Was wurde bewusst nicht geändert

- Keine neuen SEO-Daten, Preise, Keywords oder Maßnahmen ergänzt.
- Keine neue fachliche Behauptung eingefügt.
- Bestehende Anonymisierung wurde beibehalten.
- Keine externen Fonts verwendet.

## Offene Fragen für Human Review

- Soll der neue Generator dauerhaft im Repo bleiben oder nach Abnahme entfernt werden?
- Soll das erzeugte PDF später zusätzlich in `assets/` abgelegt werden, damit `danke.html` direkt darauf verlinken kann?

## Asset- und Lizenzhinweise

- Keine neuen Bild-, Icon- oder Font-Assets.
- PDF wurde mit ReportLab und Systemschrift Helvetica erzeugt.

## Verification

- V12-Quelle gesucht in Repo und Downloads: keine separate Vorlage gefunden; PDF-Metadaten zeigen ReportLab.
- V13 erzeugt: `SEO_Audit_Showcase_v13.pdf`, 10 Seiten, ca. 29 KB.
- Seitengrößen geprüft:
  - Seiten 1-7: Portrait
  - Seiten 8-10: Landscape
- Textprüfung per `pypdf`:
  - Keine Treffer für `Erfahru ng`, `Markenkonsisten z`, `Ranking-Differenzieru ng`, `Click-Throug h`, `Branchenverzeich nis`, `Hautanalyse-Bl öcke`.
  - Keine Treffer für `laser haarentfernung kosten münchen`, `laser haarentfernung schulung münchen`, `[großstadt]` oder `/kategorie-seite￾alt/`.
  - Treffer bestätigt für `User-Erfahrung`, `Markenkonsistenz`, `Ranking-Differenzierung`, `Click-Through`, `Branchenverzeichnis`, `Hautanalyse-Blöcke`, `laser haarentfernung kosten [Großstadt]`, `laser haarentfernung schulung [Großstadt]`, `/kategorie-seite-alt/`.
- PNG-Render-QA:
  - Alle 10 Seiten mit PyMuPDF gerendert.
  - Kritische Seiten 8 und 10 visuell geprüft: Tabellen sind lesbar, Landscape, keine sichtbaren Wortzerreißungen in Maßnahmenplan und Angebotstabelle.
  - Nachkorrektur geprüft: Fließtext und Tabellen sind linksbündig gesetzt, ohne sichtbare Textjustierung oder Buchstabenabstände innerhalb von Wörtern.

## Lighthouse-Score

- Nicht relevant. Keine Website-Performance-Änderung.
