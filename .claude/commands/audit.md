---
description: Domain-Audit für Outreach (Ubersuggest + Firecrawl + Sistrix). Erzeugt audit-md/pdf + outreach-.txt. Argument = Domain.
---

Führe einen vollständigen Domain-Audit für `$ARGUMENTS` aus.

**Pflicht:** Nutze die `audit`-Skill-Definition in `.claude/skills/audit.md` als Workflow-Quelle — die enthält:
- Zwei-Quellen-Verifikations-Regel
- Phase 0 Redirect-Resolution (curl HEAD)
- Phase 1 Parallel-Calls: Ubersuggest MCP × 4 (domain_overview, domain_keywords, domain_top_pages, backlinks_overview) + Firecrawl `audit <target>` + Firecrawl `firecrawl-search "site:<target>"` + PageSpeed API + Sistrix-Scrape (`app.sistrix.com/de/visibility-index?domain=<input>`)
- Phase 1.5 Verification (WebFetch / ctx_fetch_and_index gegen Firecrawl-Befunde)
- Phase 2 Synthese + Health-Score (rekalibriert 1-10)
- Phase 3 Triple-Output

**Outputs (alle drei pflicht):**

1. `reports/audit-<sanitized-domain>-<YYYYMMDD>.md` — vollständiger Markdown-Report
2. `reports/audit-<sanitized-domain>-<YYYYMMDD>.pdf` — via Edge Headless (Skill-Block "PDF-Generation")
3. **`reports/outreach-<sanitized-domain>-<YYYYMMDD>.txt`** — fertige Variante-C-Outreach-Mail mit personalisiertem Hook aus den verifizierten Befunden

**File-Naming:** `<sanitized-domain>` = Domain lowercased, `.` → `-` (z.B. `vitaminbude.de` → `vitaminbude-de`).

**Pflicht-Regeln aus dem Skill:**
- Business-Type-Detection (Studio/Shop/Praxis/Salon/Spa/Center/Unternehmen) bestimmt Subject und Body-Wording
- Outreach-Hook nur aus **verifizierten** Befunden (2-Quellen-Regel)
- Browser-Verifiability-Filter: nur Befunde die der Empfänger in < 30 s im Browser nachprüfen kann landen im Hook
- HWG-konform: keine Heil-/Behandlungs-/Patient-Wörter, max 120 Wörter Body
- UTF-8 ohne BOM für .txt

**Am Ende der Session:**

Gib eine kompakte Chat-Zusammenfassung:
- Health-Score (X/10)
- Verdict (one-liner)
- **Outreach-Hook im Klartext** (der genaue Hook-Text der in `outreach-<domain>-<date>.txt` steht — Empfänger-fertig nach Auflösen von [NAME]/[ORT]/[ABSENDER])
- Pfade zu allen drei Output-Files

Wenn `$ARGUMENTS` leer ist: fehle laut mit Hinweis `Nutzung: /audit <domain>`.

Wenn der Audit-Skill in `.claude/skills/audit.md` nicht geladen wird (z.B. weil neue Session), lies ihn explizit als Workflow-Spec.
