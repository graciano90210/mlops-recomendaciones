# Uso: Ejecuta este script en PowerShell desde la carpeta del proyecto
#   powershell -ExecutionPolicy Bypass -File .\scripts\setup_py311_venv.ps1
# Crea un entorno .venv311 con Python 3.11, instala Torch CPU y requirements del módulo Two-Tower.

$ErrorActionPreference = "Stop"

Write-Host "[1/6] Verificando instalador de Python 3.11..." -ForegroundColor Cyan

function Get-Py311Path {
  try {
    $pyExe = (Get-Command py -ErrorAction SilentlyContinue)
    if ($pyExe) {
      $out = & py -3.11 -c "import sys; print(sys.executable)" 2>$null
      if ($LASTEXITCODE -eq 0 -and $out) { return $out.Trim() }
    }
  } catch {}
  $candidates = @(
    "$Env:LocalAppData\Programs\Python\Python311\python.exe",
    "C:\\Program Files\\Python311\\python.exe",
    "C:\\Python311\\python.exe"
  )
  foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
  return $null
}

$py311 = Get-Py311Path
if (-not $py311) {
  Write-Host "Python 3.11 no encontrado. Intentando instalar con winget..." -ForegroundColor Yellow
  $winget = (Get-Command winget -ErrorAction SilentlyContinue)
  if (-not $winget) {
    Write-Error "winget no está disponible. Instala Python 3.11 manualmente desde https://www.python.org/downloads/release/python-3110/ y reintenta."
  }
  winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
  Start-Sleep -Seconds 5
  $py311 = Get-Py311Path
  if (-not $py311) { Write-Error "No se pudo localizar Python 3.11 tras la instalación." }
}

Write-Host "Usando Python 3.11 en: $py311" -ForegroundColor Green

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$venvPath = Join-Path $projectRoot ".venv311"

Write-Host "[2/6] Creando venv en $venvPath ..." -ForegroundColor Cyan
& "$py311" -m venv "$venvPath"

$py = Join-Path $venvPath "Scripts\python.exe"
$pip = Join-Path $venvPath "Scripts\pip.exe"

Write-Host "[3/6] Actualizando pip/setuptools/wheel..." -ForegroundColor Cyan
& "$py" -m pip install --upgrade pip setuptools wheel

Write-Host "[4/6] Instalando Torch CPU desde índice oficial..." -ForegroundColor Cyan
& "$py" -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio

Write-Host "[5/6] Instalando requirements del módulo..." -ForegroundColor Cyan
& "$pip" install -r (Join-Path $projectRoot "next_rec_two_tower\requirements-tt.txt")

Write-Host "[6/6] Listo. Activa el entorno y prueba entrenamiento:" -ForegroundColor Green
Write-Host "`nPara activar:" -NoNewline; Write-Host " `n  `"$venvPath\Scripts\Activate.ps1`"" -ForegroundColor Yellow
Write-Host "`nEntrenar:`n  `"$py`" `"$projectRoot\next_rec_two_tower\models\train_two_tower.py`" --data-root `"$projectRoot`" --artifacts `"$projectRoot\.artifacts`" --epochs 1 --dim 16" -ForegroundColor Yellow
