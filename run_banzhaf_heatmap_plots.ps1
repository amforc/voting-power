$csvDirectory = ".\banzhaf_heatmap\"

$csvFiles = Get-ChildItem -Path $csvDirectory -Filter *.csv

$pythonScript = ".\heatmapplot.py"

foreach ($csvFile in $csvFiles) {
    $currentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$currentTime - Running Banzhaf heatmap plot script on $($csvFile.Name)"

    $csvFilePath = Join-Path -Path $csvDirectory -ChildPath $csvFile.Name
    $command = "python '$pythonScript' '$csvFilePath'"
    
    Invoke-Expression -Command $command
}
