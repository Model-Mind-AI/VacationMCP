# Quick Setup Verification Script
# Run this to verify your deployment and local setup

Write-Host "=== VacationMCP Deployment Verification ===" -ForegroundColor Cyan
Write-Host ""

# Check if required files exist
Write-Host "Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "mcp_server.py",
    "Dockerfile",
    "render.yaml",
    "requirements.txt",
    "src\app.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (MISSING)" -ForegroundColor Red
    }
}

Write-Host ""

# Check Python and packages
Write-Host "Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
}

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "  ✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Virtual environment not found (recommended)" -ForegroundColor Yellow
}

# Check MCP package
Write-Host ""
Write-Host "Checking Python packages..." -ForegroundColor Yellow
try {
    $mcpInstalled = python -c "import mcp; print('installed')" 2>&1
    if ($mcpInstalled -match "installed") {
        Write-Host "  ✓ mcp package installed" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ mcp package not found. Install with: pip install mcp" -ForegroundColor Red
}

try {
    $requestsInstalled = python -c "import requests; print('installed')" 2>&1
    if ($requestsInstalled -match "installed") {
        Write-Host "  ✓ requests package installed" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ requests package not found. Install with: pip install requests" -ForegroundColor Red
}

# Check MCP server script
Write-Host ""
Write-Host "Checking MCP server script..." -ForegroundColor Yellow
if (Test-Path "mcp_server.py") {
    $scriptPath = (Resolve-Path "mcp_server.py").Path
    Write-Host "  ✓ mcp_server.py found at:" -ForegroundColor Green
    Write-Host "    $scriptPath" -ForegroundColor Gray
} else {
    Write-Host "  ✗ mcp_server.py not found" -ForegroundColor Red
}

# Check for Cursor MCP config
Write-Host ""
Write-Host "Checking Cursor MCP configuration..." -ForegroundColor Yellow
$cursorConfigPath = "$env:APPDATA\Cursor\User\globalStorage\mcp.json"
if (Test-Path $cursorConfigPath) {
    Write-Host "  ✓ Cursor MCP config found" -ForegroundColor Green
    try {
        $config = Get-Content $cursorConfigPath | ConvertFrom-Json
        if ($config.mcpServers.'vacation-mcp') {
            Write-Host "  ✓ vacation-mcp configured" -ForegroundColor Green
            $config.mcpServers.'vacation-mcp' | Format-List
        } else {
            Write-Host "  ⚠ vacation-mcp not configured in mcp.json" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠ Could not parse mcp.json (may have syntax errors)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Cursor MCP config not found at:" -ForegroundColor Yellow
    Write-Host "    $cursorConfigPath" -ForegroundColor Gray
    Write-Host "    (You may need to create it)" -ForegroundColor Gray
}

# Environment variables check
Write-Host ""
Write-Host "Checking environment variables..." -ForegroundColor Yellow
if ($env:VACATION_API_URL) {
    Write-Host "  ✓ VACATION_API_URL = $env:VACATION_API_URL" -ForegroundColor Green
} else {
    Write-Host "  ⚠ VACATION_API_URL not set (required for manual testing)" -ForegroundColor Yellow
}

if ($env:VACATION_API_KEY) {
    Write-Host "  ✓ VACATION_API_KEY is set" -ForegroundColor Green
} else {
    Write-Host "  ⚠ VACATION_API_KEY not set (required for manual testing)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Verification Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Deploy to Render (see DEPLOYMENT_GUIDE.md)" -ForegroundColor White
Write-Host "2. Configure Cursor MCP settings" -ForegroundColor White
Write-Host "3. Restart Cursor and test!" -ForegroundColor White

