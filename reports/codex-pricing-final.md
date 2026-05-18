# Pricing Final — 2026-05-18

## Geänderte Dateien

- `index.html`
- `reports/codex-pricing-final.md`

## Untracked Dateien

- `reports/codex-pricing-final.md`

## Was wurde geändert

- `index.html`
  - Pricing-Sektion vollständig neu aufgebaut.
  - Block `Einmaliger Einstieg` mit drei Karten ergänzt:
    - Kostenlose Erstanalyse für `0€`
    - SEO-Audit für `499€`
    - Premium-Audit für `1.299€` mit `Empfohlen`-Badge und grünem Rahmen
  - Hinweis unter Block 1 ergänzt: `Nach dem Audit optional: Quick Fix — Umsetzung der Top-3-Hebel für 699€.`
  - Block `Laufende Betreuung · Monatlich kündbar` mit SEO-Betreuung und Premium aktualisiert.
  - Block `Einzelne Blogartikel · Ohne Abo` mit 1 Blogartikel und 3 Artikel-Paket ergänzt.
  - Fußzeile `Keine Mindestlaufzeit · Alle Preise zzgl. MwSt.` beibehalten.
  - Pricing-CSS angepasst:
    - Karten verwenden `display: flex` und `flex-direction: column`.
    - Feature-Listen verwenden `flex: 1`.
    - CTA-Buttons haben `margin-top: 1rem`.
    - Dreispaltiger Desktop-Modifier für den ersten Pricing-Block ergänzt.
    - Sekundärer Kartenhintergrund und kleine Hinweisbox ergänzt.

## Was wurde bewusst nicht geändert

- Keine anderen Sections außer der Pricing-Sektion geändert.
- Keine Links, Dateinamen, globalen Assets oder externen Ressourcen geändert.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Bitte visuell prüfen, ob die Kartenhöhe und Spaltenwirkung dem gewünschten Muster entspricht.

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Fonts, Icons oder externen Assets hinzugefügt.

## Lighthouse-Score

- Nicht neu gemessen, da keine neuen externen Assets oder Skripte ergänzt wurden.
- Lokale Browser-Prüfung: `http://127.0.0.1:8080/#pricing` lädt die Pricing-Sektion, alle neuen Texte sind im DOM vorhanden, Console-Logs für `error`/`warn` waren leer.
- Textprüfung in `index.html`: alle geforderten Preise, Labels, Features, CTAs und Fußzeile gefunden.
