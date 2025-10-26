# 🔧 Script de verificación de Docker para Windows
# ===============================================

Write-Host "🐳 Verificando Docker..." -ForegroundColor Blue

# Verificar si Docker está instalado
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ Docker instalado: $dockerVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Docker no está instalado" -ForegroundColor Red
    Write-Host "💡 Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar si Docker está corriendo
try {
    docker info 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker está corriendo" -ForegroundColor Green
    } else {
        throw "Docker no está corriendo"
    }
} catch {
    Write-Host "⚠️ Docker no está corriendo" -ForegroundColor Yellow
    Write-Host "🚀 Iniciando Docker Desktop..." -ForegroundColor Blue
    
    # Intentar iniciar Docker Desktop
    $dockerDesktopPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktopPath) {
        Start-Process $dockerDesktopPath
        Write-Host "⏳ Esperando a que Docker se inicie..." -ForegroundColor Yellow
        Write-Host "   Esto puede tomar 30-60 segundos..." -ForegroundColor Yellow
        
        # Esperar hasta que Docker esté listo
        $timeout = 120 # 2 minutos
        $elapsed = 0
        
        while ($elapsed -lt $timeout) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            
            try {
                docker info 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Docker está listo!" -ForegroundColor Green
                    break
                }
            } catch {
                # Continuar esperando
            }
            
            Write-Host "   Esperando... ($elapsed/$timeout segundos)" -ForegroundColor Yellow
        }
        
        if ($elapsed -ge $timeout) {
            Write-Host "❌ Timeout esperando a Docker" -ForegroundColor Red
            Write-Host "💡 Inicia Docker Desktop manualmente y vuelve a ejecutar este script" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "❌ No se encontró Docker Desktop" -ForegroundColor Red
        Write-Host "💡 Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Docker está listo para usar!" -ForegroundColor Green
Write-Host "🚀 Ahora puedes ejecutar:" -ForegroundColor Blue
Write-Host "   .\deploy.ps1" -ForegroundColor White