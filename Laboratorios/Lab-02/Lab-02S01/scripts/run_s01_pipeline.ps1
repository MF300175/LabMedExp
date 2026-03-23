[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [switch]$SkipFetch,
    [switch]$SkipCK
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Ensure-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Comando '$Name' não encontrado no PATH."
    }
}

function Get-EnvValue {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [AllowEmptyCollection()][AllowEmptyString()][string[]]$Lines = @()
    )

    $line = $Lines | Where-Object { $_ -match "^\s*$([regex]::Escape($Name))\s*=" } | Select-Object -First 1
    if (-not $line) {
        return ""
    }
    return (($line -split "=", 2)[1]).Trim()
}

function Set-EnvValue {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value,
        [AllowEmptyCollection()][AllowEmptyString()][string[]]$Lines = @()
    )

    $pattern = "^\s*$([regex]::Escape($Name))\s*="
    $newLine = "$Name=$Value"
    if ($Lines | Where-Object { $_ -match $pattern }) {
        return $Lines | ForEach-Object { if ($_ -match $pattern) { $newLine } else { $_ } }
    }
    return @($Lines + $newLine)
}

function Read-EnvLines {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path $Path)) {
        return @()
    }

    $raw = Get-Content $Path -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($null -eq $raw) {
        return @()
    }

    if ($raw -is [string]) {
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return @()
        }
        return @($raw)
    }

    return @($raw)
}

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    # scripts/ -> Lab-02S01/ -> Lab-02/ -> Laboratorios/ -> repo root
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
}

$s01Dir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$envFile = Join-Path $s01Dir ".env"
$envExample = Join-Path $s01Dir ".env.example"
$dataDir = Join-Path $s01Dir "data"
$logsDir = Join-Path $s01Dir "logs"
$logFile = Join-Path $logsDir "execution_s01.log"
$reposCsv = Join-Path $dataDir "repos_1000.csv"
$reposJson = Join-Path $dataDir "repos_1000.json"
$sampleCsv = Join-Path $dataDir "sample_metrics.csv"

Write-Step "Validando pré-requisitos"
Ensure-Command -Name "python"
Ensure-Command -Name "git"
Ensure-Command -Name "java"

Write-Step "Entrando em $s01Dir"
Set-Location $s01Dir

$venvActivate = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Step "Ativando ambiente virtual"
    & $venvActivate
}

Write-Step "Instalando dependências Python"
python -m pip install -r .\requirements.txt

Write-Step "Preparando diretórios"
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

Write-Step "Preparando arquivo .env"
if (-not (Test-Path $envFile)) {
    if (-not (Test-Path $envExample)) {
        throw "Arquivo .env.example não encontrado em $envExample"
    }
    Copy-Item $envExample $envFile -Force
}

$envLines = Read-EnvLines -Path $envFile

$token = Get-EnvValue -Name "GITHUB_TOKEN" -Lines $envLines
if ([string]::IsNullOrWhiteSpace($token)) {
    $secureToken = Read-Host "Informe GITHUB_TOKEN" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    try {
        $token = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "GITHUB_TOKEN não informado."
    }
    $envLines = Set-EnvValue -Name "GITHUB_TOKEN" -Value $token -Lines $envLines
}

$ckJar = Get-EnvValue -Name "CK_JAR_PATH" -Lines $envLines
if (-not $SkipCK) {
    if ([string]::IsNullOrWhiteSpace($ckJar) -or -not (Test-Path $ckJar)) {
        $ckJar = Read-Host "Informe CK_JAR_PATH (arquivo .jar completo)"
        if ([string]::IsNullOrWhiteSpace($ckJar)) {
            throw "CK_JAR_PATH não informado."
        }
        if (-not (Test-Path $ckJar)) {
            throw "CK_JAR_PATH inválido: $ckJar"
        }
        $envLines = Set-EnvValue -Name "CK_JAR_PATH" -Value $ckJar -Lines $envLines
    }
}

# Configuração estável padrão
$envLines = Set-EnvValue -Name "LAB02_TARGET_REPOS" -Value "1000" -Lines $envLines
$envLines = Set-EnvValue -Name "LAB02_PAGE_SIZE" -Value "20" -Lines $envLines
$envLines = Set-EnvValue -Name "LAB02_TIMEOUT_SECS" -Value "90" -Lines $envLines
$envLines = Set-EnvValue -Name "LAB02_MAX_RETRIES" -Value "20" -Lines $envLines

$envLines | Set-Content -Path $envFile -Encoding UTF8

Write-Step "Carregando variáveis do .env para a sessão"
Get-Content $envFile -Encoding UTF8 | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') {
        return
    }
    $k, $v = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), "Process")
}

if (-not $SkipFetch) {
    Write-Step "Executando coleta dos 1000 repositórios"
    python .\fetch_repos.py
}

Write-Step "Validando saídas da coleta"
if (-not (Test-Path $reposCsv)) {
    throw "Arquivo não encontrado: $reposCsv"
}
if (-not (Test-Path $reposJson)) {
    throw "Arquivo não encontrado: $reposJson"
}

$rows = (Import-Csv $reposCsv).Count
Write-Host "Repos no CSV: $rows" -ForegroundColor Yellow
if ($rows -lt 1000) {
    throw "CSV com menos de 1000 repositórios: $rows"
}

if (-not $SkipCK) {
    Write-Step "Executando CK em 1 repositório (com log)"
    python .\collect_sample_metrics.py 2>&1 | Tee-Object -FilePath $logFile

    if (-not (Test-Path $sampleCsv)) {
        throw "Arquivo não encontrado: $sampleCsv"
    }
}

Write-Step "Concluído"
Write-Host "Saídas principais:" -ForegroundColor Green
Write-Host "- $reposJson"
Write-Host "- $reposCsv"
if (-not $SkipCK) {
    Write-Host "- $sampleCsv"
    Write-Host "- $logFile"
}
