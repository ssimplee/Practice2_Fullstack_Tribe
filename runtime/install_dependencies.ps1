$ErrorActionPreference = "Stop"

$RuntimeRoot = $PSScriptRoot
$PackageRoot = Split-Path -Parent $RuntimeRoot
$ProjectRoot = Join-Path $PackageRoot "CampusBot"
$PythonExe = Join-Path $RuntimeRoot "python\python.exe"
$WheelRoot = Join-Path $RuntimeRoot "wheels"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

if (-not (Test-Path $RequirementsFile)) {
    Write-Host "requirements.txt was not found: $RequirementsFile" -ForegroundColor Red
    exit 1
}

Write-Host "Installing dependencies from the bundled offline wheel folder..."
& $PythonExe -m pip install `
    --disable-pip-version-check `
    --no-index `
    --find-links $WheelRoot `
    --requirement $RequirementsFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "" 
    Write-Host "A required wheel is not bundled." -ForegroundColor Red
    Write-Host "Add a compatible Windows x64 Python 3.11 .whl file to runtime\wheels and try again."
    exit $LASTEXITCODE
}

Write-Host "Offline dependencies are ready."
