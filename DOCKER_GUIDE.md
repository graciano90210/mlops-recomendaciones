# 🐳 Docker Documentation - MLOps Recomendaciones

> **Guía completa para containerización y despliegue de la API de recomendaciones**

## 📋 **Índice**

- [🎯 Información General](#-información-general)
- [🏗️ Construcción de Imagen](#️-construcción-de-imagen)
- [🚀 Ejecución Local](#-ejecución-local)
- [⚙️ Configuración Avanzada](#️-configuración-avanzada)
- [🌐 Despliegue en Producción](#-despliegue-en-producción)
- [🔧 Troubleshooting](#-troubleshooting)

## 🎯 **Información General**

### Características de la Imagen

- **Base**: `python:3.11-slim` (Ubuntu optimizada)
- **Tamaño**: ~150MB (comprimida)
- **Puerto**: 8000 (FastAPI)
- **Usuario**: No-root (`appuser`) para seguridad
- **Health Check**: Endpoint `/salud` cada 30 segundos

### Estructura de Capas

```dockerfile
📦 Imagen Final
├── 🐍 Python 3.11 Runtime
├── 👤 Usuario no-root (appuser)
├── 📁 Directorio de trabajo (/app)
├── 📦 Dependencias Python optimizadas
├── 📊 Datos CSV (usuarios, productos, interacciones)
├── 🚀 API FastAPI (api_nospark.py)
└── ❤️ Health Check configurado
```

## 🏗️ **Construcción de Imagen**

### Build Básico

```bash
# Construcción estándar
docker build -t mlops-api .

# Con tag específico
docker build -t mlops-api:v1.0.0 .

# Con logs detallados
docker build --progress=plain -t mlops-api .
```

### Build Optimizado

```bash
# Usando cache de BuildKit
DOCKER_BUILDKIT=1 docker build -t mlops-api .

# Multi-platform (ARM64 + AMD64)
docker buildx build --platform linux/amd64,linux/arm64 -t mlops-api .

# Con etiquetas múltiples
docker build -t mlops-api:latest -t mlops-api:production .
```

### Verificar Construcción

```bash
# Ver información de la imagen
docker image inspect mlops-api

# Verificar tamaño
docker images mlops-api

# Analizar capas
docker history mlops-api
```

## 🚀 **Ejecución Local**

### Ejecución Básica

```bash
# Ejecutar en primer plano
docker run -p 8000:8000 mlops-api

# Ejecutar en background
docker run -d --name mlops-api -p 8000:8000 mlops-api

# Con logs en tiempo real
docker run -d --name mlops-api -p 8000:8000 mlops-api && docker logs -f mlops-api
```

### Configuración de Entorno

```bash
# Con variables de entorno personalizadas
docker run -d \
  --name mlops-api \
  -p 8000:8000 \
  -e ENV=production \
  -e LOG_LEVEL=info \
  mlops-api

# Con límites de recursos
docker run -d \
  --name mlops-api \
  -p 8000:8000 \
  --memory=512m \
  --cpus=1.0 \
  mlops-api
```

## ⚙️ **Configuración Avanzada**

### Variables de Entorno

| Variable | Descripción | Default | Ejemplo |
|----------|-------------|---------|---------|
| `ENV` | Entorno de ejecución | `development` | `production` |
| `PORT` | Puerto de la API | `8000` | `8080` |
| `LOG_LEVEL` | Nivel de logging | `info` | `debug` |
| `WORKERS` | Número de workers | `1` | `4` |

### Health Check Custom

```bash
# Verificar health check
docker run -d --name mlops-api -p 8000:8000 mlops-api
docker inspect --format='{{.State.Health.Status}}' mlops-api

# Health check manual
curl http://localhost:8000/salud
```

## 🌐 **Despliegue en Producción**

### AWS ECR Deployment

```bash
# 1. Autenticar con ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  322614675421.dkr.ecr.us-east-1.amazonaws.com

# 2. Tag para ECR
docker tag mlops-api:latest \
  322614675421.dkr.ecr.us-east-1.amazonaws.com/mlops-recomendaciones:latest

# 3. Push a ECR
docker push 322614675421.dkr.ecr.us-east-1.amazonaws.com/mlops-recomendaciones:latest

# 4. Deploy en ECS
aws ecs update-service \
  --cluster mlops-cluster \
  --service mlops-api-service \
  --force-new-deployment
```

## 🔧 **Troubleshooting**

### Comandos de Debug

```bash
# Entrar al contenedor
docker exec -it mlops-api bash

# Ver logs detallados
docker logs --details mlops-api

# Monitorear recursos
docker stats mlops-api

# Inspeccionar configuración
docker inspect mlops-api
```

---

## 🎯 **Quick Reference**

### Comandos Esenciales

```bash
# Build
docker build -t mlops-api .

# Run
docker run -d --name mlops-api -p 8000:8000 mlops-api

# Logs
docker logs -f mlops-api

# Stop
docker stop mlops-api

# Remove
docker rm mlops-api
```

### URLs Importantes

- **API Local**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/salud
- **Recomendaciones**: http://localhost:8000/recomendar/40

---

¿Problemas? Consulta la sección [Troubleshooting](#-troubleshooting) o abre un issue en GitHub 🚀