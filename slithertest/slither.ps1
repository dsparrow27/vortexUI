
$currentRoot=(Get-Item $PSScriptRoot).Parent.FullName
$env:PYTHONPATH="%PYTHONPATH%;$currentRoot"
$env:ZOO_PACKAGE_VERSION_FILE="package_version_cli.config"
$env:QT_SCALE_FACTOR="1.0"
$zRoot = $env:ZOOTOOLS_PRO_ROOT
& $zRoot\install\core\bin\zoo_cmd.bat env -- py $currentRoot\slithertest\slithermodel.py
