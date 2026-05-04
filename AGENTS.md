# AGENTS.md — Projektregeln für maxcontentseo.de

Dies ist die dauerhafte Projektanweisung für Codex und andere AI-Coding-Agents,
die in diesem Repo arbeiten. Diese Regeln gelten für **jeden** Run und müssen
bei **jeder** Änderung beachtet werden.

---

## Projekt-Kontext

- **Was:** Statische Website für MaxContentSEO, ein Solo-SEO-Business
- **Wer:** Georg Stopfer, Solo-Berater (kein Team, keine Agentur)
- **Zielgruppe:** Lokale Dienstleister im Beauty-, Wellness- und TCM-Bereich
- **Hosting:** GitHub Pages (statisch, kein Build-Step)
- **Stack:** HTML, CSS, vanilla JS — keine Frameworks, kein NPM
- **Sprache der Inhalte:** Deutsch (Sie-Form)

---

## Brand Voice — nicht verletzen

1. **"Sie"-Form**, niemals "Du" oder "Dir"
2. **Klares, einfaches Deutsch** — keine Agentur-Floskeln
3. **Verbotene Wörter:** "ganzheitlich", "synergetisch", "performant",
   "AI-native", "leverage", "KPI", "Ökosystem", "Lösungspartner",
   "Augenhöhe", "auf Augenhöhe begegnen", "passgenaue Lösungen"
4. **"Wir" nur dann**, wenn schon im Text vorhanden — sonst Solo-Form
   ("ich", "mein"). Niemals "unser Team".
5. **Keine erfundenen Floskel-Zwischentitel** wie "Praxisbeispiel",
   "Real Insights", "Strategischer Approach". Bestehende Section-Header
   bleiben oder werden durch konkrete, sachliche Alternativen ersetzt.

---

## Faktentreue — keine Halluzinationen

1. **Keine erfundenen Zahlen.** Wenn eine Zahl nicht im Repo oder in
   bestehenden Inhalten belegt ist, NICHT hinzufügen.
2. **Keine erfundenen Testimonials, Kundenstimmen oder Logos.**
3. **Keine erfundenen Case Studies.** Es gibt aktuell genau einen Case:
   LingQi — TCM Head Spa München. Alles andere wäre erfunden.
4. **Keine konkreten Ranking-Versprechen** ("Top 1 in 4 Wochen" etc.).
5. **Keine Suchvolumen-Zahlen oder Suchvolumen-Ranges erfinden.**
   Auch Angaben wie "100–500 Suchen/Monat" sind nicht erlaubt, wenn sie
   nicht aus einem konkreten Tool oder Screenshot stammen. Erlaubt sind
   nur Beispiel-Suchmuster ohne Volumenangabe.
6. **Keine kausalen Ergebnisversprechen** ("mehr Buchungen", "X% mehr
   Umsatz"). SEO liefert Sichtbarkeit, nicht Buchungen. Erlaubt:
   "mehr qualifizierte Anfragen", "bessere Sichtbarkeit", "mehr Reichweite
   bei kaufnahen Suchanfragen".
7. **Keine Heilversprechen oder medizinischen Wirkaussagen** zu
   Behandlungen wie Microneedling, Hydrafacial, TCM-Anwendungen etc.
   Behandlungsnamen dürfen als Keywords genannt werden, aber **ohne**
   Aussagen zu Wirkung, Dauer, Schmerzfreiheit, Hautverbesserung.

---

## Lizenzrecht & Assets

1. **Keine externen Bilder, Icons, Fonts** ohne klare Lizenz im Repo.
2. **Keine kostenpflichtigen Web-Fonts** (Aeonik, GT America, Editorial
   New, Söhne etc.).
3. **Erlaubte Fonts:**
   - System-Fonts (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`,
     `system-ui`, `sans-serif`)
   - Lokal im Repo vorhandene, lizenzierte Font-Dateien
4. **Nicht erlaubt:**
   - Google Fonts per externer URL laden (DSGVO-Risiko in Deutschland)
   - Adobe Fonts, Typekit, Fontshare oder andere externe Font-CDNs
   - Neue Font-Dateien hinzufügen, wenn die Lizenz nicht im Repo
     dokumentiert ist
5. **Keine Stockfotos generieren oder einbinden** (auch keine
   AI-generierten Bilder von "Frauen mit Gesichtsmasken" o.ä.).
6. **CSS-Platzhalter statt echter Bilder** verwenden, solange keine
   eigenen Assets im Repo liegen.

---

## Performance & Stack

1. **Lighthouse Performance Score muss >= 90 bleiben.**
2. **Kein JS-Framework** (React, Vue, Svelte etc.).
3. **Kein NPM, keine package.json, kein node_modules** anlegen oder
   verändern. Site ist reine HTML/CSS/JS-Static-Site.
4. **Keine externen CDN-Scripts**, außer absolut notwendig.
5. **Kein Build-Step.** Site muss weiterhin direkt von GitHub Pages
   ausgeliefert werden.
6. **Keine Video-Hintergründe.**
7. **Animationen nur, wenn explizit angefragt** — keine "schickeren"
   Mikroanimationen ohne Auftrag.

---

## Scope-Disziplin

1. **Nur Dateien anfassen, die im Goal explizit genannt sind.**
2. **Kein "Refactoring nebenbei"** — auch wenn Code suboptimal aussieht.
3. **Texte außerhalb der Goal-Sektion nicht umformulieren,** auch nicht
   zur "Verbesserung". Texte sind Brand-relevant.
4. **Keine Layout-Änderungen** an Sektionen, die nicht im Scope sind.
5. **Keine Style-Änderungen am globalen Theme,** außer im Goal explizit
   gefordert.

---

## Git- und Deployment-Sicherheit

1. **Codex darf keine Commits erstellen.**
2. **Codex darf nicht pushen.**
3. **Codex darf nicht deployen.**
4. **Codex darf keine GitHub-Actions, DNS-, Hosting- oder
   Deployment-Konfigurationen ändern** (`.github/`, `CNAME`,
   `_config.yml` etc.).

Codex bereitet Änderungen lokal vor. Commit, Push und Deploy macht
ausschließlich der Mensch nach Review.

---

## Reports — Pflicht nach jedem Run

Am Ende jedes Codex-Runs einen Report unter `/reports/` anlegen, mit
sprechendem Namen nach Schema:

```
/reports/codex-goal-NN-kurzname.md
```

Beispiele:
- `/reports/codex-goal-01-lingqi-case.md`
- `/reports/codex-goal-02-pricing.md`
- `/reports/codex-goal-03-whitespace.md`

Inhalt jedes Reports:

1. **Goal-Bezeichnung und Datum**
2. **Geänderte Dateien** (Liste mit Pfaden)
3. **Untracked Dateien** (neu angelegt)
4. **Was wurde geändert** (kurze Beschreibung pro Datei)
5. **Was wurde bewusst nicht geändert** (wenn relevant)
6. **Offene Fragen für Human Review**
7. **Asset- und Lizenzhinweise** (welche Schriften/Bilder verwendet)
8. **Lighthouse-Score** (vor/nach, falls Performance-relevant)

Reports werden **nicht** überschrieben — jedes Goal hat seinen eigenen.

---

## Stop-Bedingungen

Codex stoppt und meldet zurück, **anstatt** weiterzumachen, wenn:

1. Ein Goal nur durch Verletzung dieser Regeln umsetzbar wäre
2. Wesentliche Informationen fehlen, die nicht durch das Goal
   explizit als "Placeholder erlaubt" markiert sind
3. Ein Asset nötig wäre, dessen Lizenz unklar ist
4. Die Brand Voice nur durch Erfindung von Inhalten gehalten werden könnte

**Nicht** silently Tradeoffs eingehen. Lieber abbrechen und fragen.

---

## Inspirationsquellen — nicht 1:1 kopieren

Wenn andere Sites als Referenz genannt werden (z.B. terminal-industries.com):

- **Erlaubt:** Architektur-Patterns, Spacing-Disziplin, Typo-Hierarchie
- **Nicht erlaubt:** Farben, Schriften, Bilder, Animationen, Texte,
  Layout 1:1 übernehmen
- **Niemals:** Assets von der Referenz-Site herunterladen und einbinden

---

## Pre-Commit-Checkliste (für den Menschen, nicht Codex)

Nach jedem Codex-Run, **bevor du committest**:

- [ ] Mobile bei 375px: kein horizontaler Scroll
- [ ] Desktop bei 1440px: keine zerrissenen Layouts
- [ ] Alle CTAs funktionieren (Anchor-Links, Forms)
- [ ] Lighthouse Performance >= 90
- [ ] Keine Console-Errors
- [ ] Keine kaputten internen Links
- [ ] Report unter `/reports/` ist vollständig
- [ ] Keine ungewollten Datei-Änderungen außerhalb des Scopes

---

## Was Codex bei Unsicherheit tun soll

1. **Lieber weniger ändern als zu viel.**
2. **Lieber konservativ formulieren als überversprechen.**
3. **Lieber im Report nachfragen als raten.**

Diese Site verkauft Vertrauen. Jede falsche Zahl, jede leere Floskel,
jeder kopierte Stockfoto-Look schwächt das Geschäft. Im Zweifel:
weniger ist mehr.
