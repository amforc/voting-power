$csvDirectory = ".\input_csvs\"

$csvFiles = Get-ChildItem -Path $csvDirectory -Filter *.csv

$pythonScript = ".\banzhaf.py"

foreach ($csvFile in $csvFiles) {
    $currentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$currentTime - Running Banzhaf script on $($csvFile.Name)"

    $csvFilePath = Join-Path -Path $csvDirectory -ChildPath $csvFile.Name
    $command = "python '$pythonScript' '$csvFilePath'"
    
    Invoke-Expression -Command $command
}
