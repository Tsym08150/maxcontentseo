# Audit-Verify-Pipeline — Setup

Zwei-Maschinen-Architektur für unabhängige Audit-Verifikation:

```
┌─────────────────┐         GitHub          ┌──────────────────┐
│ Haupt-PC        │   ←→    /OneDrive  ←→   │ Laptop           │
│ (Claude Code)   │                          │ (Codex / 2. AI)  │
│                 │                          │                  │
│ 1. /audit       │   audit-*.md             │ 4. codex run     │
│    erzeugt      │  ──────────────────→     │    --prompt      │
│    Report+Mail  │   outreach-*.txt         │    codex-verify  │
│                 │   codex-verify.md        │                  │
│ 2. verify-      │                          │ 5. erzeugt       │
│    pipeline.ps1 │   verify-*.md            │    verify-*.md   │
│    pollt        │  ←─────────────────      │    + git push    │
│                 │                          │                  │
│ 3. liest        │                          │                  │
│    Verdict      │                          │                  │
└─────────────────┘                          └──────────────────┘
```

## Channels (Sync zwischen den Maschinen)

| Channel | Vorteile | Nachteile | Setup-Aufwand |
|---|---|---|---|
| **Git** (Default) | Audit-Trail, Versionierung, asynchron | 1-2 s Push-Push-Lag, Branch-Konflikte möglich | 0 (existiert) |
| **OneDrive** | Instant-Sync, kein Commit | Kein Audit-Trail, Sync kann hängen | 0 (existiert) |
| SSH | Synchron, direkter Call | Kein SSH-Server konfiguriert | ⚠️ nicht vorhanden |
| RDP-Automation | Wie ein Mensch klicken | Sehr fragil (GUI-Drift) | nicht empfohlen |

**Aktive Auswahl:** `scripts/verify-pipeline.ps1 -Channel auto` wählt Git, fällt auf OneDrive zurück.

## Setup Haupt-PC (einmalig)

Skript ist bereits in Place:
- `scripts/verify-pipeline.ps1`
- `.claude/prompts/codex-verify.md`

Aufruf:
```powershell
cd "D:\000 SEO Business\maxcontentseo"
.\scripts\verify-pipeline.ps1                    # neuester Audit
.\scripts\verify-pipeline.ps1 -Domain vitaminbude-de
.\scripts\verify-pipeline.ps1 -Channel onedrive -TimeoutMinutes 30
```

## Setup Laptop (einmalig)

### Variante A — Git-Channel (empfohlen)

```powershell
# Repo klonen
git clone https://github.com/Tsym08150/maxcontentseo.git
cd maxcontentseo

# Codex (oder beliebige zweite AI-CLI) installieren — siehe deren Doku
# Falls Codex MCP-fähig ist: Ubersuggest MCP konfigurieren (eigener OAuth-Flow)
# Falls nicht: HTTP-API-Calls (Ubersuggest, Firecrawl) direkt mit env-Keys

# .env oder credentials für Firecrawl
$env:FIRECRAWL_API_KEY = "fc-..."
```

**Workflow nach Audit-Trigger:**
```powershell
cd maxcontentseo
git pull origin main

# Codex (oder Alternative) mit dem Prompt aufrufen.
# Exemplarisch (passe an deine CLI an):
codex run `
  --prompt .claude/prompts/codex-verify.md `
  --input reports/audit-vitaminbude-de-20260512-v3.md `
  --input reports/outreach-vitaminbude-de-20260512-v3.txt `
  --output reports/verify-vitaminbude-de-20260512-v3.md

git add reports/verify-vitaminbude-de-20260512-v3.md
git commit -m "verify: vitaminbude.de — <Verdict>"
git push origin main
```

### Variante B — OneDrive-Channel

```powershell
# Pfad öffnen (synct automatisch vom Haupt-PC)
explorer "$env:USERPROFILE\OneDrive\audit-verify-bridge"

# Codex manuell mit den Dateien füttern
# Verify-Report mit gleichem Filename in OneDrive ablegen
# Sync zurück passiert automatisch
```

## Automation des Laptop-Triggers (optional)

Damit der Laptop nicht manuell angetippt werden muss, gibt es drei Auto-Trigger-Optionen:

### Option 1 — Git-Polling-Daemon auf Laptop

`scripts/laptop-watcher.ps1` (TBD — noch nicht implementiert):
- Pollt alle 30 s `git fetch && git status`
- Bei neuer audit-*.md im Remote → automatisch Codex-Run
- Push der verify-*.md sobald fertig

### Option 2 — GitHub Action

`.github/workflows/verify.yml` (TBD — noch nicht implementiert):
- Trigger: Push einer Datei nach `reports/audit-*.md`
- Job läuft auf einem self-hosted Runner auf dem Laptop
- Codex wird im Runner ausgeführt

### Option 3 — Manueller Anstoß (aktuelle Default-Form)

Skript zeigt eine klare Anleitung — der Laptop-User triggert Codex selbst.

## Verdict-Codes (Exit-Status der Pipeline)

| Exit-Code | Bedeutung |
|---|---|
| 0 | ✅ FREIGEGEBEN — Mail kann versendet werden |
| 10 | ⚠️ KORREKTUREN NÖTIG — Diff-Liste im verify-*.md |
| 20 | ❌ ABGELEHNT — kein Lead / Audit falsch |
| 1 | Audit-Datei nicht gefunden |
| 2 | Kein Channel verfügbar |
| 3 | Timeout |

## Bekannte Limitierungen

1. **Codex-Remote-Start nicht implementiert.** Aktuell muss der Laptop-User Codex manuell starten. SSH/RDP würde das ändern, ist aber nicht configured.
2. **Beide Maschinen nutzen die gleichen APIs (Ubersuggest, Firecrawl).** Die Verifikation ist also nicht "unabhängige Datenquelle", sondern "unabhängiges Modell mit denselben Daten". Das fängt vor allem AI-Halluzinationen + Tool-Fehlbedienungen ab.
3. **Codex auf dem Laptop muss MCP- oder API-zugang haben.** Ohne Ubersuggest-Auth kann er nur die HTTP-Verifikation machen (Trailing-Slash, Meta-Tags), nicht die Ubersuggest-Werte gegenprüfen.
4. **Polling kostet Strom + GitHub-API-Calls.** Default 15 Min Timeout / 20 s Intervall → max. 45 git-fetches pro Run.
