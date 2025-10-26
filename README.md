# 🚀 MLOps - Sistema de Recomendaciones

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-ECR%20%7C%20ECS-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org/)

> **Sistema completo de MLOps para recomendaciones de productos usando filtrado colaborativo**

## 🎯 **Descripción del Proyecto**

Este proyecto implementa un **pipeline completo de MLOps** para un sistema de recomendaciones de productos de e-commerce. Utiliza **filtrado colaborativo** y está optimizado para **despliegue en la nube** con Docker y AWS.

### ✨ **Características Principales**

- 🤖 **Algoritmo de ML**: Filtrado colaborativo inteligente
- 🚀 **API REST**: FastAPI con documentación automática
- 🐳 **Containerizado**: Docker listo para producción
- ☁️ **Cloud Ready**: Configurado para AWS ECS/Fargate y Kubernetes
- 📊 **Datos Sintéticos**: Dataset completo de prueba incluido
- 🔍 **Monitoreo**: Health checks y logging integrados
- 🧪 **Testing**: Scripts de prueba automatizados

## 📁 **Estructura del Proyecto**

```
📦 Proyecto_MLOps/
├── 🐳 Docker & Deployment
│   ├── Dockerfile              # Imagen Docker optimizada
│   ├── docker-compose.yml      # Orquestación con Nginx
│   ├── requirements.txt        # Dependencias Python
│   └── .dockerignore           # Archivos excluidos
│
├── ☁️ Cloud Configuration
│   ├── aws-ecs-task-definition.json    # Configuración ECS
│   ├── k8s-deployment.yaml            # Configuración Kubernetes
│   ├── deploy-ecs-simple.ps1          # Script despliegue AWS
│   └── nginx.conf                     # Configuración proxy
│
├── 🤖 Machine Learning
│   ├── api_nospark.py           # API principal (sin Spark)
│   ├── etl_spark.py            # ETL con PySpark (original)
│   └── entrenar_modelo.py      # Entrenamiento modelo ALS
│
├── 📊 Data
│   ├── usuarios.csv            # 100 usuarios sintéticos
│   ├── productos.csv           # 50 productos por categoría
│   └── interacciones.csv       # 5,000 interacciones
│
├── 🧪 Testing & Utils
│   ├── test_pipeline.py                # Test completo del pipeline
│   ├── analizador_recomendaciones.py   # Análisis de recomendaciones
│   ├── ejemplos_interpretacion.py      # Guías de interpretación
│   └── check-docker.ps1               # Verificación Docker
│
└── 📚 Documentation
    ├── README.md               # Este archivo
    ├── DOCKER_README.md        # Documentación Docker
    └── guia_interpretacion.md  # Guía de uso
```

## 🚀 **Quick Start**

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/mlops-recomendaciones.git
cd mlops-recomendaciones

# 2. Ejecutar con Docker
docker build -t mlops-api .
docker run -d --name mlops-api -p 8000:8000 mlops-api

# 3. ¡Listo! API disponible en http://localhost:8000
```

### Opción 2: Local

```bash
# 1. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar API
python api_nospark.py
```

## 🌐 **Uso de la API**

### Endpoints Principales

| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/` | GET | Estado general de la API |
| `/docs` | GET | Documentación interactiva |
| `/salud` | GET | Health check del sistema |
| `/recomendar/{user_id}` | GET | **Obtener 5 recomendaciones** |
| `/usuario/{user_id}/historial` | GET | Historial del usuario |
| `/usuarios` | GET | Lista de usuarios disponibles |
| `/productos` | GET | Lista de productos |

### Ejemplo de Uso

```bash
# Obtener recomendaciones para usuario 40
curl http://localhost:8000/recomendar/40

# Respuesta
{
  "user_id": 40,
  "total_recomendaciones": 5,
  "recomendaciones": [
    {
      "producto_id": 1025,
      "nombre": "Customer-focused homogeneous conglomeration",
      "categoria": "Electrónica",
      "precio": "$248.32",
      "puntuacion": 5.0,
      "metodo": "colaborativo"
    }
    // ... más recomendaciones
  ],
  "metodo": "filtrado_colaborativo + popularidad"
}
```

## 🤖 **Algoritmo de Recomendación**

### Cómo Funciona

1. **Análisis de Usuario**: Examina el historial de interacciones
2. **Usuarios Similares**: Encuentra usuarios con gustos parecidos
3. **Productos Candidatos**: Identifica productos que les gustaron
4. **Filtrado Inteligente**: Excluye productos ya conocidos
5. **Ranking**: Ordena por probabilidad de interés
6. **Fallback**: Usa productos populares si no hay datos suficientes

### Interpretación de Puntuaciones

- **5.0 - 4.8**: 🥇 Excelente - ¡Muy recomendado!
- **4.7 - 4.4**: 🥈 Buena - Opción sólida
- **4.3 - 3.5**: 🥉 Moderada - Considéralo
- **3.4 - 1.0**: 📊 Básica - Opción de respaldo

## 🐳 **Despliegue en Producción**

### AWS ECS/Fargate

```bash
# 1. Autenticar con ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 2. Construir y subir imagen
docker build -t mlops-api .
docker tag mlops-api:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mlops-api:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/mlops-api:latest

# 3. Desplegar con ECS
./deploy-ecs-simple.ps1
```

### Kubernetes

```bash
# Aplicar configuración
kubectl apply -f k8s-deployment.yaml

# Verificar despliegue
kubectl get pods -n mlops-recomendaciones
```

## 📊 **Datos del Proyecto**

- **👥 Usuarios**: 100 perfiles sintéticos realistas
- **🛍️ Productos**: 50 productos en 5 categorías
- **📈 Interacciones**: 5,000 eventos (clics, vistas, compras)
- **🎯 Categorías**: Electrónica, Ropa, Deportes, Hogar, Juguetes

## 🧪 **Testing**

```bash
# Ejecutar test completo del pipeline
python test_pipeline.py

# Analizar recomendaciones específicas
python analizador_recomendaciones.py

# Ver ejemplos de interpretación
python ejemplos_interpretacion.py
```

## 📈 **Métricas y Monitoreo**

- **Health Checks**: Endpoint `/salud` con estado detallado
- **Logs Estructurados**: Compatible con ELK Stack
- **Docker Health**: Verificación automática del contenedor
- **Métricas de Performance**: Tiempo de respuesta < 1s

## 🔧 **Configuración Avanzada**

### Variables de Entorno

```bash
ENV=production           # Entorno de ejecución
PORT=8000               # Puerto de la API
LOG_LEVEL=info          # Nivel de logging
```

### Escalabilidad

- **Horizontal**: Múltiples instancias con Load Balancer
- **Vertical**: Hasta 2GB RAM, 1 vCPU por instancia
- **Auto-scaling**: Configurado en Kubernetes HPA

## 🛠️ **Tecnologías Utilizadas**

| Categoría | Tecnología | Versión | Propósito |
|-----------|------------|---------|-----------|
| **Backend** | FastAPI | 0.104.1 | API REST Framework |
| **Data Processing** | Pandas | 2.1.4 | Manipulación de datos |
| **ML Algorithm** | Custom | - | Filtrado colaborativo |
| **Containerization** | Docker | Latest | Containerización |
| **Cloud** | AWS ECS | - | Orquestación |
| **Proxy** | Nginx | Alpine | Load Balancer |
| **Testing** | Python | 3.11 | Scripts de prueba |

## 🎯 **Roadmap**

- [ ] **Modelo ML Avanzado**: Implementar ALS con PySpark
- [ ] **Base de Datos**: Migrar a PostgreSQL/MongoDB
- [ ] **Cache**: Implementar Redis para recomendaciones
- [ ] **CI/CD**: Pipeline automático con GitHub Actions
- [ ] **Monitoring**: Prometheus + Grafana
- [ ] **Security**: Autenticación JWT
- [ ] **A/B Testing**: Comparación de algoritmos

## 🤝 **Contribuir**

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 **Autor**

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- LinkedIn: [tu-perfil](https://linkedin.com/in/tu-perfil)
- Email: tu-email@example.com

## 🙏 **Agradecimientos**

- FastAPI por el excelente framework
- Docker por simplificar el despliegue
- AWS por la infraestructura cloud
- Comunidad MLOps por las mejores prácticas

---

⭐ **¡Si este proyecto te fue útil, dale una estrella!** ⭐