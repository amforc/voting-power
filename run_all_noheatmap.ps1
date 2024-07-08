param (
    [string]$network,
    [string]$lookback
)

$date = Get-Date -Format "yyyyMMdd"
Write-Host "Date: $date, Network: $network, Lookback: $lookback"

$commands = @(
    "python .\voting_from_subscan.py $network $lookback",
    "python .\prepare_data.py ${date}_${network}_${lookback}_days.csv",
    ".\run_banzhaf.ps1"
)

foreach ($command in $commands) {
    Write-Host "Executing: $command"
    Invoke-Expression $command
}
