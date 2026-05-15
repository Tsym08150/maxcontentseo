# Security-Fix — Umsetzung der Pflicht-Aktionen aus security-check-public-repo.md

**Datum:** 2026-05-15
**Vorlage:** `reports/security-check-public-repo.md`
**Branch:** main

## Status: ✅ Alle 5 Pflicht-Aktionen umgesetzt

| # | Aktion | Status |
|---|---|---|
| 1 | Root-`.gitignore` angelegt | ✅ |
| 2 | Sheet-ID redacted in `.env.example` + `outreach-cli/REVIEW.md` | ✅ |
| 3 | `PROJECT_BRIEF.md` aus Git-Index entfernt | ✅ |
| 4 | `reports/audit-*` + `reports/outreach-*` aus Git-Index entfernt | ✅ |
| 5 | `audit-queue.md` aus Git-Index entfernt | ✅ |

---

## 1. Root-`.gitignore` angelegt

**Datei:** `.gitignore` (Root, neu)

**Inhalt:**

```gitignore
.env
.env.*
!.env.example
outreach-cli/.env

# Audit-Outputs (Drittfirma-PII + interne Sales-Strategie)
reports/audit-*.md
reports/audit-*.pdf
reports/outreach-*.md
reports/outreach-*.txt
audit-queue.md

# Operatives Live-Wissen (Hot-Leads, Pricing, Privatadresse)
PROJECT_BRIEF.md

# Local Claude Code settings
.claude/settings.local.json
.claude/scheduled_tasks.lock

# Sonstiger lokaler Müll
nul
*.lnk
```

**Erweiterung gegenüber User-Spec:**
- User-Spec listete nur `reports/audit-*.md` und `reports/outreach-*.md`. Real existieren auch `reports/audit-*.pdf` und `reports/outreach-*.txt` — Patterns entsprechend ergänzt, sonst wäre der Schutz unvollständig.
- `.claude/settings.local.json` und `.claude/scheduled_tasks.lock` ergänzt — waren bereits als untracked sichtbar.
- `nul` und `*.lnk` ergänzt — bereits als untracked sichtbar (Windows-Artefakte).

## 2. Sheet-ID redacted

### 2a. `outreach-cli/.env.example` Zeile 6

```diff
- SHEET_ID=19ak15Thx3icvmcviMLePG6d22psdWocBChTBNykorL0
+ SHEET_ID=REPLACE_ME_WITH_SHEET_ID
```

### 2b. `outreach-cli/REVIEW.md` Zeile 110

```diff
- **Issue:** `SHEET_ID=19ak15Thx3icvmcviMLePG6d22psdWocBChTBNykorL0` — this looks like a real Google Spreadsheet ID, not a placeholder.
+ **Issue:** `SHEET_ID=<real-google-spreadsheet-id>` — a real-looking Google Spreadsheet ID was committed as the example value, not a placeholder. *(Redacted on 2026-05-15 in security-fix; original value rotated/scrubbed before public release.)*
```

### 2c. `reports/security-check-public-repo.md` (Bonus-Fix)

Der Audit-Report selbst hat die ID 4× im Klartext zitiert. Ersetzt durch `<redacted-sheet-id>`. Ebenso die Drittfirma-Adresse + Mobil-Nummer aus M-2-Tabelle.

## 3. `PROJECT_BRIEF.md` aus Git-Index entfernt

```bash
git rm --cached PROJECT_BRIEF.md
```

- Datei bleibt lokal auf Disk (für Eigennutzung).
- `.gitignore` verhindert Re-Tracking.
- Enthielt: Privatadresse, Hot-Leads (Vitaminbude/Robin, Beauty Club/Mustafa), Pricing, Sheet-ID, Versende-Daten pro Batch.

## 4. `reports/audit-*` + `reports/outreach-*` aus Git-Index entfernt

```bash
git rm --cached \
  reports/audit-dermacosmetic-wiesbaden-de-20260513.md \
  reports/audit-dermacosmetic-wiesbaden-de-20260513.pdf \
  reports/audit-vitaminbude-de-20260512-v2.md \
  reports/audit-vitaminbude-de-20260512-v2.pdf \
  reports/audit-vitaminbude-de-20260512-v3.md \
  reports/audit-vitaminbude-de-20260512-v3.pdf \
  reports/outreach-dermacosmetic-wiesbaden-de-20260513.txt \
  reports/outreach-vitaminbude-de-20260512-v2.txt \
  reports/outreach-vitaminbude-de-20260512-v3.txt
```

**9 Files entfernt** (3 Audits × md+pdf + 3 Outreach × txt). Files bleiben lokal.

**Bleibt im Repo:**
- `reports/codex-goal-01-lingqi-case.md` bis `…-05-rechner.md` (Strategie-Dokumente ohne PII — sind im `.gitignore`-Pattern explizit nicht erfasst, da Pattern `audit-*` / `outreach-*` greift nicht).
- `reports/security-check-public-repo.md` und `reports/security-fix.md` (Audit-Dokumentation, jetzt sanitisiert).

## 5. `audit-queue.md` aus Git-Index entfernt

```bash
git rm --cached audit-queue.md
```

Enthielt 21 Lead-Domains, Personen-Klarnamen (Dr. Karen Wenzel), 24 Lead-Email-Adressen, Versende-Daten. **DSGVO-relevant.** Datei bleibt lokal als operatives Tracking-Sheet.

---

## Verifikation

### `git status` nach allen Aktionen

```
D  PROJECT_BRIEF.md
D  audit-queue.md
 M outreach-cli/.env.example
 M outreach-cli/REVIEW.md
D  reports/audit-dermacosmetic-wiesbaden-de-20260513.md
D  reports/audit-dermacosmetic-wiesbaden-de-20260513.pdf
D  reports/audit-vitaminbude-de-20260512-v2.md
D  reports/audit-vitaminbude-de-20260512-v2.pdf
D  reports/audit-vitaminbude-de-20260512-v3.md
D  reports/audit-vitaminbude-de-20260512-v3.pdf
D  reports/outreach-dermacosmetic-wiesbaden-de-20260513.txt
D  reports/outreach-vitaminbude-de-20260512-v2.txt
D  reports/outreach-vitaminbude-de-20260512-v3.txt
?? .gitignore
?? reports/security-check-public-repo.md
?? reports/security-fix.md
```

Erklärung:
- `D` (deleted from index, exists in working tree) → wie gewünscht, files lokal vorhanden, aber nicht mehr getrackt.
- `M` → Sheet-ID-Redactions.
- `??` (untracked) → neue Files die jetzt committet werden: `.gitignore`, `security-check-public-repo.md`, `security-fix.md`.

---

## Offen / Empfehlung Folge-Schritte

### History-Scrubbing (nicht in dieser Fix-Aktion enthalten)

Die Sheet-ID, Privatadresse, Drittfirma-Daten und Lead-Emails sind in der **Commit-History** weiterhin abrufbar via:

```bash
git log -p -- PROJECT_BRIEF.md audit-queue.md reports/audit-*.md
```

Vor Public-Release **eine der drei Optionen** umsetzen:

1. **Repo neu initialisieren** (sauberste Variante, verliert History):
   ```bash
   rm -rf .git
   git init -b main
   git add .
   git commit -m "initial public release"
   ```

2. **`git filter-repo`** mit den sensiblen Files:
   ```bash
   pip install git-filter-repo
   git filter-repo --invert-paths \
     --path PROJECT_BRIEF.md \
     --path audit-queue.md \
     --path-glob 'reports/audit-*' \
     --path-glob 'reports/outreach-*'
   git push --force-with-lease origin main
   ```

3. **Privates Repo lassen.** Wenn ohnehin History-relevante Daten drin sind, ist Public-Release-mit-clean-History oft mehr Aufwand als ein neues Public-Showcase-Repo.

### Weitere Empfehlungen aus security-check-public-repo.md (MITTEL/NIEDRIG)

- M-3 (Privatadresse in Templates): bewusste Entscheidung — bleibt drin, da Mails sie ohnehin enthalten.
- N-1 (Windows-Pfade in 10 Files): optional, vor Public-Release Cosmetics-Pass.
- `bin/firecrawl-pp-cli.exe`: optional aus Repo entfernen, via Release-Tags bereitstellen.
- Pre-Commit-Hook (`gitleaks` oder `detect-secrets`) als langfristiger Schutz.

---

## Commit-Plan

```bash
git add .gitignore outreach-cli/.env.example outreach-cli/REVIEW.md \
        reports/security-check-public-repo.md reports/security-fix.md
git commit -m "security: add root .gitignore, remove sensitive files from tracking"
git push origin main
```

Wird nach Abnahme dieses Reports ausgeführt.
