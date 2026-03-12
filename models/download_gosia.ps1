param(
    [string]$OutDir = "."
)

$ErrorActionPreference = "Stop"

$resolvedOutDir = Resolve-Path $OutDir -ErrorAction SilentlyContinue
if (-not $resolvedOutDir) {
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
    $resolvedOutDir = Resolve-Path $OutDir
}

$onnxUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx"
$jsonUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json"

$onnxPath = Join-Path $resolvedOutDir "pl_PL-gosia-medium.onnx"
$jsonPath = Join-Path $resolvedOutDir "pl_PL-gosia-medium.onnx.json"

Write-Host "Downloading model to: $resolvedOutDir"
Write-Host "1/2 -> $onnxPath"
Invoke-WebRequest -Uri $onnxUrl -OutFile $onnxPath

Write-Host "2/2 -> $jsonPath"
Invoke-WebRequest -Uri $jsonUrl -OutFile $jsonPath

Write-Host "Done."
Write-Host "Files:"
Get-ChildItem $resolvedOutDir | Where-Object { $_.Name -like "pl_PL-gosia-medium.onnx*" } | Select-Object Name, Length
