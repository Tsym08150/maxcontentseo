# Goal 22 — Impressum-PLZ fuer Places-Lookup (2026-05-20)

## Geaenderte Dateien

- `tools/places_lookup.ps1`
- `tools/places_lookup_from_impressum.ps1`
- `.claude/commands/audit-gbp.md`
- `reports/_stage1_scrape/impressum/bellapelle-de.md`
- `reports/_stage1_scrape/impressum/lingqi-muenchen-de.md`
- `reports/_stage1_scrape/impressum/vitaminbude-de.md`
- `reports/codex-goal-22-impressum-plz-places.md`

## Untracked Dateien

- `tools/places_lookup.ps1`
- `tools/places_lookup_from_impressum.ps1`
- `.claude/commands/audit-gbp.md`
- `reports/_stage1_scrape/impressum/bellapelle-de.md`
- `reports/_stage1_scrape/impressum/lingqi-muenchen-de.md`
- `reports/_stage1_scrape/impressum/vitaminbude-de.md`
- `reports/codex-goal-21-gbp-automation.md`
- `reports/codex-goal-22-impressum-plz-places.md`

## Was wurde geaendert

- `tools/places_lookup.ps1`: `Plz` ist jetzt optional. Der Aufruf `-PLZ` funktioniert ueber den Parameternamen case-insensitive. Wenn keine PLZ uebergeben wird, laeuft der Lookup ohne PLZ-Bonus weiter.
- `tools/places_lookup_from_impressum.ps1`: Neuer Wrapper liest einen Impressum-Scrape als UTF-8, extrahiert die erste deutsche PLZ per `\b\d{5}\b` und ruft danach `places_lookup.ps1` ohne Sheet-Schreibung auf.
- `.claude/commands/audit-gbp.md`: Additiver GBP-Flow dokumentiert jetzt den Wrapper-Aufruf mit Impressum-Scrape.
- `reports/_stage1_scrape/impressum/*.md`: Drei rohe Impressum-Scrape-Snippets fuer den Testlauf abgelegt.

## Was wurde bewusst nicht geaendert

- `.claude/commands/audit.md` wurde nicht angefasst.
- `docs/pipeline-v2.md` wurde nicht angefasst.
- `Tools/Firecrawl/firecrawl_score_engine.ps1` wurde nicht angefasst; die Datei existiert im Repo weiterhin nicht.
- Es wurde keine Sheet-Schreibung eingebaut.

## Offene Fragen fuer Human Review

- `lingqi-muenchen.de` loest per Firecrawl/DNS nicht auf; fuer den Impressum-Scrape wurde deshalb die verifizierte Live-Quelle `lingqi-tcm.com/impressum/` verwendet.
- Bei Bellapelle extrahiert das Impressum `22605`, Google Places scheint aber mit einer anderen Standort-PLZ zu matchen. Das erzeugt weiterhin `NAP_MATCH = konflikt`.
- Vitaminbude wurde mit Sheet-Stadt Hamburg getestet, der Impressum- und Places-Treffer liegt in Muenchen. Das ist als Review-Signal wichtig.

## Asset- und Lizenzhinweise

- Keine neuen Bilder, Fonts, Icons oder externen Assets verwendet.
- Genutzt wurden Firecrawl-Scrapes der jeweiligen Impressum-Seiten und die Google Places API ueber den lokalen Key in `tools/config.ps1`.

## Lighthouse-Score

- Nicht ausgefuehrt; Aenderung betrifft kein Frontend und keine auslieferbare Website-Performance.
