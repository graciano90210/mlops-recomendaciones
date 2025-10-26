# 🚀 Script de construcción y despliegue de Docker para Windows
# ===========================================================

Write-Host "🐳 MLOps API - Docker Build & Deploy Script" -ForegroundColor Blue
Write-Host "===========================================" -ForegroundColor Blue

# Variables
$IMAGE_NAME = "mlops-recomendaciones"
$TAG = "latest"
$CONTAINER_NAME = "mlops-api-container"

Write-Host "📦 Paso 1: Construyendo imagen Docker..." -ForegroundColor Blue
docker build -t ${IMAGE_NAME}:${TAG} .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Imagen construida exitosamente!" -ForegroundColor Green
} else {
    Write-Host "❌ Error construyendo la imagen" -ForegroundColor Red
    exit 1
}

Write-Host "🧹 Paso 2: Limpiando contenedores anteriores..." -ForegroundColor Blue
docker stop $CONTAINER_NAME 2>$null
docker rm $CONTAINER_NAME 2>$null

Write-Host "🚀 Paso 3: Ejecutando contenedor..." -ForegroundColor Blue
docker run -d --name $CONTAINER_NAME -p 8000:8000 --restart unless-stopped ${IMAGE_NAME}:${TAG}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Contenedor iniciado exitosamente!" -ForegroundColor Green
    Write-Host "📍 API disponible en: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "📖 Documentación en: http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host "🏥 Health check en: http://localhost:8000/salud" -ForegroundColor Yellow
} else {
    Write-Host "❌ Error iniciando el contenedor" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Paso 4: Verificando estado..." -ForegroundColor Blue
Start-Sleep -Seconds 5

# Verificar que el contenedor esté corriendo
$containerStatus = docker ps --filter "name=$CONTAINER_NAME" --format "{{.Status}}"

if ($containerStatus) {
    Write-Host "✅ Contenedor corriendo correctamente" -ForegroundColor Green
    
    # Probar la API
    Write-Host "🔍 Probando la API..." -ForegroundColor Blue
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/salud" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API respondiendo correctamente!" -ForegroundColor Green
            Write-Host "🎉 ¡Despliegue completado exitosamente!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ API aún iniciando..." -ForegroundColor Yellow
        Write-Host "💡 Prueba en unos minutos: http://localhost:8000" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Contenedor no está corriendo" -ForegroundColor Red
    Write-Host "📋 Logs del contenedor:" -ForegroundColor Yellow
    docker logs $CONTAINER_NAME
}

Write-Host ""
Write-Host "🛠️ Comandos útiles:" -ForegroundColor Blue
Write-Host "  Ver logs:      docker logs $CONTAINER_NAME"
Write-Host "  Parar:         docker stop $CONTAINER_NAME"
Write-Host "  Reiniciar:     docker restart $CONTAINER_NAME"
Write-Host "  Eliminar:      docker rm $CONTAINER_NAME"
Write-Host "  Entrar:        docker exec -it $CONTAINER_NAME bash"