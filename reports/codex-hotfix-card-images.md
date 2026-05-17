# Goal: Hotfix Card-Bilder — 2026-05-16

## Geänderte Dateien
- `assets/Haarausfall durch Stress.png` → `assets/haarausfall-stress.png`
- `assets/kosmetikstudio-muenchen.png`
- `index.html`
- `blog/index.html`
- `reports/codex-hotfix-card-images.md`

## Untracked Dateien
- `assets/haarausfall-stress.png`
- `assets/kosmetikstudio-muenchen.png`
- `reports/codex-hotfix-card-images.md`
- `reports/codex-goal-asset-check-card-images.md` war bereits vor diesem Run untracked.
- `reports/codex-hotfix-links-images.md` war bereits vor diesem Run untracked.
- `reports/codex-link-audit.md` war bereits vor diesem Run untracked.

## Was wurde geändert
- Die beiden Bilddateien wurden auf URL-sichere Namen umbenannt.
- In `index.html` wurde die Kosmetikstudio-München-Card mit `assets/kosmetikstudio-muenchen.png` ergänzt.
- In `index.html` wurde die Haarausfall-Card auf `/assets/haarausfall-stress.png` umgestellt.
- In `blog/index.html` wurde die vorhandene Haarausfall-Card auf `/assets/haarausfall-stress.png` umgestellt.

## Was wurde bewusst nicht geändert
- In `blog/index.html` wurde keine Medical-Beauty-Card ergänzt, weil dort keine solche Card vorhanden ist und keine neue Referenz/Blog-Card erfunden werden soll.
- Keine Commits, Pushes oder Deployments.

## Offene Fragen für Human Review
- Soll `blog/index.html` eine zusätzliche Medical-Beauty-Card erhalten? Dafür bräuchte es ein konkretes Ziel und freigegebenen Inhalt.

## Asset- und Lizenzhinweise
- Verwendet wurden lokal vorhandene Assets aus dem Repo.
- Keine externen Bilder, Fonts oder Stockfotos eingebunden.

## Lighthouse-Score
- Nicht gemessen. Es wurden nur lokale Bildpfade und Dateinamen geändert.
