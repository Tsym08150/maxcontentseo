param(
  [Parameter(Mandatory=$true)]
  [string]$DraftFile,
  [string]$OutputFile = "D:\000 SEO Business\maxcontentseo\codex_output\roast_result.txt",
  [int]$TimeoutSeconds = 180
)

# Encoding fix für korrekte Umlaut-/Emoji-Übertragung via Pipe
$OutputEncoding = [System.Text.Encoding]::UTF8

# Sicherheits-Check
if (-not (Test-Path $DraftFile)) {
  Write-Error "[Roast] Draft-Datei nicht gefunden: $DraftFile"
  exit 1
}

# Draft laden + BOM-Strip
$draft = Get-Content $DraftFile -Raw -Encoding UTF8
$draft = $draft -replace '^\xEF\xBB\xBF', ''

# Checklist-Header abschneiden — nur ab "Subject:" oder "AN:" weitergeben
$cutMatch = [regex]::Match($draft, '(?im)^(Subject:|AN:)')
if ($cutMatch.Success) {
  $draft = $draft.Substring($cutMatch.Index)
}

# DSGVO-Footer abschneiden — DSGVO-Footer ist CLAUDE.md-Pflicht, kein Roast-Kriterium.
# Frage 3 (Screenshot/Beweis) ist für Plain-Text-E-Mail physisch nicht
# anwendbar — wird nicht als schwacher Punkt gewertet.
$footerMatch = [regex]::Match($draft, '(?m)^---\r?\n\r?\nMaxContentSEO')
if ($footerMatch.Success) {
  $draft = $draft.Substring(0, $footerMatch.Index).TrimEnd()
}

# Roast-Prompt bauen
$roastPrompt = @"
Du bist eine skeptische Studioinhaberin (Beauty/Wellness/TCM, Deutschland).
Du hast gerade eine Cold-Outreach-Mail erhalten.

Beurteile die Mail nach diesen 4 Fragen:

1. ERSTE REAKTION: Ist deine erste Reaktion "oh shit, das stimmt" oder nur "interessant"?
   → "oh shit" = stark, "interessant" = schwach

2. AGENTUR-KLANG: Klingt ein Satz wie jede andere SEO-Agentur?
   → Ja = schwach, Nein = stark
   → HINWEIS: "kurze Analyse dokumentiert — mit konkreten Ansatzpunkten" und
     "konkrete Ansatzpunkte" im CTA-Satz sind Template-Pflicht aus variante_audit.txt —
     identisch geschützt wie der Follow-up-Einstieg. Nicht als schwachen Punkt werten.

3. MESSWERT-BEWEIS: Enthält die Mail eine konkrete, nachprüfbare Zahl
   (z.B. Ladezeit in Sekunden, Google-Position, Seitenanzahl)?
   → Ja = stark (kein schwacher Punkt), Nein = schwach

4. ABSCHRECKUNG: Was schreckt ab oder wirkt unprofessionell?
   → Konkret benennen oder "nichts"
   → HINWEIS: "vor einigen Wochen hatte ich Ihnen geschrieben" ist Template-Pflicht
     bei Variante D Follow-up — nicht als schwachen Punkt werten.

BEWERTUNG:
0 schwache Punkte → GUT — Freigabe möglich
1 schwacher Punkt → ÜBERARBEITEN — was ändern
2+ schwache Punkte → NEU SCHREIBEN

Ausgabe-Format (exakt einhalten):
────────────────────────────────
ROAST-ERGEBNIS
Frage 1: [oh shit / interessant] — [1 Satz]
Frage 2: [Ja / Nein] — [1 Satz]
Frage 3: [Messwert vorhanden / kein Messwert] — [1 Satz]
Frage 4: [Was stört / nichts / Template-Pflicht] — [1 Satz]
Schwache Punkte: [0 / 1 / 2+]
Urteil: [GUT / ÜBERARBEITEN / NEU SCHREIBEN]
Empfehlung: [1-2 Sätze konkret]
────────────────────────────────

MAIL ZUM BEURTEILEN:
$draft
"@

# Roast-Prompt in temp-Datei schreiben (UTF-8 ohne BOM)
$tempFile = "D:\000 SEO Business\maxcontentseo\codex_input\roast_aktiv.txt"
[System.IO.File]::WriteAllText($tempFile, $roastPrompt, [System.Text.UTF8Encoding]::new($false))

Write-Host "[Roast] Starte Codex Roast-Pass..."
Write-Host "[Roast] Draft:  $DraftFile"
Write-Host "[Roast] Output: $OutputFile"

# Codex aufrufen
$job = Start-Job -ScriptBlock {
  param($tf, $of)
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $OutputEncoding = [System.Text.Encoding]::UTF8
  Get-Content $tf -Raw -Encoding UTF8 | codex exec `
    -o $of `
    --skip-git-repo-check `
    --ephemeral `
    -s read-only `
    -
} -ArgumentList $tempFile, $OutputFile

$completed = Wait-Job $job -Timeout $TimeoutSeconds

if (-not $completed) {
  Stop-Job $job
  Remove-Job $job -Force
  Write-Error "[Roast] Timeout nach $TimeoutSeconds Sekunden."
  exit 2
}

Receive-Job $job | Out-Null
Remove-Job $job

if (-not (Test-Path $OutputFile)) {
  Write-Error "[Roast] Output-Datei nicht erstellt: $OutputFile"
  exit 3
}

# Ergebnis lesen und parsen
$result = Get-Content $OutputFile -Raw -Encoding UTF8

# Urteil und Schwache-Punkte-Zahl extrahieren
$urteil = ""
if ($result -match "Urteil:\s*(GUT|ÜBERARBEITEN|NEU SCHREIBEN)") {
  $urteil = $Matches[1]
}
$schwach = 0
if ($result -match "Schwache Punkte:\s*(\d+)") {
  $schwach = [int]$Matches[1]
}

Write-Host ""
Write-Host "════════════════════════════════"
Write-Host "ROAST-ERGEBNIS"
Write-Host "════════════════════════════════"
Write-Host $result
Write-Host "════════════════════════════════"

# Gate-Entscheidung
switch ($urteil) {
  "GUT" {
    Write-Host "✅ Freigabe möglich — Mail kann gesendet werden."
    exit 0
  }
  "ÜBERARBEITEN" {
    Write-Host "⚠️  ÜBERARBEITEN — $schwach schwacher Punkt."
    Write-Host "→ Claude Code überarbeitet, dann erneuter Roast."
    exit 1
  }
  default {
    Write-Host "❌ NEU SCHREIBEN — $schwach schwache Punkte."
    Write-Host "→ Draft verwerfen, neu aufsetzen."
    exit 2
  }
}
