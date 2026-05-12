# outreach-cli: Email-Verifikation (ZeroBounce)

## Use Case

Vor jedem `--confirm-live` Versand wird die Bounce-Quote senkende Vor-Validierung erzwungen. Im letzten Live-Batch hatten wir **12.5% Bounces** (siehe [bounce-check.md](bounce-check.md)) — das schadet Sender-Reputation. ZeroBounce-Verifikation senkt diese Quote, indem ungültige Adressen vor dem Versand aussortiert werden.

## Pipeline

```
outreach send --confirm-live --tab X ...
  ├── Phase A: Leads laden (gleiche Filter wie Send)
  ├── Phase B: Email-Verifikation (NEU)
  │   ├── 1. Cache-Lookup (cache/verified-emails.json, TTL 30 Tage)
  │   ├── 2. Für uncached: ZeroBounce API /v2/validate
  │   ├── 3. Bucketing: valid → SEND, catch-all → SEND+WARN, rest → SKIP
  │   ├── 4. SKIP → Sheet Recherche_Status = "Email-Ungültig"
  │   └── 5. Cache speichern
  ├── Phase C: Ergebnis-Anzeige + EXPLIZITE FREIGABE (typer.confirm)
  └── Phase D: SMTP-Versand nur an SEND + SEND+WARN
```

## Status-Routing

ZeroBounce returnt einen von 7 Status-Werten. Wir mappen sie in 3 Buckets:

| ZeroBounce-Status | Bucket | Aktion |
|---|---|---|
| `valid` | **SEND** | Mail rausgeschickt |
| `catch-all` | **SEND_WITH_WARN** | Mail trotzdem rausgeschickt (catch-all-Domains akzeptieren technisch alles, aber landen oft) — gelbe Warnung im Output |
| `invalid` | **SKIP** | Nicht senden + Sheet auf "Email-Ungültig" |
| `unknown` | **SKIP** | dito |
| `spamtrap` | **SKIP** | dito (gefährlich: kann Sender-Reputation killen) |
| `abuse` | **SKIP** | dito |
| `do_not_mail` | **SKIP** | dito |

## Konfiguration

In `outreach-cli/.env`:

```ini
ZEROBOUNCE_API_KEY=<dein-key>
```

Free-Tier: **100 Verifikationen/Monat** auf https://www.zerobounce.net/. Account erstellen → Dashboard → API → API Key kopieren.

## Cache

**Pfad:** `outreach-cli/cache/verified-emails.json`
**TTL:** 30 Tage
**Format:**
```json
{
  "schema": 1,
  "entries": {
    "info@example.de": {
      "status": "valid",
      "sub_status": "alias_address",
      "verified_at": "2026-05-12T15:30:00+00:00",
      "did_you_mean": "",
      "free_email": false
    }
  }
}
```

Cache ist `.gitignore`d (enthält Status-Daten pro Lead, sollte nicht öffentlich).

**Atomic-Writes:** temp-File + `os.replace` — keine Datenverluste bei Crash.

**Korrupte JSON:** wird beim Read silently ignoriert + beim nächsten Save überschrieben.

## Commands

### Standalone — `verify-emails`

```powershell
# Aus einem Sheet-Tab (gleiche Filter wie send)
py -m outreach_cli verify-emails --tab Frankfurt_Umland --status Neu --limit 20

# Eine einzelne Adresse
py -m outreach_cli verify-emails --email info@example.de

# Aus Datei (eine Email pro Zeile)
py -m outreach_cli verify-emails --emails-from leads.txt

# Dry-Run: nur prüfen, kein Sheet-Update
py -m outreach_cli verify-emails --tab X --dry-run

# JSON für Scripting
py -m outreach_cli verify-emails --tab X --json
```

### Auto-Trigger — `send --confirm-live`

Bei `outreach send --confirm-live --tab X --template Y` läuft die Verifikation **automatisch vor dem SMTP-Versand**. Ablauf:

1. Verifikations-Tabelle wird angezeigt
2. Skip-Adressen werden im Sheet auf "Email-Ungültig" gesetzt
3. Prompt: `Sende JETZT N verifizierte Mails (inkl. M catch-all mit Warnung)? [y/N]`
4. Bei Y: Versand mit der gefilterten Liste
5. Bei N: Abbruch (Sheet-Updates bleiben aber bestehen!)

`--dry-run` und `--test-self` triggern KEINE Verifikation (würde nur Credits verbrauchen).

## Output-Beispiel

```
EMAIL-VERIFIKATION (ZeroBounce): Frankfurt_Umland
  Total geprüft: 22  (API: 4, Cache: 18)
  ✓ Send (valid):       17
  ⚠ Send + Warnung (catch-all): 2
  ✗ Skip (invalid/sus): 3

  Übersprungen (Sheet auf Email-Ungültig gesetzt):
    ✗ falsche@studio.xyz  [invalid/mailbox_not_found] [api]
    ✗ test@nicht-existent.de  [invalid/no_dns_entries] [cache]
    ✗ broken@spamtrap.io  [spamtrap/-] [api]

  catch-all (versendet, aber Bounce möglich):
    ⚠ info@bsstudio.de  [api]
    ⚠ kontakt@beauty-x.de  [cache]

  Sheet-Updates: 3 OK, 0 failed

Sende JETZT 19 verifizierte Mails (inkl. 2 catch-all mit Warnung)? [y/N]:
```

## Quota-Strategie

| Use-Case | API-Calls/Monat | Strategie |
|---|---|---|
| 1× Welle Frankfurt_Umland (24 Leads) | ~24 erste Welle, 0 bei Re-Audit (Cache) | ✅ Free-Tier reicht |
| 2× Welle/Monat (München + Hamburg ~50 Leads each) | ~100 erste Wellen, ~5 bei Re-Audits | ⚠️ Limit-Grenzbereich |
| > 3 Wellen/Monat | > 100 API-Calls | ❌ Free-Quota überschritten → Bezahl-Tier oder Cache erweitern |

**Bei Quota-Exhaustion:** Pipeline bricht beim erschöpften API-Call ab, restliche Adressen werden als `QUOTA_ABORT` markiert. Send-Pipeline bricht ab — kein partieller Versand mit unverifizierten Adressen.

## Architektur

```
outreach_cli/
├── verifier/
│   ├── __init__.py            # Public API
│   ├── zerobounce.py          # API-Client + ZeroBounceConfig.from_env
│   ├── cache.py               # EmailVerifyCache (TTL 30d, atomic write)
│   └── pipeline.py            # verify_batch(emails) → BatchVerifyResult
├── commands/
│   └── verify.py              # run_verify_for_tab/_emails + Sheet-Update-Hook
└── cli.py
    ├── verify-emails (standalone Typer-Command)
    └── send → ruft run_verify_for_tab vor --confirm-live + prompt
```

## Tests

- `tests/test_verifier_cache.py` — 9 Tests (TTL, dedupe, atomic write, corruption)
- `tests/test_verifier_pipeline.py` — 9 Tests (bucketing, cache-hit, quota-abort, API-error, dedupe, etc.)
- Insgesamt: 18 neue Tests, alle 131 Tests grün.

## Bekannte Limitierungen

1. **catch-all wird gesendet, kann aber bouncen.** ZeroBounce kann bei catch-all-Domains nicht garantieren ob die Mailbox existiert. Bounce-Check (24h nach Versand) fängt das nach.
2. **`unknown` als SKIP behandelt.** Konservativ. Manche `unknown`-Adressen funktionieren — Trade-off zugunsten Reputation.
3. **Free-Quota 100/Monat.** Bei Wachstum: ZeroBounce Bezahltarif (10$ für 2000 Verifikationen).
4. **Kein automatisches "did_you_mean"-Fix.** Wenn ZeroBounce einen Typo-Fix vorschlägt (`infoo@x.de` → `info@x.de`), zeigen wir ihn nur an. Manuelle Korrektur im Sheet nötig.
5. **Bei API-Down → Send blockiert.** Wir senden NICHT ohne Verifikation. Workaround: `outreach verify-emails --tab X` einzeln aufrufen wenn API wieder da ist, dann `send --confirm-live` (alle Cache-Hits, kein API-Call mehr).
