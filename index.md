---
layout: default
title: MLOps Recommendation System
description: 🚀 Sistema completo de MLOps para recomendaciones con FastAPI, Docker y AWS
---

# 🚀 MLOps - Sistema de Recomendaciones

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-ECR%20%7C%20ECS-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org/)

> **Sistema completo de MLOps para recomendaciones de productos usando filtrado colaborativo**

## 🎯 Demo en Vivo

- **📖 Documentación Completa**: [Ver README](README.md)
- **🐳 Guía Docker**: [Docker Guide](DOCKER_GUIDE.md)
- **🤝 Contribuir**: [Contributing Guide](CONTRIBUTING.md)

## 🚀 Quick Start

```bash
# Clonar repositorio
git clone https://github.com/graciano90210/mlops-recomendaciones.git
cd mlops-recomendaciones

# Ejecutar con Docker
docker build -t mlops-api .
docker run -d --name mlops-api -p 8000:8000 mlops-api

# ¡API disponible en http://localhost:8000!
```

## 🌐 Endpoints Principales

| Endpoint | Descripción |
|----------|-------------|
| `/docs` | Documentación interactiva |
| `/recomendar/{user_id}` | Obtener recomendaciones |
| `/salud` | Health check |

## 🏗️ Arquitectura

```
📦 MLOps Pipeline
├── 🤖 Machine Learning (Collaborative Filtering)
├── 🚀 FastAPI (RESTful API)
├── 🐳 Docker (Containerization)
├── ☁️ AWS ECS/Fargate (Cloud Deployment)
├── 🔄 GitHub Actions (CI/CD)
└── 📊 Monitoring & Logging
```

## 👨‍💻 Autor

**Juan Fernando Graciano**
- 🐙 [GitHub](https://github.com/graciano90210)
- 💼 [LinkedIn](https://linkedin.com/in/juan-fernando-graciano)
- 📧 graciano90210@gmail.com

---

⭐ **¡Dale una estrella si te gusta este proyecto!** ⭐