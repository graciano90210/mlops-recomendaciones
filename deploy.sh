#!/bin/bash
# 🚀 Script de construcción y despliegue de Docker
# ===============================================

echo "🐳 MLOps API - Docker Build & Deploy Script"
echo "==========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
IMAGE_NAME="mlops-recomendaciones"
TAG="latest"
CONTAINER_NAME="mlops-api-container"

echo -e "${BLUE}📦 Paso 1: Construyendo imagen Docker...${NC}"
docker build -t ${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imagen construida exitosamente!${NC}"
else
    echo -e "${RED}❌ Error construyendo la imagen${NC}"
    exit 1
fi

echo -e "${BLUE}🧹 Paso 2: Limpiando contenedores anteriores...${NC}"
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

echo -e "${BLUE}🚀 Paso 3: Ejecutando contenedor...${NC}"
docker run -d \
    --name ${CONTAINER_NAME} \
    -p 8000:8000 \
    --restart unless-stopped \
    ${IMAGE_NAME}:${TAG}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Contenedor iniciado exitosamente!${NC}"
    echo -e "${YELLOW}📍 API disponible en: http://localhost:8000${NC}"
    echo -e "${YELLOW}📖 Documentación en: http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}🏥 Health check en: http://localhost:8000/salud${NC}"
else
    echo -e "${RED}❌ Error iniciando el contenedor${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Paso 4: Verificando estado...${NC}"
sleep 5

# Verificar que el contenedor esté corriendo
if docker ps | grep -q ${CONTAINER_NAME}; then
    echo -e "${GREEN}✅ Contenedor corriendo correctamente${NC}"
    
    # Probar la API
    echo -e "${BLUE}🔍 Probando la API...${NC}"
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/salud)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ API respondiendo correctamente!${NC}"
        echo -e "${GREEN}🎉 ¡Despliegue completado exitosamente!${NC}"
    else
        echo -e "${YELLOW}⚠️ API aún iniciando... (código: $response)${NC}"
        echo -e "${YELLOW}💡 Prueba en unos minutos: http://localhost:8000${NC}"
    fi
else
    echo -e "${RED}❌ Contenedor no está corriendo${NC}"
    echo -e "${YELLOW}📋 Logs del contenedor:${NC}"
    docker logs ${CONTAINER_NAME}
fi

echo ""
echo -e "${BLUE}🛠️ Comandos útiles:${NC}"
echo "  Ver logs:      docker logs ${CONTAINER_NAME}"
echo "  Parar:         docker stop ${CONTAINER_NAME}"
echo "  Reiniciar:     docker restart ${CONTAINER_NAME}"
echo "  Eliminar:      docker rm ${CONTAINER_NAME}"
echo "  Entrar:        docker exec -it ${CONTAINER_NAME} bash"