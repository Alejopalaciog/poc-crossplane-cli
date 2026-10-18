<#
.SYNOPSIS
  Ciclo de validación "en cluster" (lo que se hace hoy sin CLI): espera a que el XR
  quede Ready o falle, y vuelca el feedback que una persona/AI tendría que leer.

.DESCRIPTION
  Hace polling del XR raíz y de todo su árbol (XRs hijos y managed resources,
  siguiendo la label crossplane.io/composite). Termina cuando:
    - el XR está Ready=True                       → exit 0
    - algún recurso del árbol reporta Synced=False → exit 2
    - se agota el timeout                         → exit 3
  Al terminar imprime condiciones y eventos de los recursos no listos.
#>
param(
    [Parameter(Mandatory)] [string] $Kind,
    [Parameter(Mandatory)] [string] $Name,
    [int] $TimeoutSec = 900,
    [int] $IntervalSec = 15
)

function Get-Tree {
    $all = (kubectl get managed,composite -A -o json 2>$null | ConvertFrom-Json).items
    $names = [System.Collections.Generic.HashSet[string]]::new()
    [void]$names.Add($Name)
    do {
        $before = $names.Count
        foreach ($i in $all) {
            if ($names.Contains([string]$i.metadata.labels.'crossplane.io/composite')) { [void]$names.Add($i.metadata.name) }
        }
    } while ($names.Count -gt $before)
    $all | Where-Object { $names.Contains($_.metadata.name) }
}

function Get-Cond($item, $type) { ($item.status.conditions | Where-Object type -eq $type).status }

$deadline = (Get-Date).AddSeconds($TimeoutSec)
$exit = 3
while ((Get-Date) -lt $deadline) {
    $tree = @(Get-Tree)
    $root = $tree | Where-Object { $_.metadata.name -eq $Name }
    $notReady = @($tree | Where-Object { (Get-Cond $_ 'Ready') -ne 'True' })
    Write-Host ("[{0:HH:mm:ss}] XR Ready={1}  recursos={2}  no-listos={3}" -f (Get-Date), (Get-Cond $root 'Ready'), $tree.Count, $notReady.Count)
    if ((Get-Cond $root 'Ready') -eq 'True') { $exit = 0; break }
    if ($tree | Where-Object { (Get-Cond $_ 'Synced') -eq 'False' }) { $exit = 2; break }
    Start-Sleep -Seconds $IntervalSec
}

Write-Host "`n===== Estado final ====="
$tree = @(Get-Tree)
$tree | ForEach-Object {
    '{0,-28} {1,-70} synced={2,-6} ready={3}' -f $_.kind, $_.metadata.name, (Get-Cond $_ 'Synced'), (Get-Cond $_ 'Ready')
}
Write-Host "`n===== Feedback (recursos no listos) ====="
$tree | Where-Object { (Get-Cond $_ 'Ready') -ne 'True' } | ForEach-Object {
    $ns  = if ($_.metadata.namespace) { @('-n', $_.metadata.namespace) } else { @() }
    $res = '{0}.{1}/{2}' -f $_.kind.ToLower(), ($_.apiVersion -split '/')[0], $_.metadata.name
    Write-Host "--- $res"
    $_.status.conditions | ForEach-Object { '  {0}={1} {2}: {3}' -f $_.type, $_.status, $_.reason, $_.message }
    kubectl get events @ns --field-selector "involvedObject.name=$($_.metadata.name)" --sort-by=.lastTimestamp 2>$null |
        Select-Object -Last 5
}
exit $exit
