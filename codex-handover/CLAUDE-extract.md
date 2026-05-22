# CLAUDE.md — Auszug für Codex (Frankfurt_Umland Tranche 2026-05-22)

> **Quelle:** `D:\000 SEO Business\CLAUDE.md` Stand 2026-05-22. Dies ist ein verbindlicher Auszug für Codex' Stufe-1-Arbeit. Bei Konflikt mit lokalen Kopien (`maxcontentseo-codex-assets\CLAUDE.md`) — **dieser Extract gewinnt**, weil er die aktuelle Adresse + Layer-C-Gate enthält.

---

## Adresse (verbindlich)

**Hauptstr. 29, 85551 Kirchheim b. München**

Veraltete Adresse `An den Höfen 1a, 04626 Schmölln` ist überall durch die obige zu ersetzen. Drafts aus älteren Wellen (z.B. Last-Touch 2026-05-19) tragen die alte Adresse — beim Re-Render zwingend auf neue umstellen.

---

## Lead-Qualitäts-Regeln (verbindlich)

1. Kette oder Einzelstandort? → Ketten IMMER entfernen.
2. Blog/Content vorhanden? (Pflicht-Prüfung beim Audit)
3. Service-Angebot korrekt (Beauty/Wellness/TCM)?
4. E-Mail verifiziert? (Impressum → Verzeichnisse → Maps → 11880/golocal → Kontaktformular last resort)
5. Bewertungsanzahl nur wenn auf Website sichtbar — sonst keine Zahl nennen.
6. Google-Ranking NUR mit SEO-Tool — niemals schätzen.
7. Score und Sales-Angle nur aus verifizierten Daten.

---

## Scoring (7 Kriterien, Max-Score 8)

| Krit. | Beschreibung | Punkte |
|-------|--------------|--------|
| 1 | DA ≥ 10 | +1 |
| 2 | ≥ 5 ranking Keywords lokal | +1 |
| 3 | Eigene Website (kein Free-Builder, kein Facebook-Only) | +1 |
| 4 | Service-Angebot Beauty/Wellness/TCM klar erkennbar | +1 |
| 5 | Einzelstandort (keine Kette/Filiale) | +1 |
| 6 | Inhaberin/Inhaber identifiziert (Impressum oder Über-uns) | +1 |
| 7 | **Brand-Traffic ≤ 80%** — sonst DQ | +1 |
| 8 | Sichtbarer SEO-Hebel (Blog fehlt / lokale Landingpages fehlen / Schema fehlt) | +1 |

**Krit. 7 ist auf Codex-Maschine nicht ausführbar** (kein Sistrix-Zugang) — siehe `HANDOVER-CODEX-2026-05-22.md` §3.4, Sistrix-Deferral.

---

## Pflicht-Footer (UWG/DSGVO) — verbatim

Jede Outreach-Mail (Erstmail, Follow-up, Last-Touch, Audit) endet mit den drei folgenden Blöcken — exakt, ohne Umformulierung.

**Block 1: Adresse**
```
---
MaxContentSEO – Inhaber Georg Stopfer
Hauptstr. 29, 85551 Kirchheim b. München
E-Mail: georg@maxcontentseo.de
Web: maxcontentseo.de
```

**Block 2: Rechtsgrundlage**
```
Hinweis nach UWG/DSGVO:
Sie erhalten diese Mail als gewerblicher Ansprechpartner
Ihres Studios. Rechtsgrundlage: berechtigtes Interesse
(Art. 6 Abs. 1 lit. f DSGVO) zur Anbahnung einer
B2B-Geschäftsbeziehung im Bereich SEO-Dienstleistungen
für Ihre Branche. Sollte ich keine Rückmeldung erhalten,
sende ich einmalig eine kurze Erinnerung – danach nicht
weiter.
```

**Block 3: Opt-out**
```
Kein Interesse? Eine kurze Antwort mit "Bitte streichen"
genügt – ich entferne Ihre Adresse umgehend und dauerhaft.
Widerspruch nach Art. 21 DSGVO ist jederzeit möglich.
```

**Pre-Send-Check:** Body enthält `UWG/DSGVO`, `Art. 6 Abs. 1 lit. f DSGVO`, `Bitte streichen`, `Art. 21 DSGVO`. Fehlt ein Marker → STOPP, Footer ergänzen, neu prüfen.

---

## Pflicht-Gate vor Live-Send (Email-Verifikation)

Vor jedem Live-Send gilt:

1. Empfänger-Liste durch NeverBounce (Primary) / ZeroBounce (Fallback). Frische ≤ 7 Tage.
2. Bouncer + `risky`-Adressen aus der Send-Liste rausziehen. Bei `unknown` konservativ skippen.
3. Draft-Header-Checklist: `[x] Email-Verifikation (NeverBounce) frisch` muss vor Send gesetzt sein. Unchecked = Abbruch.
4. `outreach-cli send --confirm-live` verifiziert automatisch. `one_shot_send.py` und `send_outreach.ps1` tun das **NICHT** — bei diesen Sendern Verify manuell vorab.

**Layer-C Hardfail (Stand 2026-05-22):** `one_shot_send.py` enthält jetzt `preflight_neverbounce_gate()`. Drafts ohne `[x] Email-Verifikation (NeverBounce) frisch (≤7 Tage)` im Header werden vor SMTP-Login abgewiesen (exit 2).

**Begründung (Vorfall 2026-05-21):** 2 Bouncer (`dek2beakuty@icloud.com` Typo + `info@dermacosmetic-wiesbaden.de` inaktiv) gingen durch, weil `one_shot_send.py` ohne NeverBounce-Vorlauf gesendet hat.

---

## Brand Voice & Verbotene Wörter

- **Sie-Form** durchgängig, nie Du.
- **Solo-Form:** ich/mein. "Wir" nur, wenn schon im Bestandstext. Niemals "unser Team".
- **Verbotene Wörter:** `ganzheitlich`, `synergetisch`, `performant`, `AI-native`, `leverage`, `KPI`, `Ökosystem`, `Lösungspartner`, `Augenhöhe`, `auf Augenhöhe begegnen`, `passgenaue Lösungen`, `maßgeschneidert`, `nachhaltig` (im Marketing-Sinn), `zudem`, `darüber hinaus` (→ `auch` oder weg), `eine Vielzahl von` (→ konkrete Zahl), `in der Lage sein zu` (→ `können`).
- **Anti-Floskeln:** `Ich hoffe, es geht Ihnen gut`, `Wie Sie sicher wissen…`, `Ich würde mich freuen, von Ihnen zu hören`, `Mit freundlichen Grüßen verbleibe ich…`.
- **Keine Emojis. Keine Agentur-Sprache. Keine Ranking-Versprechen. Keine erfundenen Zahlen.**
- SEO liefert Sichtbarkeit, nicht Buchungen. Erlaubt: "mehr qualifizierte Anfragen", "bessere lokale Sichtbarkeit".

---

## Pricing-Ladder (zur Info, nicht im Erstkontakt nennen)

| Produkt | Preis |
|---------|-------|
| Premium-Audit (Listenpreis) | 1.290 € |
| Referenzaktion (3 Plätze, München 2 frei) | 490 € |
| Quick Fix (200 € Credit in 14 Tagen) | 690 € |
| Aufbau | 890 € |
| Wachstum | 990 €/Monat |
| Premium | 1.490 €/Monat |

Erstkontakt + Follow-up enthalten **keine Preise**. Pricing kommt erst nach erster positiver Antwort.

---

## Lead Tracker

- Google Sheet ID: `19ak15Thx3icvmcviMLePG6d22psdWocBChTBNykorL0`
- Sheet-Name: `Lead_Tracker_Gesamt`
- Aktive Tabs: `Muenchen`, `Hamburg`, `Frankfurt`, `Frankfurt_Umland`, `Alle_Leads` (Aggregat)
- **Vor neuer Recherche immer Sheet lesen** → Duplikate vermeiden.
- Updates via `outreach-cli set-status` (Status-Felder) oder Google-Sheet-MCP (Free-Form-Felder).
