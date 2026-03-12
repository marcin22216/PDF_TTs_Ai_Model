param(
    [string]$OutDir = ".",
    [string]$Preset = ""
)

$ErrorActionPreference = "Stop"
$OutDir = $OutDir.Trim().Trim('"')

$resolvedOutDir = Resolve-Path $OutDir -ErrorAction SilentlyContinue
if (-not $resolvedOutDir) {
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
    $resolvedOutDir = Resolve-Path $OutDir
}

$voiceMap = @{
    "1" = @{
        Label = "Polski - Gosia (female, medium)"
        BaseUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx"
        FilePrefix = "pl_PL-gosia-medium"
    }
    "2" = @{
        Label = "English - Amy (female, medium)"
        BaseUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
        FilePrefix = "en_US-amy-medium"
    }
    "3" = @{
        Label = "English - Joe (male, medium)"
        BaseUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/en_US-joe-medium.onnx"
        FilePrefix = "en_US-joe-medium"
    }
    "4" = @{
        Label = "Deutsch - Eva K (female, medium)"
        BaseUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/medium/de_DE-eva_k-medium.onnx"
        FilePrefix = "de_DE-eva_k-medium"
    }
    "5" = @{
        Label = "Deutsch - Thorsten (male, medium)"
        BaseUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx"
        FilePrefix = "de_DE-thorsten-medium"
    }
}

function Select-Preset {
    param([string]$Provided)

    if ($Provided -and $voiceMap.ContainsKey($Provided)) {
        return $Provided
    }

    Write-Host "Select voice model to download:"
    Write-Host "  1) $($voiceMap['1'].Label)"
    Write-Host "  2) $($voiceMap['2'].Label)"
    Write-Host "  3) $($voiceMap['3'].Label)"
    Write-Host "  4) $($voiceMap['4'].Label)"
    Write-Host "  5) $($voiceMap['5'].Label)"
    $choice = Read-Host "Enter option number (1-5)"
    if (-not $voiceMap.ContainsKey($choice)) {
        throw "Invalid selection: $choice"
    }
    return $choice
}

$selectedKey = Select-Preset -Provided $Preset
$selected = $voiceMap[$selectedKey]
$onnxUrl = $selected.BaseUrl
$jsonUrl = "$($selected.BaseUrl).json"
$onnxPath = Join-Path $resolvedOutDir "$($selected.FilePrefix).onnx"
$jsonPath = Join-Path $resolvedOutDir "$($selected.FilePrefix).onnx.json"

Write-Host "Downloading: $($selected.Label)"
Write-Host "Target dir: $resolvedOutDir"
Write-Host "1/2 -> $onnxPath"
Invoke-WebRequest -Uri $onnxUrl -OutFile $onnxPath

Write-Host "2/2 -> $jsonPath"
Invoke-WebRequest -Uri $jsonUrl -OutFile $jsonPath

Write-Host "Done."
Write-Host "Downloaded files:"
Get-ChildItem $resolvedOutDir | Where-Object { $_.Name -like "$($selected.FilePrefix).onnx*" } | Select-Object Name, Length
