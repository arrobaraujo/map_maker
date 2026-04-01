param(
	[switch]$Clean
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
	throw "Virtual environment not found at .venv. Create it first with: python -m venv .venv"
}

if ($Clean) {
	if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
	if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m PyInstaller app.spec

Write-Host "Build complete. Check dist\app.exe"
