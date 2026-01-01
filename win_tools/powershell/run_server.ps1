# PowerShell script to run the PowerShell MCP server
Write-Host "Starting PowerShell MCP Server..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if required modules are available
Write-Host "Checking dependencies..." -ForegroundColor Cyan
try {
    python -c "import mcp" 2>$null
    Write-Host "MCP module found" -ForegroundColor Green
} catch {
    Write-Host "Installing MCP module..." -ForegroundColor Yellow
    python -m pip install mcp>=0.9.0
}

# Run the server
Write-Host "Starting PowerShell MCP server..." -ForegroundColor Green
python powershell.py
