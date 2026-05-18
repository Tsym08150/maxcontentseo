# Blog-Screenshots Schritt-für-Schritt — 2026-05-18

## Geänderte Dateien

- `blog/google-bewertung-loeschen.html`
- `reports/codex-blog-images.md`

## Untracked Dateien

- `reports/codex-blog-images.md`

## Was wurde geändert

- `blog/google-bewertung-loeschen.html`
  - Die alten lokalen WordPress-Exportpfade im Schritt-für-Schritt-Abschnitt wurden durch die gewünschten Asset-Pfade ersetzt.
  - Nach `Rezension auswählen und melden` wurden die Screenshots A und B eingebunden:
    - `/assets/schritt-screenshot-a.png`
    - `/assets/schritt-screenshot-b.png`
  - Nach `Status im Tool prüfen` wurde Screenshot C eingebunden:
    - `/assets/schritt-screenshot-c.png`
  - Alle drei Bilder haben die vorgegebenen `alt`-Texte und den vorgegebenen Inline-Style.

## Was wurde bewusst nicht geändert

- Bestehende Meta- und Schema-Bild-URLs im `<head>` wurden nicht geändert, weil der Auftrag nur die Bilder im Schritt-für-Schritt-Abschnitt betraf.
- Keine Texte, Überschriften oder Layout-Struktur des Artikels geändert.
- Kein Commit, kein Push, kein Deployment.

## Offene Fragen für Human Review

- Keine.

## Asset- und Lizenzhinweise

- Die drei Screenshot-Dateien waren nach `git pull origin main` bereits unter `assets/` vorhanden:
  - `assets/schritt-screenshot-a.png`
  - `assets/schritt-screenshot-b.png`
  - `assets/schritt-screenshot-c.png`

## Lighthouse-Score

- Nicht neu gemessen, da nur drei vorhandene lokale Bilder im Blogartikel referenziert wurden.
- Lokale Prüfung: Alle drei Asset-URLs liefern HTTP 200.
