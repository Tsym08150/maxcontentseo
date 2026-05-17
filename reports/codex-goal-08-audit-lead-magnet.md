# Goal 08 — Audit-Beispiel, Lead-Magnet und alte URL, 17.05.2026

## Geänderte Dateien

- `audit-beispiel.html`
- `index.html`
- `danke.html`
- Redirect-Seite für die alte Audit-URL
- `assets/kosmetikstudio-muenchen.png`
- `reports/codex-link-audit.md`
- `reports/codex-goal-asset-check-card-images.md`
- `reports/codex-hotfix-card-images.md`
- `reports/codex-hotfix-links-images.md`
- `reports/codex-goal-08-audit-lead-magnet.md`

## Untracked Dateien

- `assets/kosmetikstudio-muenchen.png`
- `danke.html`
- Redirect-Seite für die alte Audit-URL
- `reports/codex-goal-08-audit-lead-magnet.md`

## Was wurde geändert

- `audit-beispiel.html`
  - H1 auf den vorgegebenen SEO-Audit-Titel für Kosmetikstudios geändert.
  - CTA-Block direkt nach dem Hinweis zu den 35+ Befunden eingefügt.
  - Datenpunkt zur mobilen Ladezeit auf den mobilen LCP-Wert mit Google-Schwelle präzisiert.
  - Suchanfragen-Hinweis um die Ubersuggest-Schätzung mit April 2026 ergänzt.
  - Datenquelle auf `KI-gestützte Tiefenrecherche` geändert.
  - Formular auf Formspree-Endpoint, `id="formular"`, POST-Methode, Name/E-Mail-Felder, `_next` und neuen Buttontext angepasst.

- `index.html`
  - Startseiten-Card und Bildreferenz von der alten Beauty-Bezeichnung auf `Kosmetikstudio München` geändert.

- `danke.html`
  - Neue Danke-/Download-Seite mit Nav, Footer, Sie-Form-H1 und Download-Link auf `assets/audit-beispiel.pdf` angelegt.

- Redirect-Seite für die alte Audit-URL
  - Alte URL als statische Meta-Refresh-Seite auf `audit-beispiel.html` angelegt.

- `assets/kosmetikstudio-muenchen.png`
  - Vorhandenes lokales Card-Asset auf neutralen Dateinamen umbenannt.

- Reports
  - Alte Beauty-Begriffe in bestehenden HTML/MD-Treffern bereinigt.

## Was wurde bewusst nicht geändert

- Kein Commit und kein Push, entsprechend der bestätigten Vorgabe und AGENTS.md.
- Der Redirect-Ordner behält bewusst den alten Slug im Ordnernamen, weil genau diese alte URL weiterleiten soll.
- `assets/audit-beispiel.pdf` wurde nicht erstellt, weil kein PDF-Asset im Repo vorhanden ist und kein neues PDF angefordert oder geliefert wurde.
- Der `_next`-Wert wurde als relativer Pfad `danke.html` gesetzt, weil die Aufgabenregeln relative Pfade verlangen.

## Offene Fragen für Human Review

- Bitte `assets/audit-beispiel.pdf` ergänzen, damit der Download-Button auf `danke.html` nicht ins Leere führt.
- Falls Formspree zwingend einen root-relativen oder absoluten Redirect erwartet, `_next` nach Review entsprechend anpassen.

## Asset- und Lizenzhinweise

- Keine externen Fonts, Bilder oder Icons hinzugefügt.
- Das vorhandene lokale PNG-Asset wurde nur umbenannt.
- Das erwartete PDF-Asset fehlt aktuell im Repo.

## Verification

- Suche in HTML/MD nach den alten Beauty-Begriffen: keine Treffer im Date Inhalt.
- Dateinamen geprüft: Nur der Redirect-Ordner enthält bewusst noch den alten URL-Slug.
- Live-Seiten-Brand-Voice-Check auf verbotene Begriffe und Du-Form: keine Treffer in `audit-beispiel.html`, `danke.html`, Redirect-Seite und `index.html`.
- Externe-Font-Check auf den neuen/geänderten Seiten: keine Treffer.
- Lokaler HTTP-Check:
  - `/audit-beispiel.html` → `200 OK`
  - `/danke.html` → `200 OK`
  - alte Audit-URL → `200 OK`
- Lokaler Linkcheck meldet nur `danke.html -> assets/audit-beispiel.pdf`, weil das PDF-Asset fehlt.

## Lighthouse-Score

- Nicht gemessen. Die Änderung betrifft statisches HTML/CSS ohne neue externe Fonts oder Skripte.
