# RULES.md — Lead-Pipeline Hard Rules

Verbindliche Regeln für die Lead-Qualifizierung. Ergänzt CLAUDE.md / AGENTS.md.

---

## ⚠️ Pipeline_v2_Qualified ist KEINE verlässliche „Frisch"-Quelle

**Regel:** Der Sheet-Tab `Pipeline_v2_Qualified` (Sheet
`19ak15Thx3icvmcviMLePG6d22psdWocBChTBNykorL0`) darf **niemals** allein als
Beleg dafür gelten, dass ein Lead frisch / unkontaktiert / sendbar ist.

Sein `OUTREACH_STATUS` läuft erfahrungsgemäß out-of-sync: Score-Engine-Zeilen
bleiben auf `Nicht kontaktiert` stehen, obwohl Erst- und Follow-up-Mails längst
raus sind. Der reale Kontaktstatus lebt in den **Geo-Tabs**
(`Hamburg`, `Muenchen`, `Frankfurt`, `Frankfurt_Umland`, `Bad Homburg`,
`Alle_Leads`) und in `Tools/sent_log.csv` / `Tools/leads.csv`.

**Pflicht-Cross-Check vor jeder Qualifizierung / jedem Send:**

Ein Lead aus `Pipeline_v2_Qualified` gilt nur dann als frisch, wenn **alle**
folgenden Quellen das bestätigen:

1. `Pipeline_v2_Qualified.OUTREACH_STATUS` = `Nicht kontaktiert`, **und**
2. E-Mail **nicht** in `Tools/sent_log.csv`, **und**
3. E-Mail in **keinem** Geo-Tab mit Status aus
   {`Angeschrieben`, `Follow-up gesendet`, `Versendet`, `Reply`, `Closed`,
   `HOT`, `WARM`, `Bounce`}, **und**
4. kein existierender Audit-Report unter `reports/` (`audit-<domain>-*`,
   `codex-audit-<name>*`).

Schlägt **eine** Quelle an → Lead ist **nicht** frisch → kein Audit, kein Send.

**Anti-Pattern:** `Pipeline_v2_Qualified` blind als Batch-Quelle übernehmen,
weil dort alles auf `Nicht kontaktiert` steht.

### Vorfall 2026-06-02 (Begründung)

Bei einem Stufe-1-Probelauf wurden 9 vermeintlich frische
`Pipeline_v2_Qualified`-Leads vorgelegt. Cross-Check ergab: **alle 13 Zeilen
des Tabs** standen fälschlich auf `Nicht kontaktiert`, waren aber real bereits
kontaktiert (Erstmail 28.04–19.05.2026, die meisten zusätzlich Follow-up).
Ohne Cross-Check wären bis zu 13 Studios erneut — mehrere zum dritten Mal —
angeschrieben worden. Der Tab wurde anschließend auf den realen Geo-Tab-Status
reconciled (Spalte `OUTREACH_STATUS`); Dubletten werden in Spalte `HINWEIS`
vermerkt (z. B. Carries: `.com`/`.art` = selbes Studio).

Dieselbe Lehre wie der Phase-−1-Vorfall 2026-05-19 (Sheet sagte „Follow-up",
CSV sagte „sent" — eine Quelle allein reichte nicht; 13 Leads beinahe 3× kontaktiert).
