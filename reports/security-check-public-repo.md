# Security-Check vor Public-Repo-Release

**Repo:** maxcontentseo
**Datum:** 2026-05-15
**Scope:** Alle 92 git-tracked Files (`git ls-files`)
**Auditor:** Claude Code (Opus 4.7)

## TL;DR

| Risikostufe | Anzahl Findings | Aktion |
|---|---|---|
| KRITISCH | 2 | Vor Public-Release fixen |
| MITTEL | 3 | Bewusste Entscheidung nötig |
| NIEDRIG | 3 | Optionale Cosmetics |

**Kein echter API-Key, Token, Passwort, IBAN, BIC oder Steuer-ID in tracked Files gefunden.** Alle Auth-Werte sind `REPLACE_ME_*`-Placeholder. Die kritischen Punkte sind: fehlende Root-`.gitignore` und exponierte Google-Sheet-ID.

---

## KRITISCH

### K-1. Keine Root-`.gitignore` → kein automatischer Secret-Schutz

| | |
|---|---|
| Datei | `.gitignore` (Root) |
| Status | **FEHLT** |
| Inhalt | — |
| Konsequenz | Eine versehentlich ins Root abgelegte `.env`, `credentials.json`, `*.key`, `cache/` würde sofort committet werden. Nur `outreach-cli/.gitignore` schützt das Sub-Modul. |

**Fix vor Public-Release (Pflicht):**

```gitignore
# .gitignore (Root)
.env
*.env.local
credentials/
*credentials*.json
*.pem
*.p12
*.pfx
*.key
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
.mypy_cache/
node_modules/
.DS_Store
Thumbs.db
nul
.claude/settings.local.json
.claude/scheduled_tasks.lock
WDRed*.lnk

# Audit-Outputs mit Drittfirma-PII (siehe M-2)
reports/audit-*.md
reports/audit-*.pdf
reports/outreach-*.txt
audit-queue.md
```

### K-2. Google-Sheet-ID exposed (3 Files)

| Datei | Zeile | Inhalt |
|---|---|---|
| `PROJECT_BRIEF.md` | 20 | `Sheet: <redacted-sheet-id>` (Datei jetzt gitignored, siehe security-fix.md) |
| `outreach-cli/.env.example` | 6 | `SHEET_ID=<redacted-sheet-id>` (jetzt `REPLACE_ME_WITH_SHEET_ID`) |
| `outreach-cli/REVIEW.md` | 110 | gleiche ID dokumentiert (jetzt redacted) |

**Risiko-Bewertung:** Eine Sheet-ID alleine gibt **keinen Zugriff** ohne Service-Account-JSON. **Aber:** sie ist eine eindeutige Kennung der Produktions-Lead-Datenbank, mit der ein Angreifer gezielt Phishing/Brute-Force-Versuche gegen den Service-Account starten kann. Im Public-Repo verengt das die Attack-Surface unnötig.

**Fix:**
- In `.env.example` Zeile 6: `SHEET_ID=YOUR_GOOGLE_SHEET_ID_HERE`
- In `PROJECT_BRIEF.md` Zeile 20: entweder ganze Datei aus Public-Repo entfernen (enthält auch Hot-Leads + Pricing + Adresse, siehe M-1, M-3) oder Sheet-ID redacten.
- In `outreach-cli/REVIEW.md`: gleiche ID redacten.

---

## MITTEL

### M-1. `PROJECT_BRIEF.md` enthält operatives Live-Wissen

| Datei | Zeile | Inhalt | Warum problematisch |
|---|---|---|---|
| `PROJECT_BRIEF.md` | 5 | `Inhaber: Georg Stopfer, georg@maxcontentseo.de` | (= Impressum, OK) |
| `PROJECT_BRIEF.md` | 6 | `Adresse: An den Höfen 1a, 04626 Schmölln` | Privat-/Business-Adresse — im Impressum auf maxcontentseo.de zwar öffentlich (dort "04626 Drogen"), aber im Repo keine Notwendigkeit |
| `PROJECT_BRIEF.md` | 11 | Konkretes Pricing-Modell | Geschäftsstrategie — kein Sicherheitsproblem, aber wettbewerbsrelevant |
| `PROJECT_BRIEF.md` | 35–37 | Versende-Datum & Follow-up-Datum pro Batch | Operative Live-Daten |
| `PROJECT_BRIEF.md` | 40–41 | `Hot Leads: Vitaminbude/Robin … Beauty Club/Mustafa` | **Drittfirma-Klarnamen** mit Verkaufsstatus |
| `PROJECT_BRIEF.md` | 44 | Gesperrte Leads mit Personennamen | DSGVO-relevant |
| `PROJECT_BRIEF.md` | 48 | `Formspree ID: mqenpryl` | Public-Form-ID, OK (im HTML ohnehin sichtbar) |

**Empfehlung:** `PROJECT_BRIEF.md` **vor Public-Release komplett aus dem Repo nehmen** (gitignore + `git rm --cached PROJECT_BRIEF.md`) oder eine sanitisierte Version ohne Hot-Leads, Pricing und Adresse erstellen.

### M-2. Drittfirma-Daten in `reports/audit-*.md` und `audit-queue.md`

| Datei | Zeile | Inhalt | Risiko |
|---|---|---|---|
| `reports/audit-dermacosmetic-wiesbaden-de-20260513.md` | 82 | Adresse + Mobil-Telefon + Email einer Drittfirma (Quelle Impressum) — konkrete Werte hier redacted | Konzentrierte Datensammlung über Drittfirma erleichtert Spam/Stalking. Datei jetzt gitignored. |
| `audit-queue.md` | 14–35 | 21 Domain-Namen + Operativ-Status + Notes wie "catch-all-Adresse", "NB SKIP — invalid", Personen-Adressen (info@kosmetik-institut-dr-wenzel.de + Anmerkung "Dr. Karen Wenzel") | Verkaufsfunnel-Snapshot mit Lead-Bewertungen — **DSGVO-relevant**, weil hier Status-Annotationen über benannte Drittpersonen geführt werden |
| `audit-queue.md` | 70 | `office@kosmetik-institut-dr-wenzel.de` + Klarname "Dr. Karen Wenzel" | Identifizierbare Drittperson + Kontaktdaten + interne Klassifikation |
| `audit-queue.md` | 75–80 | 24 Lead-Emails (`info@bb-beautybox.de` etc.) mit Versende-Datum | Lead-DB-Snapshot |
| `reports/outreach-*.txt` (3 Files) | — | Drittfirma-Email-Inhalte + interne Hook-Strategie | Verrät Sales-Methodik gegen named Firmen |

**Empfehlung:**
- `reports/audit-*.md`, `reports/audit-*.pdf`, `reports/outreach-*.txt` und `audit-queue.md` via `.gitignore` aus dem Public-Repo halten.
- Für Public-Release einen sanitisierten **Beispiel-Audit** mit dummy-Domain `example-studio.de` als Showcase einchecken (nicht die Echt-Audits).

### M-3. Privatanschrift Inhaber in Email-Templates + index.html

| Datei | Zeile | Inhalt |
|---|---|---|
| `index.html` | 1228, 1231, 1241 | `Georg Stopfer, An den Höfen 1a, 04626 Drogen, Deutschland` (Impressum-Pflicht) |
| `PROJECT_BRIEF.md` | 6 | `Adresse: An den Höfen 1a, 04626 Schmölln` |
| `outreach-cli/outreach_cli/templates/variante_audit.txt` | 23 | `An den Höfen 1a, 04626 Schmölln` |
| `outreach-cli/outreach_cli/templates/variante_c.txt` | 26 | `An den Höfen 1a, 04626 Schmölln` |

**Risiko-Bewertung:**
- `index.html` Impressum → **gewollt öffentlich** (Pflicht nach § 5 TMG / § 18 MStV).
- Email-Templates → die Adresse landet in jeder versendeten Mail, ist also bei den Empfängern. Im Public-Repo ist sie aber dauerhaft indexierbar (Github-Suche, Archive.org).
- **Hinweis Adress-Diskrepanz:** Impressum sagt "04626 Drogen", interne Dateien sagen "04626 Schmölln". Vermutlich Ortsteil-Schreibweise — vor Public-Release vereinheitlichen.

**Empfehlung:** Templates bleiben drin (Adresse ist eh in jeder Mail), aber `PROJECT_BRIEF.md` siehe M-1.

---

## NIEDRIG

### N-1. Lokale Windows-Pfade in 10 Files

| Datei | Charakter |
|---|---|
| `AGENTS.md` | `D:\000 SEO Business\…` als Working-Dir-Referenz |
| `CHANGELOG.md` | `D:\000 SEO Business\…` |
| `PROJECT_BRIEF.md` Zeile 14 | `outreach-cli: D:\000 SEO Business\maxcontentseo\outreach-cli\` |
| `docs/firecrawl-cli-usage.md` | `C:\Users\myste\…` |
| `docs/verify-pipeline-setup.md` | `D:\000 SEO Business\…` |
| `outreach-cli/.env.example` Zeile 10 | `GOOGLE_CREDENTIALS_PATH=D:\000 SEO Business\Tools\GoogleAutomationfür…\google-service-account.json` |
| `outreach-cli/README.md` | mehrere |
| `outreach-cli/docs/email-verification.md` | mehrere |
| `outreach-cli/v2_nachzieh.py` Zeile 52 | hardcoded Pfad |
| `outreach-cli/v3_restore_dirty_kont.py` Zeile 38–39 | hardcoded Pfad |

**Risiko:** Sehr niedrig. Verrät nur lokale Filesystem-Struktur und Windows-Username (`myste`). Keine Auth-Wege, kein Zugriff. Aber unprofessionell für ein Public-Repo.

**Empfehlung:**
- `.env.example` Zeile 10: durch `GOOGLE_CREDENTIALS_PATH=path/to/google-service-account.json` ersetzen.
- `v2_nachzieh.py` + `v3_restore_dirty_kont.py`: Pfade via `os.environ` oder CLI-Arg parametrisieren ODER beide Files aus dem Public-Repo entfernen (sind Ad-hoc-Migration-Scripts).
- Docs / READMEs: optional generische `./outreach-cli/` Schreibweise.

### N-2. Geschäfts-Email in 14 Files (33 Vorkommen)

`georg@maxcontentseo.de` taucht in AGENTS.md, PROJECT_BRIEF.md, .env.example, Code-Kommentaren, Test-Files und Templates auf.

**Risiko:** Minimal. Adresse ist via Impressum öffentlich. Im Public-Repo bedeutet das aber mehr Crawler-Hits → mehr Spam.

**Empfehlung:** Akzeptieren. Adresse ist sowieso scraped vom Impressum.

### N-3. Hardcoded Test-Fixtures mit Placeholder-Tokens

| Datei | Zeile | Inhalt |
|---|---|---|
| `outreach-cli/tests/test_smtp.py` | 49 | `token="fake-app-password"` |
| `outreach-cli/tests/test_smtp.py` | 87 | `"REPLACE_ME_WITH_PROTON_APP_PASSWORD"` als String-Constant für Negativ-Test |
| `outreach-cli/tests/test_cli_provider_label.py` | 30, 44 | `REPLACE_ME_WITH_KEY`, `YOUR_NB_KEY`, `CHANGE_ME` |
| `outreach-cli/tests/test_neverbounce.py` | 141 | `REPLACE_ME_WITH_NB_KEY` |

**Risiko:** Keins — alles offensichtliche Placeholder. Nur erwähnt, damit Linter/Automated-Secret-Scanner nicht false-positive triggern.

---

## Per-File-Befund

### KEINE sensiblen Daten gefunden

- `.claude/commands/audit.md`
- `.claude/commands/autorun.md`
- `.claude/prompts/codex-verify.md`
- `.claude/skills/audit.md`
- `CHANGELOG.md` *(nur lokaler Pfad, siehe N-1)*
- `CNAME`
- `README.md`
- `bin/firecrawl-pp-cli.exe` *(Binary, manuell nicht-prüfbar — Build-Artefakt aus `printing-press` Pipeline, sollte reproducible sein; Empfehlung: aus Repo entfernen und über Release-Tags bereitstellen)*
- `branchen/kosmetikstudios.html`
- `docs/pipeline-v2.md`
- `docs/sistrix-integration-eval.md`
- `docs/superpowers/specs/2026-05-12-audit-skill-design.md`
- `docs/superpowers/specs/2026-05-12-firecrawl-cli-design.md`
- `outreach-cli/.gitignore`
- `outreach-cli/REVIEW-BACKLOG.md`
- `outreach-cli/REVIEW-send.md`
- `outreach-cli/docs/bounce-check.md` *(nur Variable-Name PROTONMAIL_BRIDGE_PASSWORD, kein Wert)*
- `outreach-cli/outreach_cli/__init__.py`
- `outreach-cli/outreach_cli/__main__.py`
- `outreach-cli/outreach_cli/audit_hook.py`
- `outreach-cli/outreach_cli/cli.py`
- `outreach-cli/outreach_cli/commands/*` (alle 5 Files)
- `outreach-cli/outreach_cli/config.py`
- `outreach-cli/outreach_cli/email/*` (alle 4 Files)
- `outreach-cli/outreach_cli/imap/client.py` *(nur ENV-Variable-Doku, kein Wert)*
- `outreach-cli/outreach_cli/imap/parser.py`
- `outreach-cli/outreach_cli/leads/*`
- `outreach-cli/outreach_cli/sheets.py`
- `outreach-cli/outreach_cli/templates/engine.py`
- `outreach-cli/outreach_cli/verifier/*` (alle 5 Files)
- `outreach-cli/pyproject.toml`
- `outreach-cli/tests/*` *(Placeholder-Tokens, siehe N-3)*
- `reports/codex-goal-01-lingqi-case.md` bis `…-05-rechner.md` *(Strategie-Dokumente ohne PII)*
- `scripts/verify-pipeline.ps1`
- `tools/seo-check.*`

### Findings vorhanden (siehe oben)

- `.gitignore` (FEHLT, K-1)
- `AGENTS.md` (N-1)
- `CONTEXT.md` *(operative Live-Daten ähnlich PROJECT_BRIEF — bei Public-Release prüfen ob Vitaminbude/LingQi-Details ins Public sollen; siehe M-1-Analoge)*
- `PROJECT_BRIEF.md` (K-2, M-1, M-3, N-1)
- `audit-queue.md` (M-2)
- `docs/firecrawl-cli-usage.md` (N-1)
- `docs/verify-pipeline-setup.md` (N-1)
- `index.html` (M-3 — gewollt, Impressum)
- `outreach-cli/.env.example` (K-2, M-3-indirekt, N-1)
- `outreach-cli/README.md` (N-1)
- `outreach-cli/REVIEW.md` (K-2)
- `outreach-cli/docs/email-verification.md` (N-1)
- `outreach-cli/outreach_cli/templates/variante_audit.txt` (M-3)
- `outreach-cli/outreach_cli/templates/variante_c.txt` (M-3)
- `outreach-cli/v2_nachzieh.py` (N-1)
- `outreach-cli/v3_restore_dirty_kont.py` (N-1)
- `reports/audit-dermacosmetic-wiesbaden-de-20260513.md` (M-2)
- `reports/audit-vitaminbude-de-20260512-v2.md` und `-v3.md` (M-2)
- `reports/outreach-*.txt` (3 Files, M-2, M-3)

---

## Negativ-Befunde (gut!)

Folgende Patterns wurden gesucht und **nicht gefunden**:

- Keine echten OpenAI/Anthropic/Google API-Keys (`sk-…`, `AIza…`, `ghp_…`, `xoxb-…`)
- Keine Firecrawl-API-Keys (`fc-…`)
- Keine echten NeverBounce-/ZeroBounce-Keys
- Keine IBAN/BIC/Steuer-IDs (Pattern `[A-Z]{2}\d{2}…`)
- Keine `.pem`, `.p12`, `.pfx`, `.key`, `credentials.json` tracked
- Keine `.env`-Files tracked (nur `.env.example`)
- Keine Klartext-Passwörter in Code (alle `password=`-Vorkommen sind Variablen-Namen oder Doku)
- Kein Windows-User-Pfad mit `C:\Users\myste\` außer einem Doku-Beispiel in `docs/firecrawl-cli-usage.md`

---

## Action-Items vor Public-Release (priorisiert)

### Pflicht

1. **Root-`.gitignore` anlegen** (Snippet siehe K-1)
2. **`PROJECT_BRIEF.md` entscheiden:** entweder `git rm --cached PROJECT_BRIEF.md` + gitignore, oder sanitisieren (Adresse, Hot-Leads, Pricing entfernen) (K-2, M-1)
3. **Sheet-ID redacten** in `.env.example:6` und `outreach-cli/REVIEW.md` (K-2)
4. **`reports/audit-*`, `reports/outreach-*`, `audit-queue.md`** aus Public-Repo entfernen (`git rm --cached` + gitignore) (M-2)
5. **`.env.example:10`** Pfad-Beispiel entwindowsifizieren (N-1)

### Empfohlen

6. Adress-Diskrepanz Drogen/Schmölln vereinheitlichen
7. `outreach-cli/v2_nachzieh.py` + `v3_restore_dirty_kont.py` aus Public-Repo entfernen (interne Migration-Scripts)
8. `bin/firecrawl-pp-cli.exe` aus Repo entfernen, via Release-Tags bereitstellen
9. `CONTEXT.md` auf operative Live-Daten prüfen (analog M-1)
10. README mit Hinweis: "Lead-Daten, Audit-Reports und PROJECT_BRIEF sind nicht öffentlich — dieses Repo enthält nur Code + öffentliche Dokumentation."

### Optional / Cosmetic

11. Lokale Windows-Pfade in Doku durch generische Pfade ersetzen
12. Pre-Commit-Hook für Secret-Scanning einbauen (z.B. `gitleaks` oder `detect-secrets`)

---

## Methodik

Geprüft mit:
- `git ls-files` für tracked-File-Liste (92 Files)
- Grep-Patterns für API-Key-Formate: `sk-[a-zA-Z0-9]{20,}`, `AIza[…]`, `ghp_[…]`, `xoxb-[…]`, `fc-[…]`
- Grep-Pattern für Auth-Strings: `(password|api[_-]?key|token|secret)\s*[:=]\s*["']?[A-Za-z0-9_\-\.]{16,}` (case-insensitive)
- Grep-Pattern für IBAN/BIC: `[A-Z]{2}[0-9]{2}[A-Z0-9]{15,30}`
- Grep für Sheet-ID-Konstante
- Grep für Telefon-/Adress-/Privatnamen-Patterns
- Grep für Windows-Pfade `D:\\000 SEO Business\\` und `C:\\Users\\myste`
- `git check-ignore` zur Verifikation dass `.env`-Files ignoriert werden
- Read der `.env.example` zur Verifikation aller Placeholder

Nicht geprüft (Empfehlung Folge-Schritt): `git log -p` auf historische Commits — wenn jemals echte Secrets committet und später entfernt wurden, sind sie in History noch erreichbar. Vor Public-Release ggf. `git filter-repo` oder Repo neu initialisieren.
