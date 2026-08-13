$ErrorActionPreference = "Stop"

$RuntimeRoot = $PSScriptRoot
$PackageRoot = Split-Path -Parent $RuntimeRoot
$ProjectRoot = Join-Path $PackageRoot "CampusBot"
$PythonExe = Join-Path $RuntimeRoot "python\python.exe"
$TestRoot = Join-Path $ProjectRoot "tests"

if (-not (Test-Path $TestRoot)) {
    Write-Host "No tests folder exists yet: $TestRoot" -ForegroundColor Yellow
    Write-Host "Create CampusBot\tests and add test_*.py files, then run this command again."
    exit 0
}

Write-Host "Running CampusBot tests..."
Push-Location $ProjectRoot
try {
    & $PythonExe -m unittest discover -s tests -p "test_*.py" -v
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
