# Audit-Queue — Pipeline v2 Status-Tracking

**Workflow:** Codex (Laptop) → Claude Code (Haupt-PC) → Claude.ai (Browser) → Send via `outreach-cli`.
Spec: [docs/pipeline-v2.md](docs/pipeline-v2.md).

**Status-Werte:**
- `DONE` — Stufe komplett
- `PENDING` — noch zu erledigen
- `BLOCKED` — Eskalation nötig (siehe Notes)
- `SKIP` — manuell ausgeschlossen (z.B. HWG-Quarantäne)
- `—` — Stufe noch nicht erreicht (Vorgänger-Stufe nicht DONE)

| # | Domain | Codex | Claude Code | Claude.ai | Send | Notes |
|---|---|---|---|---|---|---|
| 1 | dermacosmetic-wiesbaden.de | DONE | DONE | DONE | PENDING | Hybrid-Hook fertig, NB-Verify offen |
| 2 | beautytime-rena.de | PENDING | — | — | — | Neu-Isenburg, variant-c heute morgen versandt |
| 3 | kosmetikstudio-mj.de | PENDING | — | — | — | Offenbach |
| 4 | kosmetik-fusspflege-behr.de | PENDING | — | — | — | Offenbach |
| 5 | emiliakosmetik.de | PENDING | — | — | — | Offenbach |
| 6 | anna-leinweber.de | PENDING | — | — | — | Offenbach (NB SKIP — Email-Ungültig) |
| 7 | vivanesse.de | PENDING | — | — | — | Offenbach, catch-all-Adresse |
| 8 | cosmos-kosmetikstudio.de | PENDING | — | — | — | Raunheim (NB SKIP — invalid) |
| 9 | kosmetik-rosbach.de | PENDING | — | — | — | Rosbach (NB SKIP — unknown) |
| 10 | the-art-of-beauty-rosbach.de | PENDING | — | — | — | Rosbach |
| 11 | salmana-medical-beauty.de | PENDING | — | — | — | Rüsselsheim, catch-all |
| 12 | marabeaute.com | PENDING | — | — | — | Rüsselsheim |
| 13 | beauty-my.de | PENDING | — | — | — | Steinbach, catch-all |
| 14 | schoengeister.com | PENDING | — | — | — | Wiesbaden |
| 15 | sandrafaeth.de | PENDING | — | — | — | Wiesbaden, Permanent Make-up |
| 16 | claudia-schwensky.de | PENDING | — | — | — | Wiesbaden, Medical Beauty |
| 17 | kosmetikstudio-wiesbaden-burg.de | PENDING | — | — | — | Wiesbaden |
| 18 | kosmetik-van-wyngaarden.de | PENDING | — | — | — | Wiesbaden |
| 19 | fine-line-wiesbaden.de | PENDING | — | — | — | Wiesbaden, Permanent Make-up |
| 20 | yourskinaesthetic.de | PENDING | — | — | — | Wiesbaden, HydraFacial |
| 21 | soulistas.de | **BLOCKED** | — | — | — | **Codex Re-Run Pflicht** — Service-Halluzinationen (siehe Blocker-Sektion) |

## Status-Snapshot

- **Total:** 21 Domains
- **Codex DONE:** 1
- **Claude Code DONE:** 1
- **Claude.ai DONE:** 1
- **Send DONE:** 0
- **Send PENDING:** 1
- **BLOCKED:** 1 (Soulistas — Codex Re-Run Pflicht)
- **Pipeline noch nicht gestartet:** 19

## 🚨 Aktive Blocker

### soulistas.de — Stufe 3 fand 3 Service-Halluzinationen im Codex-Audit

Branch `audit/soulistas-de-20260513` (Commits `54dc6b3` + `48bf8c4`) **wird nicht gemerged**. Codex hat 3 Services im Hook genannt, die nicht der Realität entsprechen:

| Halluziniert (Codex) | Wahrheit (live geprüft auf soulistas.de) | Konsequenz |
|---|---|---|
| "Soul-Time-Massage hat keine eigene URL" | `soulistas.de/massagen/soul-time-de-luxe.html` existiert | Service entfernen oder Behauptung umformulieren |
| "Entspannung de Luxe" | Tatsächlicher Name: **"Soul-Time de Luxe"** | Korrekten Namen einsetzen |
| "Full-Body-Peeling" | Tatsächlicher Name: **"Softpeeling"** / "Softpeeling-Massage" | Korrekten Namen einsetzen |

**Codex muss neu laufen mit Pflicht:**
- Service-Namen DIREKT aus `soulistas.de/angebot.html` ziehen (live-Scrape)
- Jeden Service-Namen einzeln via `site:soulistas.de "<Service-Name>"` verifizieren
- 3 Services nennen die WIRKLICH keine eigene URL haben
- Wenn alle Services eigene URLs haben → Hook-Logik komplett ändern (z.B. Duplicate-Title-Problem → Profil C statt Profil B)

## Quarantäne / Sonderfälle

| Domain | Grund |
|---|---|
| office@kosmetik-institut-dr-wenzel.de | HWG-Manual: "Dr. Karen Wenzel" Studio-Branding — separater Audit nötig, ggf. Premium-Eskalation (Stufe 4) |

## Schon vor Pipeline-v2 versendet (variant-c)

Diese Leads haben bereits eine variant-c-Mail bekommen (12.05./13.05. ohne Audit-Personalisierung) und sind im Sheet auf "Angeschrieben". Wenn keine Antwort kommt: Follow-up via variant-audit gemäss Pipeline-v2.

- info@bb-beautybox.de, kontakt@beautyvit.de, mail@karin-raschka.de, kontakt@die-beautywerkstatt.de, info@beautykey-hanau.de
- info@beauty-diamonds.de, lale-beauty@hotmail.com, info@lar-beauty.de, info@kosmetikstudio-hanau.de, info@medic-puls.de
- info@rose-aesthetic.de, info@kosmetik-studio-petra-domnick.de, info@kosmetikstudio-button.de, info@kosmetikstudio-langen.de, info@jk-beauty.com
- info@beautique-lily.de, Lumi@Lumi-Kosmetik-Mainz.de, kosmetik@hautrein.de, info@bebeauty-mainz.de, Info@schoenheitssalon-mainz.de
- info@kosmetik-zimmermann.de, info@kosmetik-mainz-schroeder.de, sabine@meine-tcm.de, sofia@cosmeticscare.de

Bounce-Check-Task `MaxContentSEO_BounceCheck_20260513_075812` läuft 2026-05-14 07:58 — danach wissen wir welche dieser Adressen real angekommen sind.

## Update-Regel

Nach jeder Stufe (Codex/Claude Code/Claude.ai/Send): Tabelle hier aktualisieren + `git commit`. Codex pullt vor seinem nächsten Audit, weiß damit was schon erledigt ist.