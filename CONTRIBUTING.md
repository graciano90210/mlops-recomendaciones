# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir al proyecto MLOps de Recomendaciones! 🎉

## 📋 **Índice**

- [🚀 Primeros Pasos](#-primeros-pasos)
- [🔧 Configuración del Entorno](#-configuración-del-entorno)
- [🌿 Workflow de Contribución](#-workflow-de-contribución)
- [📝 Estándares de Código](#-estándares-de-código)
- [🧪 Testing](#-testing)
- [📚 Documentación](#-documentación)
- [🐳 Docker](#-docker)
- [🚫 Qué NO hacer](#-qué-no-hacer)

## 🚀 **Primeros Pasos**

### Tipos de Contribuciones Bienvenidas

- 🐛 **Bug fixes**: Corrección de errores
- ✨ **Features**: Nuevas funcionalidades
- 📚 **Documentación**: Mejoras en docs
- 🧪 **Tests**: Nuevas pruebas o mejoras
- 🎨 **Refactoring**: Mejoras de código
- 🔧 **Configuración**: DevOps y deployment

### Antes de Empezar

1. **Fork** el repositorio
2. **Crear issue** para discutir cambios grandes
3. **Revisar** issues existentes para evitar duplicados
4. **Leer** esta guía completamente

## 🔧 **Configuración del Entorno**

### Requisitos

- Python 3.11+
- Docker Desktop
- Git
- VS Code (recomendado)

### Setup Local

```bash
# 1. Clonar tu fork
git clone https://github.com/TU-USUARIO/mlops-recomendaciones.git
cd mlops-recomendaciones

# 2. Agregar upstream
git remote add upstream https://github.com/REPO-ORIGINAL/mlops-recomendaciones.git

# 3. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar instalación
python test_pipeline.py
```

### Setup con Docker

```bash
# Construir imagen
docker build -t mlops-api .

# Ejecutar contenedor
docker run -d --name mlops-dev -p 8000:8000 mlops-api

# Verificar
curl http://localhost:8000/salud
```

## 🌿 **Workflow de Contribución**

### 1. Preparar Rama

```bash
# Sincronizar con upstream
git fetch upstream
git checkout main
git merge upstream/main

# Crear rama feature
git checkout -b feature/descripcion-corta
```

### 2. Desarrollar

```bash
# Hacer cambios
# ... edit files ...

# Probar localmente
python test_pipeline.py
python api_nospark.py  # Verificar API

# Commit incremental
git add .
git commit -m "feat: agregar nueva funcionalidad X"
```

### 3. Testing

```bash
# Tests unitarios
python test_pipeline.py

# Test API completo
python analizador_recomendaciones.py

# Test Docker
docker build -t test-image .
docker run -d --name test-api -p 8001:8000 test-image
curl http://localhost:8001/salud
docker stop test-api && docker rm test-api
```

### 4. Preparar PR

```bash
# Push a tu fork
git push origin feature/descripcion-corta

# Crear PR desde GitHub
# Incluir descripción detallada
```

## 📝 **Estándares de Código**

### Python Style Guide

```python
# ✅ BIEN - Docstrings descriptivos
def calcular_similitud(usuario_a: int, usuario_b: int) -> float:
    """
    Calcula similitud entre dos usuarios usando correlación de Pearson.
    
    Args:
        usuario_a: ID del primer usuario
        usuario_b: ID del segundo usuario
        
    Returns:
        float: Coeficiente de similitud [-1, 1]
        
    Raises:
        ValueError: Si los usuarios no existen
    """
    # Implementation here
    pass

# ✅ BIEN - Type hints
from typing import List, Dict, Optional

def obtener_recomendaciones(
    user_id: int, 
    num_recomendaciones: int = 5
) -> List[Dict[str, Any]]:
    pass

# ✅ BIEN - Nombres descriptivos
usuarios_similares = encontrar_usuarios_similares(user_id)
productos_candidatos = filtrar_productos_no_vistos(user_id)
```

### Estructura de Archivos

```python
# ✅ BIEN - Estructura de archivo Python
"""
Módulo para el sistema de recomendaciones colaborativas.

Este módulo implementa algoritmos de filtrado colaborativo
para generar recomendaciones personalizadas.
"""

# Standard library imports
import logging
from typing import List, Dict, Any

# Third-party imports
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException

# Local imports
from .utils import load_data
from .models import RecommendationModel

# Constants
DEFAULT_RECOMMENDATIONS = 5
SIMILARITY_THRESHOLD = 0.1

# Code here...
```

### Mensajes de Commit

```bash
# ✅ BIEN - Formato convencional
feat: agregar endpoint para historial de usuario
fix: corregir cálculo de similitud para usuarios sin datos
docs: actualizar README con instrucciones Docker
test: agregar tests para casos edge del algoritmo
refactor: optimizar función de filtrado colaborativo
chore: actualizar dependencias a versiones seguras

# ❌ MAL - Mensajes poco descriptivos
fix: bug
update: changes
wip: stuff
```

## 🧪 **Testing**

### Tests Obligatorios

```python
# test_contribution.py - Ejemplo de test
def test_nueva_funcionalidad():
    """Test para la nueva funcionalidad agregada."""
    # Setup
    user_id = 40
    expected_recommendations = 5
    
    # Execute
    result = obtener_recomendaciones(user_id)
    
    # Assert
    assert len(result) == expected_recommendations
    assert all('producto_id' in rec for rec in result)
    assert all('puntuacion' in rec for rec in result)

def test_edge_case_usuario_sin_historial():
    """Test para usuario sin historial de interacciones."""
    user_id = 999  # Usuario que no existe
    
    with pytest.raises(HTTPException) as exc_info:
        obtener_recomendaciones(user_id)
    
    assert exc_info.value.status_code == 404
```

### Coverage Mínimo

- **Nuevas funciones**: 100% coverage
- **Funciones modificadas**: Mantener coverage existente
- **Tests de integración**: Para endpoints API

## 📚 **Documentación**

### README Updates

Si tu contribución afecta:

- **API**: Actualizar sección de endpoints
- **Docker**: Actualizar instrucciones de build
- **Algoritmo**: Actualizar sección técnica
- **Configuración**: Actualizar variables de entorno

### Docstrings

```python
# ✅ BIEN - Docstring completo
def generar_recomendaciones_hibridas(
    user_id: int,
    weight_collaborative: float = 0.7,
    weight_content: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Genera recomendaciones usando enfoque híbrido.
    
    Combina filtrado colaborativo y basado en contenido
    con pesos configurables para optimizar resultados.
    
    Args:
        user_id: Identificador único del usuario
        weight_collaborative: Peso para filtrado colaborativo [0-1]
        weight_content: Peso para filtrado por contenido [0-1]
        
    Returns:
        Lista de diccionarios con recomendaciones ordenadas por score:
        [
            {
                'producto_id': int,
                'nombre': str,
                'categoria': str,
                'puntuacion': float,
                'metodo': str
            }
        ]
        
    Raises:
        ValueError: Si los pesos no suman 1.0
        HTTPException: Si el usuario no existe (404)
        
    Example:
        >>> recomendaciones = generar_recomendaciones_hibridas(
        ...     user_id=40,
        ...     weight_collaborative=0.8,
        ...     weight_content=0.2
        ... )
        >>> len(recomendaciones)
        5
        >>> recomendaciones[0]['puntuacion'] >= recomendaciones[1]['puntuacion']
        True
    """
```

## 🐳 **Docker**

### Dockerfile Changes

Si modificas `Dockerfile`:

```dockerfile
# ✅ BIEN - Comentarios explicativos
# Install security updates
RUN apt-get update && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ BIEN - Multi-stage builds
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

### Testing Docker

```bash
# Antes de commit, verificar:
docker build -t test-image .
docker run --rm test-image python test_pipeline.py
```

## 🚫 **Qué NO hacer**

### ❌ Código

```python
# ❌ MAL - Sin type hints
def obtener_datos(usuario):
    return algo

# ❌ MAL - Magic numbers
if similarity > 0.342857:
    # Sin explicación del threshold

# ❌ MAL - Variables crípticas
u = get_u(uid)
r = calc_r(u, p)
```

### ❌ Git

```bash
# ❌ MAL - Commits gigantes
git add .
git commit -m "fix everything"

# ❌ MAL - Pushear directamente a main
git checkout main
git commit -m "hotfix"
git push origin main
```

### ❌ Docker

```dockerfile
# ❌ MAL - Instalar como root
USER root
RUN pip install pandas

# ❌ MAL - Secrets en imagen
ENV AWS_SECRET_KEY=actual-secret-key
```

## 🎯 **Checklist Pre-PR**

Antes de abrir el Pull Request, verifica:

- [ ] ✅ **Tests**: Todos los tests pasan
- [ ] ✅ **Linting**: Código sigue estándares
- [ ] ✅ **Documentation**: README actualizado si es necesario
- [ ] ✅ **Docker**: Imagen construye correctamente
- [ ] ✅ **Commits**: Mensajes descriptivos
- [ ] ✅ **Branch**: Actualizada con upstream/main
- [ ] ✅ **Testing**: Funcionalidad probada localmente

## 🏆 **Proceso de Review**

### Lo que Revisamos

1. **Funcionalidad**: ¿Hace lo que dice?
2. **Performance**: ¿Impacta negativamente?
3. **Security**: ¿Introduce vulnerabilidades?
4. **Mantenibilidad**: ¿Es fácil de mantener?
5. **Testing**: ¿Está bien probado?

### Tiempos Esperados

- **Reviews simples**: 1-2 días
- **Features complejas**: 3-5 días
- **Cambios arquitecturales**: 1 semana

### Después del Review

- **Responder feedback**: Clarificar dudas
- **Hacer cambios**: En la misma rama
- **Re-request review**: Después de cambios

## 🎉 **¡Gracias por Contribuir!**

Tu contribución hace que este proyecto sea mejor para toda la comunidad MLOps. 

¿Preguntas? Abre un **issue** con la etiqueta `question` 💭

---

**Happy Coding!** 🚀