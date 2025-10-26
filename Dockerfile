# 🐳 Dockerfile para API MLOps sin Spark
# =====================================
# Imagen base optimizada para Python
FROM python:3.11-slim

# Información del mantenedor
LABEL maintainer="MLOps Team"
LABEL description="API de Recomendaciones MLOps con Filtrado Colaborativo"
LABEL version="3.0-NoSpark"

# Variables de entorno para optimización
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN groupadd -r mlops && useradd -r -g mlops mlops

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias del sistema y Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copiar archivos de la aplicación
COPY api_nospark.py .
COPY *.csv ./

# Crear directorio para logs
RUN mkdir -p /app/logs && chown -R mlops:mlops /app

# Cambiar al usuario no-root
USER mlops

# Exponer el puerto de la API
EXPOSE 8000

# Health check para verificar que la API esté funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/salud || exit 1

# Comando por defecto para ejecutar la aplicación
CMD ["python", "api_nospark.py"]