# outreach-cli: Bounce-Check + Task-Scheduler

## Use Case

Nach `outreach send --confirm-live` werden Outreach-Mails an Leads geschickt. Einige Adressen sind ungültig (Tippfehler, abgelaufene Domains, leere Postfächer). ProtonMail antwortet darauf mit `MAILER-DAEMON`-Bounce-Mails im Posteingang von `georg@maxcontentseo.de`.

Ohne Bounce-Check landen diese Leads in der nächsten Outreach-Welle wieder — die Reputation der Sender-Domain leidet.

Dieser Workflow automatisiert:
- **Detection:** IMAP über ProtonMail Bridge → MAILER-DAEMON-Mails finden
- **Parsing:** Failed-Recipient aus jeder Bounce-Mail extrahieren
- **Sheet-Update:** `Recherche_Status` = "Bounce" via `SheetClient.set_status`
- **Scheduling:** Automatisch 24h nach Versand + wöchentlich Montag 09:00

## Setup (einmalig)

### 1. Bridge muss laufen

ProtonMail Bridge startet automatisch beim System-Start. Prüfen mit:
```powershell
tasklist | findstr bridge.exe
netstat -an | findstr 127.0.0.1:1143
```

### 2. Env-Variablen in `.env`

```ini
IMAP_HOST=127.0.0.1
IMAP_PORT=1143
PROTON_IMAP_USER=georg@maxcontentseo.de
PROTONMAIL_BRIDGE_PASSWORD=<16-Zeichen-Token aus Bridge GUI>
```

Falls `PROTONMAIL_BRIDGE_PASSWORD` leer ist, fällt der Code zurück auf:
1. `PROTON_IMAP_PASSWORD`
2. `SMTP_TOKEN` (häufig identisch, weil Bridge ein einziges Token für beide nutzt)

**Bridge "no such user"?** → Die in `PROTON_IMAP_USER` eingetragene Adresse stimmt nicht mit der in Bridge konfigurierten Mailbox-Address überein. Bridge GUI öffnen → "Mailbox configuration" → exakte Adresse kopieren.

### 3. Wöchentlichen Task installieren

```powershell
py -m outreach_cli install-weekly-bounce
# oder mit Custom-Slot:
py -m outreach_cli install-weekly-bounce --weekday Tuesday --hour 10
```

Task-Name: `MaxContentSEO_WeeklyBounceCheck`. Idempotent (überschreibt existierende).

Prüfen: `schtasks /Query /TN MaxContentSEO_WeeklyBounceCheck`
Entfernen: `schtasks /Delete /TN MaxContentSEO_WeeklyBounceCheck /F`

## Automatik

### Auto-Schedule nach `--confirm-live`

Wenn `outreach send --confirm-live` mindestens **eine Mail erfolgreich versendet** hat, wird automatisch ein Task erstellt:

- Name: `MaxContentSEO_BounceCheck_YYYYMMDD_HHMMSS`
- Trigger: einmalig, 24h nach jetzt
- Action: `py -m outreach_cli bounce-check --tab <gesendeter-Tab>`
- Auto-Delete: 1 Tag nach Ausführung (kein Müll im Scheduler)

Du siehst eine Bestätigung im Send-Output:
```
⏰ Bounce-Check geplant: 'MaxContentSEO_BounceCheck_20260512_201500' @ 2026-05-13 20:15 (in 24h, schtasks)
```

### Wöchentlicher Sweep (Montag 09:00)

Über alle Tabs (`PRIMARY_TABS + AGGREGATE_TABS`). Fängt späte Bounces auf, die nach dem 24h-Fenster zurückkamen.

## Manueller Aufruf

```powershell
# Ein Tab, Default 2-Tage-Fenster
py -m outreach_cli bounce-check --tab Frankfurt_Umland

# Alle Tabs, 7-Tage-Fenster
py -m outreach_cli bounce-check --all-tabs --since-days 7

# Dry-Run — nur Detection, kein Sheet-Update
py -m outreach_cli bounce-check --tab Frankfurt_Umland --dry-run

# JSON-Output (für Scripting)
py -m outreach_cli bounce-check --tab X --json
```

## Output-Beispiel

```
BOUNCE-CHECK: Frankfurt_Umland (seit 2d)
  Angeschrieben im Scope:  20
  Bounce-Mails gefunden:   3
  Failed-Recipients:       3
  In Sheet gematched:      2
  Nicht im Sheet:          1
  Sheet-Writes OK:         2
  Bounce-Rate: 10.00%

  Gebouncte Adressen (im Sheet aktualisiert):
    ✓ falsche@studio-xyz.de [permanent] · Frankfurt_Umland/Studio XYZ
    ✓ leer@leere-domain.de [permanent] · Frankfurt_Umland/Leere Domain

  Bounces ohne Sheet-Match (1):
    · unknown@example.de
```

## Bounce-Rate-Farb-Codes

- 🟢 Grün < 2%  — gesunde Liste
- 🟡 Gelb 2-5% — beobachten
- 🔴 Rot ≥ 5%  — Listen-Hygiene nötig (Pre-Validation der Adressen)

## Bounce-Typ-Klassifikation

| Typ | Trigger | Sheet-Update |
|---|---|---|
| **permanent** | 5xx SMTP-Code, "Undelivered Mail Returned", "user unknown" | ✓ Status = Bounce |
| **transient** | 4xx SMTP-Code, "Delayed Mail (still being retried)" | ✓ Status = Bounce (Hinweis: kann sich erholen) |
| **unknown** | Pattern unklar | ✓ Status = Bounce (Manuelle Prüfung empfohlen) |

Aktuell setzen wir **alle drei Typen** auf "Bounce" — Konservativ. Spätere Iteration könnte transient ignorieren und nur permanent eintragen.

## Architektur

```
outreach_cli/
├── imap/
│   ├── __init__.py         # Public API: BridgeImapClient, parse_bounce
│   ├── client.py           # imaplib + STARTTLS + ImapConfig.from_env
│   └── parser.py           # MIME-Parse, Final-Recipient-Extraktion
├── commands/
│   ├── bounce_check.py     # run_bounce_check(...) — Sheet-Cross-Ref
│   └── scheduler.py        # schtasks-XML-Wrapper (ONCE + WEEKLY)
└── cli.py
    ├── bounce-check (Typer-Command)
    ├── install-weekly-bounce (Typer-Command)
    └── send → auto-schedule after confirm-live
```

## Bekannte Limitierungen

1. **Bridge muss laufen.** Wenn Bridge offline (z.B. nach System-Reboot ohne Auto-Start), schlägt bounce-check fehl. Lösung: Bridge in "Autostart with Windows" konfigurieren.
2. **`no such user` Bridge-Quirk.** Wenn Bridge die in `PROTON_IMAP_USER` eingetragene Adresse nicht kennt, hilft nur Bridge GUI öffnen + exakte Adresse kopieren. Der Code gibt einen Hint mit den nötigen Schritten.
3. **Transient-Bounces zählen wie Permanent.** Ein 4xx-deferred-Mail könnte beim nächsten Retry doch zugestellt werden. Wir markieren konservativ als "Bounce" — Caller kann später manuell zurücksetzen.
4. **IMAP-Window: 2 Tage default.** Bei langem Versand-Zyklus (mehr als 48h zwischen Welle und Check) `--since-days 7` nutzen.
5. **Task-Scheduler Windows-only.** macOS/Linux würden `launchd` / `cron` brauchen — aktuell nicht implementiert.
