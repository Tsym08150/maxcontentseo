# Goal: Hotfix Links und Cards — 2026-05-16

## Geänderte Dateien
- `blog/google-bewertung-loeschen.html`
- `blog/lingqi-haarausfall.html`
- `branchen/kosmetikstudios.html`
- `index.html`
- `blog/index.html`
- `reports/codex-hotfix-links-images.md`

## Untracked Dateien
- `reports/codex-hotfix-links-images.md`
- `reports/codex-link-audit.md` war bereits vor diesem Run untracked.

## Was wurde geändert
- `blog/google-bewertung-loeschen.html`
  - Canonical auf `https://maxcontentseo.de/blog/google-bewertung-loeschen.html` gesetzt.
  - `og:url` auf `https://maxcontentseo.de/blog/google-bewertung-loeschen.html` gesetzt.
  - WordPress-`meta name="generator"` entfernt.
  - Alte WordPress-Anchor-Links im Inhaltsverzeichnis auf reine `#anchor`-Links umgestellt.
  - Alte WordPress-Navigation und Footer-Links auf lokale Ziele bzw. `../index.html#kontakt`, `../index.html#impressum`, `../index.html#datenschutz` umgestellt.
  - Alte WordPress-`href`-Reste aus RSS/oEmbed/API/Shortlink/Modulepreload-Tags entfernt.
  - Facebook-, Instagram- und X-Social-Links entfernt.
- `blog/lingqi-haarausfall.html`
  - Canonical und `og:url` für die lokale Blog-URL ergänzt.
  - Kein WordPress-Generator-Tag vorhanden; daher nichts zu entfernen.
- `branchen/kosmetikstudios.html`
  - `mailto:maxcontentseo.de` zu `mailto:georg@maxcontentseo.de` korrigiert.
- `index.html`
  - Haarausfall-Card-Titel auf den gewünschten vollständigen Titel geändert.
- `blog/index.html`
  - Haarausfall-Card-Titel auf den gewünschten vollständigen Titel geändert.

## Was wurde bewusst nicht geändert
- Keine Commits, Pushes oder Deployments.
- Die gewünschten Card-Bilder `assets/kosmetikstudio-muenchen.png` und `assets/haarausfall-stress.png` wurden nicht eingebunden, weil beide Dateien lokal nicht existieren.
- Es wurden keine neuen Bilddateien erzeugt oder hinzugefügt, da dafür keine Asset-Lizenz im Repo vorliegt.
- `cases.html` und `cases/lingqi.html` wurden nicht geändert, weil dort keine Medical-Beauty- oder Haarausfall-Blog-Card mit den genannten Bild-/Titelstellen vorhanden ist.

## Offene Fragen für Human Review
- Bitte `assets/kosmetikstudio-muenchen.png` und `assets/haarausfall-stress.png` als lizenzierte lokale Assets bereitstellen, falls die Card-Bilder wie gewünscht umgestellt werden sollen.
- Soll der Google-Bewertung-Artikel später vollständig aus dem WordPress-Export bereinigt werden? Es gibt noch alte WordPress-URLs in Schema-/Asset-/Script-Kontexten, aber keine alten WordPress-`href`-Links mehr.

## Asset- und Lizenzhinweise
- Keine neuen Assets hinzugefügt.
- Keine externen Bilder, Fonts oder Social-Profile ergänzt.
- Fehlende Assets: `assets/kosmetikstudio-muenchen.png`, `assets/haarausfall-stress.png`.

## Lighthouse-Score
- Nicht gemessen. Änderungen betreffen Links, Meta-Tags und kleine Card-Texte; kein Lighthouse-Lauf durchgeführt.
