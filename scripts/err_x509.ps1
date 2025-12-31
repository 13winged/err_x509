#Requires -Version 3.0

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            err_x509 - x509 SSL Fixer          ║" -ForegroundColor Cyan
Write-Host "║          Fix Clash SSL certificate errors     ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check for Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3 from python.org" -ForegroundColor Yellow
    if ($Host.Name -eq "ConsoleHost") {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Run err_x509
& $python.Source -m err_x509 @args

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Operation completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Operation failed!" -ForegroundColor Red
}

if ($Host.Name -eq "ConsoleHost") {
    Read-Host "Press Enter to exit"
}