param(
    [string]$PythonBin = ".venv\Scripts\python.exe",
    [string]$AllureResultsDir = "allure\results",
    [bool]$OpenAllure = $true
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

if (-not (Test-Path $PythonBin)) {
    Write-Host "Python do projeto nao encontrado em: $PythonBin"
    Write-Host "Crie o virtualenv e instale as dependencias:"
    Write-Host "  py -3.12 -m venv .venv"
    Write-Host "  .\.venv\Scripts\Activate.ps1"
    Write-Host "  pip install -r requirements.txt"
    exit 1
}

New-Item -ItemType Directory -Force -Path $AllureResultsDir | Out-Null

& $PythonBin -m pytest tests -v "--alluredir=$AllureResultsDir" --clean-alluredir

if ($OpenAllure) {
    $AllureCommand = Get-Command allure -ErrorAction SilentlyContinue
    if (-not $AllureCommand) {
        Write-Host "Testes executados, mas o comando 'allure' nao foi encontrado no PATH."
        Write-Host "Instale o Allure CLI para abrir o relatorio com:"
        Write-Host "  allure serve $AllureResultsDir"
        exit 1
    }

    allure serve $AllureResultsDir
}
else {
    Write-Host "Relatorio Allure gerado em: $AllureResultsDir"
}
