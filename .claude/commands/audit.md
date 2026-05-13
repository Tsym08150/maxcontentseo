---
description: Domain-Audit für Outreach (Ubersuggest + Firecrawl + Sistrix). Erzeugt audit-md/pdf + outreach-.txt. Argument = Domain.
---

Führe einen vollständigen Domain-Audit für `$ARGUMENTS` aus.

**Pflicht:** Nutze die `audit`-Skill-Definition in `.claude/skills/audit.md` als Workflow-Quelle — die enthält:
- Zwei-Quellen-Verifikations-Regel
- Phase 0 Redirect-Resolution (curl HEAD)
- Phase 1 Parallel-Calls: Ubersuggest MCP × 4 + Firecrawl `audit <target>` + Firecrawl `firecrawl-search "site:<target>"` + PageSpeed API + Sistrix-Scrape
- Phase 1.5 Verification
- Phase 2 Synthese + Health-Score (rekalibriert 1-10)
- Phase 3 Triple-Output

**Outputs (alle drei pflicht):**

1. `reports/audit-<sanitized-domain>-<YYYYMMDD>.md` — vollständiger Markdown-Report
2. `reports/audit-<sanitized-domain>-<YYYYMMDD>.pdf` — via Edge Headless
3. **`reports/outreach-<sanitized-domain>-<YYYYMMDD>.txt`** — fertige Outreach-Mail. Hook = Absatz 1 (Problem) + Absatz 2 (Konsequenz). Variante_audit-Template ergänzt P3-P5.

**File-Naming:** `<sanitized-domain>` = lowercased, `.` → `-`.

## Hook-Generierungs-Regeln (Sales-Standard v2 — Pflicht)

Der Hook (`{audit_hook}` in variante_audit.txt) MUSS aus genau zwei Absätzen bestehen:

### Absatz 1 — Konkrete Beobachtung (Problem)

- **Plain-Klartext, keine Tool-Sprache.** Verboten in dieser Sektion:
  - "site:" (Google-Operator-Syntax)
  - "SISTRIX" (Tool-Brand)
  - "Sichtbarkeitsindex" (Tool-Metrik-Name)
  - Tool-URLs (`app.sistrix.com/...`, Ubersuggest-Links, etc.)
- **Stattdessen:** "nur drei Seiten Ihrer Website in Google indexiert" / "praktisch nur Ihr Studio-Name führt zu Treffern" / "auf Seite 1 nicht auffindbar"
- **Verifizierungsstand explizit hedgen:** "In der geprüften Suche", "Aktuell zeigt sich", "Bei meiner Recherche" — keine absoluten Aussagen wie "Sie ranken für 0 Keywords".
- 2-3 Sätze, ~25-40 Wörter.

### Absatz 2 — Konsequenz-Framing (Big Domino)

- **Pflicht-Satz:** "Diese Anfragen gehen [aktuell/dann] an Ihre Mitbewerber." (oder semantisch äquivalent: "landen bei Mitbewerbern")
- Konkrete Beispiel-Suchen die der Empfänger LOKAL nachvollziehen kann: "wer in Wiesbaden nach 'Hydrafacial Wiesbaden' sucht..."
- 1-2 Sätze, ~20-30 Wörter.

### Hook-Word-Limit
- **P1+P2 zusammen: max. 90 Wörter** (lässt P3-P5 Raum für die ~50 Wörter aus dem Template, Gesamt-Body bleibt < 150)
- Browser-Verifiability: ja, aber als Behauptung formuliert die der Empfänger eigenständig durch Google-Suche bestätigt — nicht durch Tool-Klick.

## Quality-Gates (alle pflicht)

| Gate | Limit |
|---|---|
| Hook-Wortlimit | ≤ 90 Wörter (P1+P2) |
| Body-Wortlimit (mit Template) | ≤ 150 Wörter |
| HWG-Sperrwörter (heilen/Behandlung/Therapie/Patient/Wirkung/wirksam/Heilung) | 0 Treffer |
| **Keine Tool-Sprache in Body** | 0 Treffer: "site:", "SISTRIX", "Sichtbarkeitsindex", Tool-URLs |
| **Konsequenz-Satz vorhanden** | Pflicht: "Mitbewerber" + Konsequenz-Verb (gehen/landen/bekommen) |
| Verifizierungsstand-Hedging | mind. eines: "In der geprüften Suche" / "Aktuell zeigt sich" / "Bei meiner Recherche" |
| Subject-Format | "Kurze Frage zu Ihrem {Business-Type} in {Ort}" |
| UTF-8 Encoding | ohne BOM |
| `[NAME]` / `[ABSENDER]` als Platzhalter | drin gelassen wenn nicht auflösbar |

## Template-Integration

Das `variante_audit.txt`-Template injiziert den Hook als `{audit_hook}` und ergänzt:
- **P3 (Hoffnung):** "Die gute Nachricht: oft reichen wenige gezielte Anpassungen..."
- **P4 (Audit-Wertigkeit):** "Sichtbarkeitscheck + 3-Punkte-Prioritätenliste"
- **P5 (CTA):** "Ein kurzes 'Ja' per Antwort genügt."

→ Hook schreibt P1+P2 NUR. Nicht P3-P5 im Audit-Outreach-Hook dazupacken (sonst Duplikation mit Template).

## Am Ende der Session

Gib eine kompakte Chat-Zusammenfassung:
- Health-Score (X/10)
- Verdict (one-liner)
- **Outreach-Hook im Klartext** (P1+P2, der genaue Text der in der .txt steht)
- Pfade zu allen drei Output-Files

Wenn `$ARGUMENTS` leer ist: fehle laut mit Hinweis `Nutzung: /audit <domain>`.
