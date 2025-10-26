# 🏗️ Arquitectura MLOps - Sistema de Recomendaciones

```
📱 FRONTEND & INTERFACES
┌─────────────────────────┐
│     GitHub Pages        │ ← Documentación y landing page pública
│   (Jekyll + Markdown)   │
└─────────────────────────┘
            │
            ▼
📊 DESARROLLO & VERSIONADO
┌─────────────────────────┐
│       GitHub            │ ← Control de versiones del código
│    (Git Repository)     │ ← Colaboración y historial de cambios
└─────────────────────────┘
            │
            ▼
🔄 CI/CD PIPELINE
┌─────────────────────────┐
│   GitHub Actions        │ ← Automatización: build, test, deploy
│  (Workflow Automation)  │ ← Testing automático en cada commit
└─────────────────────────┘
            │
            ▼
🐳 CONTAINERIZACIÓN
┌─────────────────────────┐
│        Docker           │ ← Empaqueta la aplicación y dependencias
│   (Container Platform)  │ ← Garantiza que funcione en cualquier lado
└─────────────────────────┘
            │
            ▼
☁️ CLOUD STORAGE
┌─────────────────────────┐
│     Amazon ECR          │ ← Almacena las imágenes Docker
│  (Container Registry)   │ ← Versiona y distribuye contenedores
└─────────────────────────┘
            │
            ▼
⚖️ ORQUESTACIÓN
┌─────────────────────────┐
│     Amazon ECS          │ ← Ejecuta y gestiona contenedores
│   (Container Service)   │ ← Auto-scaling y load balancing
└─────────────────────────┘
            │
            ▼
🚀 APLICACIÓN PRINCIPAL
┌─────────────────────────┐
│       FastAPI           │ ← Framework web para crear la API REST
│    (Python Web API)     │ ← Documentación automática (/docs)
└─────────────────────────┘
            │
            ▼
🤖 MACHINE LEARNING
┌─────────────────────────┐
│        Pandas           │ ← Manipulación y análisis de datos
│   (Data Processing)     │ ← Algoritmo de filtrado colaborativo
└─────────────────────────┘
            │
            ▼
📊 DATOS
┌─────────────────────────┐
│      CSV Files          │ ← Usuarios, productos, interacciones
│   (Static Dataset)      │ ← 100 usuarios, 50 productos, 5k eventos
└─────────────────────────┘

🌐 INFRAESTRUCTURA ADICIONAL
┌─────────────────────────┐     ┌─────────────────────────┐
│      Kubernetes         │     │        Nginx            │
│   (Alternative Deploy)  │     │    (Reverse Proxy)      │
│   Auto-scaling + HPA    │     │   Load Balancer         │
└─────────────────────────┘     └─────────────────────────┘

📈 MONITOREO & LOGS
┌─────────────────────────┐     ┌─────────────────────────┐
│    CloudWatch Logs      │     │    Health Checks        │
│   (AWS Monitoring)      │     │  (Uptime Monitoring)    │
│   Logs centralizados    │     │   Status endpoints      │
└─────────────────────────┘     └─────────────────────────┘

🔒 SEGURIDAD & PERMISOS
┌─────────────────────────┐     ┌─────────────────────────┐
│       IAM Roles         │     │   Security Groups       │
│   (AWS Permissions)     │     │  (Network Firewall)     │
│   ecsTaskRole, etc.     │     │   Port 8000 access      │
└─────────────────────────┘     └─────────────────────────┘
```

## 🛠️ **Explicación Detallada de Cada Tecnología**

### 🐍 **DESARROLLO & LENGUAJE**

| Tecnología | Propósito | ¿Por qué la usamos? |
|------------|-----------|---------------------|
| **Python 3.11** | Lenguaje principal | • Excelente para ML y APIs<br>• Gran ecosistema de librerías<br>• Fácil de leer y mantener |
| **Pandas** | Análisis de datos | • Manipulación eficiente de CSV<br>• Operaciones matriciales rápidas<br>• Ideal para filtrado colaborativo |
| **FastAPI** | Framework web | • API REST moderna y rápida<br>• Documentación automática<br>• Validación de datos integrada |
| **Uvicorn** | Servidor ASGI | • Servidor de alta performance<br>• Compatible con async/await<br>• Producción-ready |

### 🐳 **CONTAINERIZACIÓN & DESPLIEGUE**

| Tecnología | Propósito | ¿Por qué la usamos? |
|------------|-----------|---------------------|
| **Docker** | Containerización | • "Funciona en mi máquina" → Funciona en todas<br>• Aísla dependencias<br>• Despliegue consistente |
| **Docker Compose** | Orquestación local | • Define múltiples servicios (API + Nginx)<br>• Networking automático<br>• Desarrollo local simplificado |
| **Nginx** | Proxy inverso | • Load balancer para múltiples instancias<br>• Terminación SSL<br>• Cacheo de respuestas |

### ☁️ **CLOUD COMPUTING (AWS)**

| Tecnología | Propósito | ¿Por qué la usamos? |
|------------|-----------|---------------------|
| **Amazon ECR** | Registry de imágenes | • Almacena versiones de Docker images<br>• Integración nativa con ECS<br>• Scanning de vulnerabilidades |
| **Amazon ECS** | Orquestación de contenedores | • Ejecuta contenedores sin gestionar servidores<br>• Auto-scaling automático<br>• Pay-per-use |
| **AWS Fargate** | Compute serverless | • No gestión de servidores<br>• Escalado automático<br>• Solo pagas por recursos usados |
| **CloudWatch** | Monitoreo y logs | • Logs centralizados<br>• Métricas de performance<br>• Alertas automáticas |
| **IAM Roles** | Seguridad | • Permisos granulares<br>• Principio de menor privilegio<br>• Sin credenciales hardcoded |

### 🔄 **CI/CD & AUTOMATIZACIÓN**

| Tecnología | Propósito | ¿Por qué la usamos? |
|------------|-----------|---------------------|
| **GitHub Actions** | CI/CD Pipeline | • Testing automático en cada commit<br>• Deploy automático a AWS<br>• Workflow configurable |
| **Git** | Control de versiones | • Historial completo de cambios<br>• Colaboración en equipo<br>• Branching strategies |
| **GitHub Pages** | Hosting estático | • Documentación automática<br>• Portfolio público<br>• Gratis con dominio |

### ⚖️ **ORQUESTACIÓN AVANZADA**

| Tecnología | Propósito | ¿Por qué la usamos? |
|------------|-----------|---------------------|
| **Kubernetes** | Orquestación enterprise | • Auto-scaling horizontal (HPA)<br>• Self-healing containers<br>• Rolling updates sin downtime |
| **Helm** | Package manager K8s | • Templates reutilizables<br>• Versionado de deployments<br>• Configuración parametrizada |

### 📊 **DATOS & MACHINE LEARNING**

| Tecnología | Propósito | ¿Por qué la usamos? |
|------------|-----------|---------------------|
| **CSV Files** | Storage de datos | • Formato simple y portable<br>• Fácil de inspeccionar<br>• Compatible con todas las herramientas |
| **Filtrado Colaborativo** | Algoritmo ML | • Recomendaciones basadas en usuarios similares<br>• No requiere features complejas<br>• Escalable y interpretable |

### 🛡️ **SEGURIDAD & NETWORKING**

| Tecnología | Propósito | ¿Por qué la usamos? |
|------------|-----------|---------------------|
| **Security Groups** | Firewall de red | • Control granular de puertos<br>• Reglas de entrada/salida<br>• Seguridad por capas |
| **VPC** | Red privada virtual | • Aislamiento de recursos<br>• Control de networking<br>• Integración con servicios AWS |

## 🎯 **Flujo Completo del Proyecto**

### 📋 **1. Desarrollo Local**
```
Developer → Git → VS Code → Python/FastAPI → Docker → Local Testing
```

### 📋 **2. Pipeline CI/CD**
```
Git Push → GitHub Actions → Docker Build → Tests → ECR Push → ECS Deploy
```

### 📋 **3. Producción**
```
User Request → Load Balancer → ECS Fargate → FastAPI → ML Algorithm → Response
```

### 📋 **4. Monitoreo**
```
CloudWatch ← ECS ← FastAPI ← Health Checks ← Automated Alerts
```

## 🌟 **¿Por qué esta arquitectura es MLOps?**

### ✅ **Características MLOps que implementamos:**

1. **🔄 Automation**: CI/CD completo con GitHub Actions
2. **📦 Containerization**: Docker para consistencia entre entornos
3. **☁️ Cloud-Native**: AWS para escalabilidad y confiabilidad
4. **📊 Monitoring**: CloudWatch para observabilidad
5. **🔒 Security**: IAM roles y Security Groups
6. **📈 Scalability**: ECS/Fargate + Kubernetes para auto-scaling
7. **🧪 Testing**: Automated testing en pipeline
8. **📚 Documentation**: GitHub Pages + API docs
9. **🎯 Reproducibility**: Todo versionado y automatizado
10. **🚀 Fast Deployment**: Deploy automático en minutos

¡Esta es una arquitectura MLOps completa y profesional que cualquier empresa estaría orgullosa de tener! 💪🚀