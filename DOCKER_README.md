# 🐳 Documentación de Dockerización - API MLOps
# =============================================

## 🎯 Objetivo
Containerizar la API de recomendaciones MLOps para garantizar portabilidad y facilitar el despliegue en cualquier entorno.

## 📦 Archivos Docker

### 1. **Dockerfile**
- Imagen base: `python:3.11-slim`
- Usuario no-root para seguridad
- Health checks automáticos
- Optimizado para producción

### 2. **docker-compose.yml**
- Orquestación completa con Nginx
- Networking interno
- Persistent volumes para logs
- Auto-restart en fallos

### 3. **requirements.txt**
- Dependencias mínimas necesarias
- Sin PySpark (no requerido)
- Versiones fijas para estabilidad

## 🚀 Comandos de Despliegue

### Opción 1: Script Automatizado (Recomendado)
```powershell
# Windows
.\deploy.ps1

# Linux/Mac
./deploy.sh
```

### Opción 2: Comandos Manuales
```bash
# Construir imagen
docker build -t mlops-recomendaciones:latest .

# Ejecutar contenedor
docker run -d --name mlops-api -p 8000:8000 mlops-recomendaciones:latest

# Con Docker Compose (incluye Nginx)
docker-compose up -d
```

## 🔧 Configuración

### Variables de Entorno
- `PORT`: Puerto de la API (default: 8000)
- `ENV`: Entorno de ejecución (development/production)

### Puertos
- **8000**: API Principal
- **80**: Nginx Proxy (solo con docker-compose)

## 🏥 Health Checks

La imagen incluye health checks automáticos:
- **Endpoint**: `/salud`
- **Intervalo**: 30 segundos
- **Timeout**: 10 segundos
- **Reintentos**: 3

## 📊 Monitoreo

### Ver logs del contenedor:
```bash
docker logs mlops-api-container
```

### Acceder al contenedor:
```bash
docker exec -it mlops-api-container bash
```

### Verificar estado:
```bash
docker ps
curl http://localhost:8000/salud
```

## 🌐 URLs de Acceso

Una vez desplegado:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/salud
- **Recomendaciones**: http://localhost:8000/recomendar/{user_id}

## 🚢 Despliegue en la Nube

### AWS ECS/Fargate
```bash
# Subir a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker tag mlops-recomendaciones:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/mlops-api:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/mlops-api:latest
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlops-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mlops-api
  template:
    metadata:
      labels:
        app: mlops-api
    spec:
      containers:
      - name: api
        image: mlops-recomendaciones:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /salud
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 🔒 Seguridad

- ✅ Usuario no-root en contenedor
- ✅ Imagen base minimal (slim)
- ✅ Sin secretos hardcoded
- ✅ Health checks para estabilidad
- ✅ Headers de seguridad en Nginx

## 📈 Optimizaciones

- **Multi-stage build**: No implementado (imagen ya es pequeña)
- **Layer caching**: requirements.txt copiado antes que código
- **Minimal dependencies**: Solo lo necesario para la API
- **.dockerignore**: Excluye archivos innecesarios

## 🛠️ Troubleshooting

### Problema: API no responde
```bash
# Verificar logs
docker logs mlops-api-container

# Verificar que el contenedor esté corriendo
docker ps

# Reiniciar contenedor
docker restart mlops-api-container
```

### Problema: Puerto ya en uso
```bash
# Cambiar puerto de host
docker run -d --name mlops-api -p 8001:8000 mlops-recomendaciones:latest
```

### Problema: Health check falla
```bash
# Verificar endpoint manualmente
curl http://localhost:8000/salud

# Aumentar tiempo de health check
# Modificar HEALTHCHECK en Dockerfile
```

## 🎯 Próximos Pasos

1. **CI/CD Pipeline**: Automatizar build y deploy
2. **Monitoring**: Prometheus + Grafana
3. **Logging**: ELK Stack o similar
4. **Scaling**: Kubernetes HPA
5. **Security**: Escaneo de vulnerabilidades

## 📝 Notas Importantes

- La imagen no incluye PySpark (no necesario)
- Los datos CSV están embebidos en la imagen
- Para datos dinámicos, usar volúmenes o bases de datos externas
- El contenedor está optimizado para ser stateless