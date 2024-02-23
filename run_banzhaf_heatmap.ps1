$csvDirectory = ".\input_csvs_heatmap\"

$csvFiles = Get-ChildItem -Path $csvDirectory -Filter *.csv

$pythonScript = ".\heatmap_banzhaf.py"

foreach ($csvFile in $csvFiles) {
    $currentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$currentTime - Running Banzhaf heatmap script on $($csvFile.Name)"

    $csvFilePath = Join-Path -Path $csvDirectory -ChildPath $csvFile.Name
    $command = "python '$pythonScript' '$csvFilePath'"
    
    Invoke-Expression -Command $command
}
