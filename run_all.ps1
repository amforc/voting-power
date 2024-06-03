param (
    [string]$network
)

$date = Get-Date -Format "yyyyMMdd"
Write-Host "Date: $date"

$commands = @(
    "python .\voting_from_subscan.py $network 90",
    "python .\prepare_data.py ${date}_${network}_90_days.csv",
    ".\run_banzhaf.ps1",
    "python .\heatmap_prepare_data.py ${date}_${network}_90_days.csv",
    ".\run_banzhaf_heatmap.ps1",
    ".\run_banzhaf_heatmap_plots.ps1"
)

foreach ($command in $commands) {
    Write-Host "Executing: $command"
    Invoke-Expression $command
}
