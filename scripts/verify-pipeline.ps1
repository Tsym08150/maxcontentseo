<#
.SYNOPSIS
  Audit-Verifikations-Pipeline: Stages audit-report for Codex-Laptop, polls for verify-report.

.DESCRIPTION
  Workflow:
    1. Findet aktuellsten audit-<domain>-<date>.md in reports/
    2. Stages audit + outreach via Git (Primär) und/oder OneDrive (Fallback)
    3. Zeigt klare Anleitung für Laptop-Seite (Codex starten, Prompt einlesen)
    4. Pollt das Repo nach verify-<domain>-<date>.md
    5. Bei Eingang: pull, gibt Pfad + Verdict zurück

.PARAMETER Domain
  Domain wie im audit-Filename (z.B. "vitaminbude-de").
  Wenn weggelassen, nimmt der Pipeline das neueste audit-*.md.

.PARAMETER TimeoutMinutes
  Wie lange auf Verify-Report warten. Default: 15 Minuten.

.PARAMETER PollIntervalSeconds
  Wie oft prüfen. Default: 20 s.

.PARAMETER Channel
  "git", "onedrive", oder "auto" (default). Bei "auto" wird Git bevorzugt.

.EXAMPLE
  .\scripts\verify-pipeline.ps1
  .\scripts\verify-pipeline.ps1 -Domain vitaminbude-de -TimeoutMinutes 30
  .\scripts\verify-pipeline.ps1 -Channel onedrive
#>

[CmdletBinding()]
param(
  [string]$Domain,
  [int]$TimeoutMinutes = 15,
  [int]$PollIntervalSeconds = 20,
  [ValidateSet("git","onedrive","auto")]
  [string]$Channel = "auto"
)

$ErrorActionPreference = "Stop"

# Repo-Root deterministisch ermitteln (Skript liegt in scripts/)
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host ""
Write-Host "=== Audit-Verify-Pipeline ===" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"
Write-Host ""

# ----------------------------------------
# 1. Audit-Report finden
# ----------------------------------------
if (-not $Domain) {
  $latestAudit = Get-ChildItem -Path "reports" -Filter "audit-*.md" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if (-not $latestAudit) {
    Write-Host "[FEHLER] Kein audit-*.md in reports/ gefunden." -ForegroundColor Red
    exit 1
  }
  # Extrahiere Domain aus Filename "audit-<domain>-<date>.md" (mit optionalem -vN)
  if ($latestAudit.BaseName -match '^audit-(.+?)-(\d{8})(-v\d+)?$') {
    $Domain = $Matches[1]
    $DateStamp = $Matches[2]
    $VersionSuffix = $Matches[3]
  } else {
    Write-Host "[FEHLER] Audit-Filename '$($latestAudit.Name)' folgt nicht der Konvention 'audit-<domain>-<YYYYMMDD>[-vN].md'" -ForegroundColor Red
    exit 1
  }
} else {
  $DateStamp = Get-Date -Format "yyyyMMdd"
  $auditCandidates = Get-ChildItem -Path "reports" -Filter "audit-$Domain-*.md" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending
  if (-not $auditCandidates) {
    Write-Host "[FEHLER] Kein audit-$Domain-*.md in reports/ gefunden." -ForegroundColor Red
    exit 1
  }
  $latestAudit = $auditCandidates | Select-Object -First 1
  if ($latestAudit.BaseName -match '^audit-(.+?)-(\d{8})(-v\d+)?$') {
    $DateStamp = $Matches[2]
    $VersionSuffix = $Matches[3]
  }
}

$auditBaseName = $latestAudit.BaseName  # z.B. "audit-vitaminbude-de-20260512-v3"
$outreachFile = "reports/outreach-$Domain-$DateStamp$VersionSuffix.txt"
$verifyFile = "reports/verify-$Domain-$DateStamp$VersionSuffix.md"

Write-Host "Audit-Report:  $($latestAudit.FullName)"
Write-Host "Outreach-Mail: $RepoRoot\$outreachFile"
Write-Host "Erwarte:       $RepoRoot\$verifyFile"
Write-Host ""

# Sanity: Outreach-Datei existiert?
if (-not (Test-Path $outreachFile)) {
  Write-Host "[WARNUNG] Outreach-Mail fehlt: $outreachFile" -ForegroundColor Yellow
  Write-Host "          Codex wird trotzdem versuchen zu verifizieren, aber der Mail-Plausibilitäts-Check entfällt."
  Write-Host ""
}

# ----------------------------------------
# 2. Channel wählen
# ----------------------------------------
$useGit = $false
$useOneDrive = $false

$hasGitRemote = $false
try {
  $remoteOutput = git remote get-url origin 2>$null
  if ($LASTEXITCODE -eq 0 -and $remoteOutput) {
    $hasGitRemote = $true
    $gitRemoteUrl = $remoteOutput.Trim()
  }
} catch {}

$oneDrivePath = "$env:USERPROFILE\OneDrive\audit-verify-bridge"
$hasOneDrive = Test-Path "$env:USERPROFILE\OneDrive"

if ($Channel -eq "auto") {
  if ($hasGitRemote) { $useGit = $true }
  elseif ($hasOneDrive) { $useOneDrive = $true }
  else {
    Write-Host "[FEHLER] Weder Git-Remote noch OneDrive verfügbar." -ForegroundColor Red
    exit 2
  }
} elseif ($Channel -eq "git") {
  if (-not $hasGitRemote) {
    Write-Host "[FEHLER] Channel=git gewählt, aber kein origin-Remote." -ForegroundColor Red
    exit 2
  }
  $useGit = $true
} else {
  if (-not $hasOneDrive) {
    Write-Host "[FEHLER] Channel=onedrive gewählt, aber kein OneDrive-Pfad." -ForegroundColor Red
    exit 2
  }
  $useOneDrive = $true
}

if ($useGit)     { Write-Host "Channel: Git ($gitRemoteUrl)" -ForegroundColor Green }
if ($useOneDrive){ Write-Host "Channel: OneDrive ($oneDrivePath)" -ForegroundColor Green }
Write-Host ""

# ----------------------------------------
# 3. Stage to channel
# ----------------------------------------
if ($useGit) {
  Write-Host "[1/4] Audit + Outreach + Verify-Prompt nach GitHub pushen..."
  git add $latestAudit.FullName 2>&1 | Out-Null
  if (Test-Path $outreachFile)        { git add $outreachFile 2>&1 | Out-Null }
  if (Test-Path ".claude/prompts/codex-verify.md") { git add ".claude/prompts/codex-verify.md" 2>&1 | Out-Null }
  $hasChanges = (git diff --cached --name-only).Length -gt 0
  if ($hasChanges) {
    git commit -m "verify-pipeline: stage $auditBaseName for laptop verification" 2>&1 | Out-Null
    git push origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
      Write-Host "[WARNUNG] git push fehlgeschlagen — Laptop muss manuell pullen." -ForegroundColor Yellow
    } else {
      Write-Host "  ✓ pushed" -ForegroundColor Green
    }
  } else {
    Write-Host "  ✓ keine neuen Changes (bereits gepusht)" -ForegroundColor Green
  }
}

if ($useOneDrive) {
  Write-Host "[1/4] Audit + Outreach + Verify-Prompt nach OneDrive kopieren..."
  if (-not (Test-Path $oneDrivePath)) { New-Item -ItemType Directory -Path $oneDrivePath | Out-Null }
  Copy-Item $latestAudit.FullName $oneDrivePath -Force
  if (Test-Path $outreachFile) { Copy-Item $outreachFile $oneDrivePath -Force }
  Copy-Item ".claude/prompts/codex-verify.md" $oneDrivePath -Force
  Write-Host "  ✓ kopiert nach $oneDrivePath" -ForegroundColor Green
}

# ----------------------------------------
# 4. Anleitung für Laptop ausgeben (manuell, da kein SSH/RDP konfiguriert)
# ----------------------------------------
Write-Host ""
Write-Host "[2/4] Laptop-Seite (manueller Schritt):" -ForegroundColor Cyan
Write-Host "  ──────────────────────────────────────────────────────"
if ($useGit) {
  Write-Host "  Auf dem Laptop in einem Terminal:"
  Write-Host "    cd <pfad-zum-maxcontentseo-clone>"
  Write-Host "    git pull origin main"
  Write-Host "    codex run --prompt .claude/prompts/codex-verify.md `\"
  Write-Host "              --input reports/$($latestAudit.Name) `\"
  Write-Host "              --input $outreachFile `\"
  Write-Host "              --output $verifyFile"
  Write-Host "    git add $verifyFile"
  Write-Host "    git commit -m `"verify: $Domain`""
  Write-Host "    git push origin main"
}
if ($useOneDrive) {
  Write-Host "  Auf dem Laptop in OneDrive\audit-verify-bridge\:"
  Write-Host "    1. Öffne Codex mit codex-verify.md als Prompt"
  Write-Host "    2. Inputs: $($latestAudit.Name), $(Split-Path $outreachFile -Leaf)"
  Write-Host "    3. Output speichern als: $(Split-Path $verifyFile -Leaf)"
  Write-Host "    4. OneDrive synct automatisch zurück"
}
Write-Host "  ──────────────────────────────────────────────────────"
Write-Host ""

# ----------------------------------------
# 5. Pollen
# ----------------------------------------
Write-Host "[3/4] Polle auf $verifyFile (Timeout: $TimeoutMinutes Min, Intervall: $PollIntervalSeconds s)" -ForegroundColor Cyan
Write-Host ""

$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
$found = $false
$dotCount = 0

while ((Get-Date) -lt $deadline) {
  if ($useGit) {
    git fetch origin main 2>&1 | Out-Null
    # Check if verify file is in remote
    $remoteHasFile = $false
    $lsTreeOutput = git ls-tree -r --name-only origin/main 2>$null
    if ($LASTEXITCODE -eq 0 -and ($lsTreeOutput -contains $verifyFile)) {
      $remoteHasFile = $true
      git pull origin main 2>&1 | Out-Null
    }
    if ($remoteHasFile -and (Test-Path $verifyFile)) {
      $found = $true
      break
    }
  }

  if ($useOneDrive) {
    $oneDriveVerify = Join-Path $oneDrivePath (Split-Path $verifyFile -Leaf)
    if (Test-Path $oneDriveVerify) {
      Copy-Item $oneDriveVerify $verifyFile -Force
      $found = $true
      break
    }
  }

  Write-Host -NoNewline "."
  $dotCount++
  if ($dotCount % 30 -eq 0) {
    $remain = [int]($deadline - (Get-Date)).TotalMinutes
    Write-Host " ($remain Min verbleiben)"
  }
  Start-Sleep -Seconds $PollIntervalSeconds
}

Write-Host ""
Write-Host ""

if (-not $found) {
  Write-Host "[TIMEOUT] Keine Verify-Datei nach $TimeoutMinutes Min." -ForegroundColor Red
  Write-Host "          Prüfe Laptop-Seite manuell. Erwarteter Pfad: $verifyFile" -ForegroundColor Red
  exit 3
}

# ----------------------------------------
# 6. Verdict-Extraktion
# ----------------------------------------
Write-Host "[4/4] Verify-Report eingegangen: $verifyFile" -ForegroundColor Green

$verifyContent = Get-Content $verifyFile -Raw
$verdictLine = ($verifyContent -split "`n" | Where-Object { $_ -match '^\*\*Verdict:\*\*' } | Select-Object -First 1)

if ($verdictLine) {
  Write-Host ""
  if ($verdictLine -match 'FREIGEGEBEN') {
    Write-Host "  VERDICT: $verdictLine" -ForegroundColor Green
  } elseif ($verdictLine -match 'KORREKTUREN') {
    Write-Host "  VERDICT: $verdictLine" -ForegroundColor Yellow
  } elseif ($verdictLine -match 'ABGELEHNT') {
    Write-Host "  VERDICT: $verdictLine" -ForegroundColor Red
  } else {
    Write-Host "  VERDICT: $verdictLine"
  }
}

Write-Host ""
Write-Host "Vollständiger Report: $verifyFile"
Write-Host ""
Write-Host "Nächster Schritt: In Claude Code 'Lies $verifyFile und gib finale Freigabe' eingeben."

# Exit-Code basiert auf Verdict (für CI/Scripting-Integration)
if ($verdictLine -match 'FREIGEGEBEN') { exit 0 }
elseif ($verdictLine -match 'KORREKTUREN') { exit 10 }
elseif ($verdictLine -match 'ABGELEHNT') { exit 20 }
else { exit 0 }
