<#
.SYNOPSIS
  Reproduce en pantalla las salidas clave de la PoC para tomar pantallazos (evidencia wiki).
  Uso:  powershell -File 06-evidence\replay.ps1 -Paso 1
#>
param([Parameter(Mandatory)] [ValidateRange(1, 4)] [int] $Paso)

Set-Location (Split-Path $PSScriptRoot -Parent)
$xp  = (Resolve-Path tools\crossplane-2.5.0.exe).Path
$old = (Resolve-Path tools\crank-2.2.6.exe).Path
$la  = '..\local-argocd-crossplane-config'
function Title($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }

switch ($Paso) {
    1 {
        Title 'E1 · CLI 2.2.6 (antes) y 2.5.0 (después) contra el core v2.3.3 del cluster'
        & $old version
        & $xp version
    }
    2 {
        Title 'E2 · Lo que se vio en el cluster en la 1.ª corrida (2,4 min, ~5.200 tokens de eventos)'
        Select-String -Path 05-measurements\runs\before-1\observe-cluster-01.log `
            -Pattern 'permissionsBoundary|field not declared|not authorized' | Select-Object -First 4 |
            ForEach-Object { $_.Line.Substring(0, [Math]::Min(220, $_.Line.Length)) }
    }
    3 {
        Title 'E3 · CLI 2.5 detecta offline los 2 bugs de composiciones generales (sin cluster ni AWS)'
        & $xp resource validate 04-after-cli-2.5\general-audit\providers.yaml 04-after-cli-2.5\general-audit\render-all.yaml
        Title 'render anidado de aws-iam-role'
        Select-String -Path 04-after-cli-2.5\general-audit\render-xiam.yaml -Pattern 'no value'
    }
    4 {
        Title 'E4 · Adopción: claim real adopt-kms-test verificado offline'
        & $xp composition render "$la\claims\adopt-kms-test\claim.yaml" "$la\platform\aws_xrds\kms\composition.yaml" 03-before-2-cli-2.2\functions.yaml -x |
            .venv\Scripts\python 05-measurements\adoption_checks.py -
        Title 'E4b · Mismo claim sin managementPolicies (error típico al editar): crearía en vez de adoptar'
        & $xp composition render 04-after-cli-2.5\adoption-demo\claim-sin-policies.yaml "$la\platform\aws_xrds\kms\composition.yaml" 03-before-2-cli-2.2\functions.yaml -x |
            .venv\Scripts\python 05-measurements\adoption_checks.py -
    }
}
