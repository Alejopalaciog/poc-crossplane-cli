<#
.SYNOPSIS
  Ejecuta un comando, lo cronometra y registra el resultado en results.csv.

.DESCRIPTION
  Cada ejecución guarda la salida completa (stdout+stderr) en runs/<escenario>/
  y agrega una fila a results.csv con: escenario, paso, iteración, duración,
  código de salida, tamaño de la salida y tokens estimados (chars/4).
  Los tokens estimados de la salida alimentan el cálculo de créditos AI:
  es el feedback que el agente tendría que leer en esa iteración.

.EXAMPLE
  ./measure.ps1 -Scenario after -Step render -Command "crossplane composition render xr.yaml comp.yaml"
#>
param(
    [Parameter(Mandatory)] [ValidateSet('before-1', 'before-2', 'after', 'setup', 'deploy', 'defects')] [string] $Scenario,
    [Parameter(Mandatory)] [string] $Step,
    [Parameter(Mandatory)] [string] $Command,
    [string] $Note = '',
    [string] $WorkDir = (Get-Location).Path
)

$root    = $PSScriptRoot
$csv     = Join-Path $root 'results.csv'
$runDir  = Join-Path $root "runs/$Scenario"
New-Item -ItemType Directory -Force $runDir | Out-Null

if (-not (Test-Path $csv)) {
    'timestamp,scenario,step,iteration,duration_s,exit_code,output_chars,output_tokens_est,note' | Out-File -Encoding utf8 $csv
}

# Iteración = cuántas veces se ha corrido este paso en este escenario.
$iteration = 1 + @(Import-Csv $csv | Where-Object { $_.scenario -eq $Scenario -and $_.step -eq $Step }).Count
$safeStep  = $Step -replace '[^\w\-]', '_'
$logFile   = Join-Path $runDir ('{0}-{1:D2}.log' -f $safeStep, $iteration)

$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$start = Get-Date
$sw    = [Diagnostics.Stopwatch]::StartNew()
Push-Location $WorkDir
try {
    $output   = & cmd /c "$Command 2>&1"
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
$sw.Stop()

$text = ($output | Out-String)
"# $Command`n# start=$($start.ToString('o')) duration=$([math]::Round($sw.Elapsed.TotalSeconds,2))s exit=$exitCode`n$text" |
    Out-File -Encoding utf8 $logFile

$chars  = $text.Length
$tokens = [math]::Ceiling($chars / 4)
$row = '{0},{1},{2},{3},{4},{5},{6},{7},"{8}"' -f $start.ToString('o'), $Scenario, $Step, $iteration,
    [math]::Round($sw.Elapsed.TotalSeconds, 2), $exitCode, $chars, $tokens, ($Note -replace '"', "'")
$row | Out-File -Append -Encoding utf8 $csv

Write-Host $text
Write-Host ("[measure] {0}/{1} #{2}: {3:N2}s exit={4} ~{5} tokens -> {6}" -f $Scenario, $Step, $iteration, $sw.Elapsed.TotalSeconds, $exitCode, $tokens, $logFile)
exit $exitCode
