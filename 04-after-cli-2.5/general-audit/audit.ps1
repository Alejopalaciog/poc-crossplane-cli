<#
.SYNOPSIS
  Auditoría offline de las composiciones generales que usa la plataforma:
  render anidado (XR hijo -> composición general) + validate contra los
  esquemas reales de los providers. No usa cluster ni AWS.
#>
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot
$xp      = (Resolve-Path ..\..\tools\crossplane-2.5.0.exe).Path
$general = (Resolve-Path ..\..\..\local-argocd-crossplane-config\platform\aws_xrds).Path
$fns     = (Resolve-Path ..\..\03-before-2-cli-2.2\functions.yaml).Path
$measure = (Resolve-Path ..\..\05-measurements\measure.ps1).Path

$targets = @{ xiam = 'iam'; xkms = 'kms'; xcloudwatch = 'cloudwatch'; xlambda = 'lambda' }
foreach ($k in $targets.Keys) {
    $comp = Join-Path $general "$($targets[$k])\composition.yaml"
    & $measure -Scenario after -Step "audit-render-$k" -WorkDir $PSScriptRoot `
        -Command "`"$xp`" composition render xr-$k.yaml `"$comp`" `"$fns`" > render-$k.yaml" `
        -Note "render anidado composicion general $($targets[$k])" | Select-Object -Last 1
}

Get-Content render-*.yaml | Set-Content -Encoding utf8 render-all.yaml
& $measure -Scenario after -Step audit-validate -WorkDir $PSScriptRoot `
    -Command "`"$xp`" resource validate providers.yaml render-all.yaml" `
    -Note "validate MRs de composiciones generales contra CRDs de providers v2.5.0"
