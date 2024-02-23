$csv1Directory = ".\error_checks\by10_13"
$csv2Directory = ".\error_checks\by10_14"

$csvFiles = Get-ChildItem -Path $csv1Directory -Filter *.csv

$pythonScript = ".\calculate_scaling_deviations.py"

foreach ($csvFile in $csvFiles) {
    $currentTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$currentTime - Running comparison script on $($csvFile.Name)"

    $csv1FilePath = Join-Path -Path $csv1Directory -ChildPath $csvFile.Name
    $csv2FilePath = Join-Path -Path $csv2Directory -ChildPath $csvFile.Name
    $command = "python '$pythonScript' '$csv1FilePath' '$csv2FilePath'"
    
    Invoke-Expression -Command $command
}
