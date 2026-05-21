param(
    [Parameter(Mandatory = $true)]
    [string]$StudioName,

    [Parameter(Mandatory = $true)]
    [string]$Stadt,

    [Parameter(Mandatory = $true)]
    [string]$Domain,

    [Parameter(Mandatory = $true)]
    [string]$ImpressumScrapePath,

    [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ImpressumPostalCode {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path)) {
        return ""
    }

    $content = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
    $match = [regex]::Match($content, "\b\d{5}\b")
    if ($match.Success) {
        return $match.Value
    }

    return ""
}

$plz = Get-ImpressumPostalCode -Path $ImpressumScrapePath
$lookupScript = Join-Path $PSScriptRoot "places_lookup.ps1"

$lookupResult = & $lookupScript `
    -StudioName $StudioName `
    -Stadt $Stadt `
    -Domain $Domain `
    -PLZ $plz `
    -AsJson | ConvertFrom-Json

$result = [PSCustomObject]@{
    INPUT_STUDIO             = $StudioName
    INPUT_STADT              = $Stadt
    INPUT_DOMAIN             = $Domain
    IMPRESSUM_SCRAPE_PATH    = $ImpressumScrapePath
    EXTRACTED_PLZ            = $plz
    PLACES_LOOKUP_RAW_RESULT = $lookupResult
}

if ($AsJson) {
    $result | ConvertTo-Json -Depth 8
} else {
    $result
}
