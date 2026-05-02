# QR Access Control PRO - Start Script (PowerShell)
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  QR Access Control PRO - Iniciando" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Activate venv
$venvPath = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green
}
else {
    Write-Host "[WARN] No se encontro venv, usando Python global" -ForegroundColor Yellow
}

# Start web panel
Write-Host "[>>] Iniciando panel web en http://localhost:5000 ..." -ForegroundColor Cyan
python (Join-Path $PSScriptRoot "web_panel\app.py")
