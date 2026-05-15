# Goal Cases V1 — 15.05.2026

## 1. Goal-Bezeichnung und Datum
- Aufbau einer zweistufigen Cases-Struktur nach dem gewünschten Muster:
  - `cases.html` als Übersicht
  - `cases/lingqi.html` als Detailseite
- Zusätzlich: Hero-Grid-Fix in `index.html` bestätigt und im neuen Flow berücksichtigt
- Datum: 15.05.2026

## 2. Geänderte Dateien
- `D:\AITools\maxcontentseo\index.html`
- `D:\AITools\maxcontentseo\cases.html`
- `D:\AITools\maxcontentseo\cases\lingqi.html`

## 3. Untracked Dateien
- `D:\AITools\maxcontentseo\reports\codex-goal-cases-v1.md`
- `D:\AITools\maxcontentseo\reports\codex-goal-rebuild-v1b-hero-fix.md`

## 4. Was wurde geändert
- `index.html`
  - Bestehender LingQi-Teaser um CTAs auf `cases/lingqi.html` und `cases.html` ergänzt
  - Hero-Grid-Fix bleibt aktiv:
    - Desktop-Grid `minmax(0, 1fr) minmax(0, 420px)`
    - H1 `max-width: 100%`
- `cases.html`
  - Neue Cases-Übersichtsseite angelegt
  - Hero mit Einordnung des öffentlich verfügbaren Case-Bereichs gebaut
  - Card für den einzigen belegten Case `LingQi — TCM Head Spa München`
  - Lead-Magnet-Bereich unter dem Card-Grid eingefügt:
    - „So sieht ein Premium-Audit aus“
    - E-Mail-Formular ohne `action`-Attribut
- `cases/lingqi.html`
  - Neue Detailseite für den LingQi-Case angelegt
  - Struktur mit Hero, Executive Summary, Ausgangslage, Ergebnis, Audit-Inhalten und CTA umgesetzt
  - Nur belegte Inhalte aus vorhandenem Repo-Material verwendet

## 5. Was wurde bewusst nicht geändert
- Kein `showcase/`-Pfad verwendet; nur `cases/`
- Keine neue Kundenstimme oder neues Testimonial erfunden
- Keine neuen Case-Zahlen außerhalb der bereits belegten Inhalte ergänzt
- Keine Form-Integration mit Backend oder `action`-Attribut eingebaut

## 6. Offene Fragen für Human Review
- Bitte prüfen, ob die Cases-Übersicht inhaltlich schon nah genug an der gewünschten späteren Bibliothek ist oder ob dort später noch mehr redaktionelle Einordnung gewünscht ist
- Die Detailseite nutzt bewusst das vorhandene Georg-Foto als lokales, lizenziertes Asset. Falls später ein projektbezogeneres Visual gewünscht ist, braucht es ein eigenes Repo-Asset

## 7. Asset- und Lizenzhinweise
- Nur System-Fonts
- Nur lokales Bild `D:\AITools\maxcontentseo\assets\georg.jpg`
- Keine externen Logos, Fonts oder Bilder
- Platzhalter-/UI-Elemente ausschließlich via HTML/CSS

## 8. Lighthouse-Score
- Nicht gemessen in diesem Run

## Smoke-Test / QA
- Lokaler Server aufgerufen für:
  - `/`
  - `/cases.html`
  - `/cases/lingqi.html`
- Geprüft:
  - Titel vorhanden
  - keine `action`-Attribute in den Formularen
  - neue Cases-Pfade funktionieren

## Screenshots
- Overview Desktop: `C:\Users\MaxContentSeO\maxcontentseo-codex-assets\outputs\cases-overview-desktop.png`
- Overview Mobile: `C:\Users\MaxContentSeO\maxcontentseo-codex-assets\outputs\cases-overview-mobile.png`
- LingQi Desktop: `C:\Users\MaxContentSeO\maxcontentseo-codex-assets\outputs\cases-lingqi-desktop.png`
- LingQi Mobile: `C:\Users\MaxContentSeO\maxcontentseo-codex-assets\outputs\cases-lingqi-mobile.png`
