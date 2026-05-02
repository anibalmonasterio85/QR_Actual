# QR Access Control PRO - Stop Script (PowerShell)
Write-Host ""
Write-Host "Deteniendo QR Access Control PRO..." -ForegroundColor Yellow

$processes = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($processes) {
    foreach ($pid in $processes) {
        Write-Host "  Terminando proceso PID: $pid" -ForegroundColor Red
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Panel web detenido." -ForegroundColor Green
} else {
    Write-Host "[INFO] No hay procesos en el puerto 5000." -ForegroundColor Cyan
}
