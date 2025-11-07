param(
    [string]$PythonExe = "python",
    [string[]]$PythonArgs = @()
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

& $PythonExe @PythonArgs -m src.server

