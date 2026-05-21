param(
    [Parameter(Mandatory = $true)]
    [string]$StudioName,

    [Parameter(Mandatory = $true)]
    [string]$Stadt,

    [Parameter(Mandatory = $true)]
    [string]$Domain,

    [Parameter(Mandatory = $false)]
    [string]$Plz = "",

    [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ConfigPath = Join-Path $PSScriptRoot "config.ps1"

function New-GbpResult {
    param(
        [string]$PlaceId = "",
        [string]$MatchScore = "",
        [string]$Status = "",
        [string]$Rating = "",
        [string]$Reviews = "",
        [string]$Category = "",
        [string]$NapMatch = "",
        [string]$HoursSet = "",
        [string]$MapsUrl = "",
        [string]$Message = ""
    )

    [PSCustomObject]@{
        GBP_PLACE_ID     = $PlaceId
        GBP_MATCH_SCORE  = $MatchScore
        GBP_STATUS       = $Status
        GBP_RATING       = $Rating
        GBP_REVIEWS      = $Reviews
        GBP_CATEGORY     = $Category
        GBP_NAP_MATCH    = $NapMatch
        GBP_HOURS_SET    = $HoursSet
        GBP_MAPS_URL     = $MapsUrl
        MESSAGE          = $Message
    }
}

function Get-NormalizedHost {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ""
    }

    $candidate = $Value.Trim()
    if ($candidate -notmatch "^[a-zA-Z][a-zA-Z0-9+.-]*://") {
        $candidate = "https://$candidate"
    }

    try {
        $uri = [System.Uri]$candidate
        return ($uri.Host -replace "^www\.", "").ToLowerInvariant()
    } catch {
        return ($Value.Trim() -replace "^https?://", "" -replace "^www\.", "" -replace "/.*$", "").ToLowerInvariant()
    }
}

function Get-ObjectValue {
    param(
        [object]$Object,
        [string]$PropertyName,
        [object]$Default = ""
    )

    if ($null -eq $Object) {
        return $Default
    }

    $property = $Object.PSObject.Properties[$PropertyName]
    if ($null -eq $property -or $null -eq $property.Value) {
        return $Default
    }

    return $property.Value
}

function Get-AddressPostalCode {
    param([string]$Address)

    if ([string]::IsNullOrWhiteSpace($Address)) {
        return ""
    }

    $match = [regex]::Match($Address, "\b\d{5}\b")
    if ($match.Success) {
        return $match.Value
    }

    return ""
}

function Get-NameTokenOverlapPercent {
    param(
        [string]$InputName,
        [string]$PlaceName
    )

    $inputTokens = @($InputName.ToLowerInvariant() -split "[^\p{L}\p{Nd}]+" | Where-Object { $_.Length -ge 3 })
    $placeTokens = @($PlaceName.ToLowerInvariant() -split "[^\p{L}\p{Nd}]+" | Where-Object { $_.Length -ge 3 })

    if ($inputTokens.Count -eq 0) {
        return 0
    }

    $placeSet = @{}
    foreach ($token in $placeTokens) {
        $placeSet[$token] = $true
    }

    $overlap = 0
    foreach ($token in $inputTokens) {
        if ($placeSet.ContainsKey($token)) {
            $overlap++
        }
    }

    return [math]::Round(($overlap / $inputTokens.Count) * 100, 2)
}

function Test-AllowedType {
    param($Types)

    $allowedTypes = @("beauty_salon", "spa", "hair_care", "health")
    foreach ($type in @($Types)) {
        if ($allowedTypes -contains $type) {
            return $true
        }
    }

    return $false
}

function Get-PrimaryCategory {
    param($Types)

    $preferredTypes = @("beauty_salon", "spa", "hair_care", "health")
    foreach ($type in $preferredTypes) {
        if (@($Types) -contains $type) {
            return $type
        }
    }

    $allTypes = @($Types)
    if ($allTypes.Count -gt 0) {
        return [string]$allTypes[0]
    }

    return ""
}

function Get-MatchScore {
    param(
        [object]$Place,
        [string]$InputName,
        [string]$InputPlz,
        [string]$InputDomain
    )

    $score = 0
    $inputHost = Get-NormalizedHost -Value $InputDomain
    $placeHost = Get-NormalizedHost -Value (Get-ObjectValue -Object $Place -PropertyName "website")
    $placePlz = Get-AddressPostalCode -Address (Get-ObjectValue -Object $Place -PropertyName "formatted_address")
    $tokenOverlap = Get-NameTokenOverlapPercent -InputName $InputName -PlaceName (Get-ObjectValue -Object $Place -PropertyName "name")

    if ($placePlz -and $InputPlz -and $placePlz -eq $InputPlz.Trim()) {
        $score += 3
    }

    if ($placeHost -and $inputHost -and $placeHost -eq $inputHost) {
        $score += 3
    }

    if (Test-AllowedType -Types (Get-ObjectValue -Object $Place -PropertyName "types" -Default @())) {
        $score += 2
    }

    if ($tokenOverlap -gt 60) {
        $score += 1
    }

    return $score
}

function Get-NapMatchStatus {
    param(
        [object]$Place,
        [string]$InputPlz,
        [string]$InputDomain
    )

    $inputHost = Get-NormalizedHost -Value $InputDomain
    $placeHost = Get-NormalizedHost -Value (Get-ObjectValue -Object $Place -PropertyName "website")
    $placePlz = Get-AddressPostalCode -Address (Get-ObjectValue -Object $Place -PropertyName "formatted_address")

    $plzMatches = ($placePlz -and $InputPlz -and $placePlz -eq $InputPlz.Trim())
    $hostMatches = ($placeHost -and $inputHost -and $placeHost -eq $inputHost)
    $plzConflict = ($placePlz -and $InputPlz -and $placePlz -ne $InputPlz.Trim())
    $hostConflict = ($placeHost -and $inputHost -and $placeHost -ne $inputHost)

    if ($plzMatches -and $hostMatches) {
        return "ja"
    }

    if ($plzConflict -or $hostConflict) {
        return "konflikt"
    }

    return "nein"
}

function Invoke-PlacesGet {
    param([string]$Url)

    try {
        return Invoke-RestMethod -Method Get -Uri $Url -TimeoutSec 30
    } catch {
        throw "Places API request failed: $($_.Exception.Message)"
    }
}

function Resolve-GoogleBusinessProfile {
    param(
        [string]$InputStudioName,
        [string]$InputStadt,
        [string]$InputPlz,
        [string]$InputDomain
    )

    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        return New-GbpResult -Status "API_ERROR" -Message "tools/config.ps1 nicht gefunden."
    }

    . $ConfigPath

    if ([string]::IsNullOrWhiteSpace($GOOGLE_PLACES_API_KEY)) {
        return New-GbpResult -Status "API_ERROR" -Message "`$GOOGLE_PLACES_API_KEY ist nicht gesetzt."
    }

    try {
        $query = "$InputStudioName $InputStadt"
        $encodedQuery = [System.Uri]::EscapeDataString($query)
        $findFields = [System.Uri]::EscapeDataString("place_id,name,formatted_address,types")
        $findUrl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=$encodedQuery&inputtype=textquery&fields=$findFields&key=$GOOGLE_PLACES_API_KEY"
        $findResponse = Invoke-PlacesGet -Url $findUrl

        if ($findResponse.status -ne "OK") {
            if ($findResponse.status -eq "ZERO_RESULTS") {
                return New-GbpResult -Status "NOT_FOUND" -Message "GBP nicht eindeutig gefunden"
            }

            return New-GbpResult -Status "API_ERROR" -Message "Find Place status: $($findResponse.status)"
        }

        $candidates = @($findResponse.candidates)
        if ($candidates.Count -eq 0 -or [string]::IsNullOrWhiteSpace($candidates[0].place_id)) {
            return New-GbpResult -Status "NOT_FOUND" -Message "GBP nicht eindeutig gefunden"
        }

        $placeId = $candidates[0].place_id
        $encodedPlaceId = [System.Uri]::EscapeDataString($placeId)
        $detailsFields = [System.Uri]::EscapeDataString("place_id,name,formatted_address,website,types,rating,user_ratings_total,business_status,opening_hours,url")
        $detailsUrl = "https://maps.googleapis.com/maps/api/place/details/json?place_id=$encodedPlaceId&fields=$detailsFields&key=$GOOGLE_PLACES_API_KEY"
        $detailsResponse = Invoke-PlacesGet -Url $detailsUrl

        if ($detailsResponse.status -ne "OK") {
            return New-GbpResult -PlaceId $placeId -Status "API_ERROR" -Message "Place Details status: $($detailsResponse.status)"
        }

        $place = $detailsResponse.result
        $score = Get-MatchScore -Place $place -InputName $InputStudioName -InputPlz $InputPlz -InputDomain $InputDomain

        if ($score -lt 4) {
            return New-GbpResult `
                -PlaceId (Get-ObjectValue -Object $place -PropertyName "place_id") `
                -MatchScore ([string]$score) `
                -Status "NOT_FOUND" `
                -MapsUrl (Get-ObjectValue -Object $place -PropertyName "url") `
                -Message "GBP nicht eindeutig gefunden"
        }

        if ($score -lt 6) {
            return New-GbpResult `
                -PlaceId (Get-ObjectValue -Object $place -PropertyName "place_id") `
                -MatchScore ([string]$score) `
                -Status "NEEDS_REVIEW" `
                -MapsUrl (Get-ObjectValue -Object $place -PropertyName "url") `
                -Message "needs-review"
        }

        $hoursSet = "nein"
        if (Get-ObjectValue -Object $place -PropertyName "opening_hours" -Default $null) {
            $hoursSet = "ja"
        }

        return New-GbpResult `
            -PlaceId (Get-ObjectValue -Object $place -PropertyName "place_id") `
            -MatchScore ([string]$score) `
            -Status (Get-ObjectValue -Object $place -PropertyName "business_status") `
            -Rating ([string](Get-ObjectValue -Object $place -PropertyName "rating")) `
            -Reviews ([string](Get-ObjectValue -Object $place -PropertyName "user_ratings_total")) `
            -Category (Get-PrimaryCategory -Types (Get-ObjectValue -Object $place -PropertyName "types" -Default @())) `
            -NapMatch (Get-NapMatchStatus -Place $place -InputPlz $InputPlz -InputDomain $InputDomain) `
            -HoursSet $hoursSet `
            -MapsUrl (Get-ObjectValue -Object $place -PropertyName "url")
    } catch {
        return New-GbpResult -Status "API_ERROR" -Message $_.Exception.Message
    }
}

$result = Resolve-GoogleBusinessProfile `
    -InputStudioName $StudioName `
    -InputStadt $Stadt `
    -InputPlz $Plz `
    -InputDomain $Domain

if ($AsJson) {
    $result | ConvertTo-Json -Depth 4
} else {
    $result
}
