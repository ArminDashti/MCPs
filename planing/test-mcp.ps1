# PowerShell script to automatically test the MCP server
# Usage: .\test-mcp.ps1

param(
    [string]$PythonPath = "python"
)

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MCP Server Automated Testing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Directory: $ScriptDir" -ForegroundColor Gray
Write-Host "Python: $PythonPath" -ForegroundColor Gray
Write-Host ""

# Check if test script exists
$TestScript = Join-Path $ScriptDir "test_mcp_auto.py"
if (-not (Test-Path $TestScript)) {
    Write-Host "Error: test_mcp_auto.py not found!" -ForegroundColor Red
    exit 1
}

# Check if h2a.py exists
$ServerScript = Join-Path $ScriptDir "h2a.py"
if (-not (Test-Path $ServerScript)) {
    Write-Host "Error: h2a.py not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Running automated tests..." -ForegroundColor Yellow
Write-Host ""

try {
    # Run the test script
    & $PythonPath $TestScript
    
    $ExitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    if ($ExitCode -eq 0) {
        Write-Host "Tests completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Tests failed with exit code: $ExitCode" -ForegroundColor Red
    }
    Write-Host "========================================" -ForegroundColor Cyan
    
    exit $ExitCode
}
catch {
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
