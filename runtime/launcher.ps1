param(
    [switch]$StopOnly
)

$ErrorActionPreference = "Stop"

$RuntimeRoot = $PSScriptRoot
$PackageRoot = Split-Path -Parent $RuntimeRoot
$ProjectRoot = Join-Path $PackageRoot "CampusBot"
$PythonExe = Join-Path $RuntimeRoot "python\python.exe"
$OllamaExe = Join-Path $RuntimeRoot "ollama\ollama.exe"
$ModelRoot = Join-Path $PackageRoot "models"
$StateRoot = Join-Path $env:LOCALAPPDATA "CampusBot Offline"
$LogRoot = Join-Path $StateRoot "logs"
$HomeRoot = Join-Path $StateRoot "home"
$PidRoot = Join-Path $StateRoot "pids"
$OllamaPort = 11435
$CampusBotPort = 8000
$OllamaBaseUrl = "http://127.0.0.1:$OllamaPort"
$CampusBotUrl = "http://127.0.0.1:$CampusBotPort"

$ServeEntry = Join-Path $ProjectRoot "serve.py"
$MainEntry = Join-Path $ProjectRoot "main.py"
if (Test-Path $ServeEntry) {
    $ApplicationEntry = $ServeEntry
}
elseif (Test-Path $MainEntry) {
    $ApplicationEntry = $MainEntry
}
else {
    Write-Host "CampusBot could not start: main.py or serve.py was not found in $ProjectRoot" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

New-Item -ItemType Directory -Force -Path $LogRoot, $HomeRoot, $PidRoot | Out-Null

function Stop-OwnedProcess {
    param(
        [string]$PidFile,
        [string]$ExpectedExecutable
    )
    if (-not (Test-Path $PidFile)) {
        return
    }

    $OwnedId = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($OwnedId) {
        $OwnedProcess = Get-Process -Id $OwnedId -ErrorAction SilentlyContinue
        if ($OwnedProcess -and $OwnedProcess.Path -eq $ExpectedExecutable) {
            $ChildProcesses = Get-CimInstance Win32_Process -Filter "ParentProcessId = $OwnedId" -ErrorAction SilentlyContinue
            foreach ($ChildProcess in $ChildProcesses) {
                Stop-Process -Id $ChildProcess.ProcessId -Force -ErrorAction SilentlyContinue
            }
            Stop-Process -Id $OwnedId -Force -ErrorAction SilentlyContinue
        }
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

function Stop-CampusBotServices {
    Stop-OwnedProcess (Join-Path $PidRoot "campusbot.pid") $PythonExe
    Stop-OwnedProcess (Join-Path $PidRoot "ollama.pid") $OllamaExe
}

function Test-LocalPort {
    param([int]$Port)
    $Client = New-Object System.Net.Sockets.TcpClient
    try {
        $Connection = $Client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $Connection.AsyncWaitHandle.WaitOne(300)) {
            return $false
        }
        $Client.EndConnect($Connection)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $Client.Close()
    }
}

function Wait-ForUrl {
    param(
        [string]$Url,
        [int]$Attempts = 90
    )
    for ($Attempt = 1; $Attempt -le $Attempts; $Attempt++) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2 | Out-Null
            return $true
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

if ($StopOnly) {
    Stop-CampusBotServices
    Write-Host "CampusBot has been stopped."
    exit 0
}

Write-Host "Starting CampusBot Offline..."
Write-Host "The first model response may take a little longer."
Write-Host ""

try {
    Stop-CampusBotServices

    if (Test-LocalPort $OllamaPort) {
        throw "Port $OllamaPort is already in use. Close the conflicting program and try again."
    }
    if (Test-LocalPort $CampusBotPort) {
        throw "Port $CampusBotPort is already in use. Close the conflicting program and try again."
    }

    $env:HOME = $HomeRoot
    $env:USERPROFILE = $HomeRoot
    $env:OLLAMA_HOST = "127.0.0.1:$OllamaPort"
    $env:OLLAMA_MODELS = $ModelRoot
    $env:OLLAMA_NO_CLOUD = "1"
    $env:OLLAMA_KEEP_ALIVE = "5m"

    $OllamaProcess = Start-Process `
        -FilePath $OllamaExe `
        -ArgumentList "serve" `
        -WorkingDirectory (Split-Path -Parent $OllamaExe) `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogRoot "ollama-output.log") `
        -RedirectStandardError (Join-Path $LogRoot "ollama-error.log") `
        -PassThru
    Set-Content -Path (Join-Path $PidRoot "ollama.pid") -Value $OllamaProcess.Id

    if (-not (Wait-ForUrl "$OllamaBaseUrl/api/tags")) {
        throw "The bundled Ollama service did not start. Logs: $LogRoot"
    }

    $ModelList = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -TimeoutSec 5
    if (-not ($ModelList.models | Where-Object { $_.name -eq "qwen3:0.6b" })) {
        throw "The bundled qwen3:0.6b model was not found."
    }

    $env:OLLAMA_URL = "$OllamaBaseUrl/api/chat"
    $env:OLLAMA_MODEL = "qwen3:0.6b"

    $CampusBotProcess = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList @("`"$ApplicationEntry`"") `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogRoot "campusbot-output.log") `
        -RedirectStandardError (Join-Path $LogRoot "campusbot-error.log") `
        -PassThru
    Set-Content -Path (Join-Path $PidRoot "campusbot.pid") -Value $CampusBotProcess.Id

    if (-not (Wait-ForUrl "$CampusBotUrl/health")) {
        throw "The CampusBot service did not start. Logs: $LogRoot"
    }

    Start-Process "$CampusBotUrl/"
    Write-Host "CampusBot is ready: $CampusBotUrl/"
    Write-Host ""
    Write-Host "Keep this window open while using CampusBot."
    Read-Host "Press Enter here when finished to stop CampusBot"
}
catch {
    Write-Host ""
    Write-Host "CampusBot could not start:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "Logs: $LogRoot"
    Read-Host "Press Enter to close"
    exit 1
}
finally {
    Stop-CampusBotServices
}
