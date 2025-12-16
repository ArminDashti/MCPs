# PowerShell script to run the MCP (Model Context Protocol) server
# Usage: .\run-mcp.ps1

param(
    [string]$PythonPath = "python"
)

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MCP Server Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Directory: $ScriptDir" -ForegroundColor Gray
Write-Host "Python: $PythonPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Starting MCP server..." -ForegroundColor Yellow
Write-Host "The server will communicate via stdio (standard input/output)" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Run the MCP server
    & $PythonPath h2a.py
}
catch {
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
finally {
    Write-Host ""
    Write-Host "MCP server stopped." -ForegroundColor Yellow
}
