import os
import json
import random
from typing import List, Dict
from fastapi import FastAPI, HTTPException
import uvicorn
import pandas as pd

# --- API SIN SPARK PARA WINDOWS ---

print("🚀 Iniciando API de Recomendación sin Spark...")

app = FastAPI(
    title="API de Recomendación MLOps", 
    version="3.0-NoSpark",
    description="API de recomendaciones usando datos locales (sin Spark)"
)

# Variables globales para datos
usuarios_df = None
productos_df = None
interacciones_df = None

def cargar_datos_locales():
    """Carga los datos CSV locales"""
    global usuarios_df, productos_df, interacciones_df
    
    try:
        print("📁 Cargando datos desde archivos CSV...")
        
        # Cargar usuarios
        usuarios_df = pd.read_csv("usuarios.csv")
        print(f"✅ Usuarios cargados: {len(usuarios_df)} registros")
        
        # Cargar productos  
        productos_df = pd.read_csv("productos.csv")
        print(f"✅ Productos cargados: {len(productos_df)} registros")
        
        # Cargar interacciones
        interacciones_df = pd.read_csv("interacciones.csv")
        print(f"✅ Interacciones cargadas: {len(interacciones_df)} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return False

def generar_recomendaciones_colaborativas(user_id: int, num_recomendaciones: int = 5) -> List[Dict]:
    """
    Genera recomendaciones usando filtrado colaborativo simple
    """
    try:
        # 1. Obtener productos que el usuario ya ha comprado/interactuado
        productos_usuario = set(
            interacciones_df[interacciones_df['user_id'] == user_id]['product_id'].tolist()
        )
        
        # 2. Encontrar usuarios similares (que compraron productos similares)
        usuarios_similares = []
        for _, row in interacciones_df.iterrows():
            if row['user_id'] != user_id and row['product_id'] in productos_usuario:
                usuarios_similares.append(row['user_id'])
        
        # 3. Obtener productos comprados por usuarios similares
        if usuarios_similares:
            productos_recomendados = set()
            for similar_user in set(usuarios_similares):
                productos_similar = interacciones_df[
                    interacciones_df['user_id'] == similar_user
                ]['product_id'].tolist()
                productos_recomendados.update(productos_similar)
            
            # 4. Remover productos que el usuario ya tiene
            productos_recomendados = productos_recomendados - productos_usuario
        else:
            # Si no hay usuarios similares, usar productos populares
            productos_populares = interacciones_df['product_id'].value_counts()
            productos_recomendados = set(productos_populares.head(20).index.tolist())
            productos_recomendados = productos_recomendados - productos_usuario
        
        # 5. Seleccionar recomendaciones finales
        productos_finales = list(productos_recomendados)[:num_recomendaciones]
        
        # 6. Si no hay suficientes, completar con productos aleatorios
        if len(productos_finales) < num_recomendaciones:
            todos_productos = set(productos_df['product_id'].tolist())
            productos_restantes = todos_productos - productos_usuario - set(productos_finales)
            productos_adicionales = random.sample(
                list(productos_restantes), 
                min(num_recomendaciones - len(productos_finales), len(productos_restantes))
            )
            productos_finales.extend(productos_adicionales)
        
        # 7. Crear respuesta con puntuaciones simuladas
        recomendaciones = []
        for i, producto_id in enumerate(productos_finales):
            # Simular puntuación decreciente
            score = round(5.0 - (i * 0.3), 2)
            recomendaciones.append({
                "producto_id": int(producto_id),
                "puntuacion": max(score, 1.0),  # Mínimo 1.0
                "metodo": "colaborativo" if usuarios_similares else "popular"
            })
        
        return recomendaciones
        
    except Exception as e:
        print(f"❌ Error generando recomendaciones: {e}")
        return []

# --- ENDPOINTS ---

@app.get("/")
async def root():
    """Endpoint de verificación"""
    return {
        "mensaje": "API de Recomendación MLOps (sin Spark)",
        "version": "3.0-NoSpark",
        "estado": "activo",
        "datos_disponibles": {
            "usuarios": len(usuarios_df) if usuarios_df is not None else 0,
            "productos": len(productos_df) if productos_df is not None else 0,
            "interacciones": len(interacciones_df) if interacciones_df is not None else 0
        }
    }

@app.get("/salud")
async def verificar_salud():
    """Endpoint de salud del sistema"""
    return {
        "estado": "saludable",
        "spark": "no requerido",
        "datos": "cargados" if usuarios_df is not None else "no cargados",
        "metodo": "filtrado colaborativo + popularidad"
    }

@app.get("/usuarios")
async def listar_usuarios():
    """Lista información básica de usuarios disponibles"""
    if usuarios_df is None:
        raise HTTPException(status_code=503, detail="Datos no disponibles")
    
    return {
        "total_usuarios": len(usuarios_df),
        "rango_ids": f"1-{len(usuarios_df)}",
        "usuarios_muestra": usuarios_df.head(5).to_dict('records')
    }

@app.get("/productos")
async def listar_productos():
    """Lista información básica de productos disponibles"""
    if productos_df is None:
        raise HTTPException(status_code=503, detail="Datos no disponibles")
    
    return {
        "total_productos": len(productos_df),
        "productos_muestra": productos_df.head(10).to_dict('records')
    }

@app.get("/usuario/{user_id}/historial")
async def obtener_historial_usuario(user_id: int):
    """Obtiene el historial de interacciones de un usuario"""
    if interacciones_df is None:
        raise HTTPException(status_code=503, detail="Datos no disponibles")
    
    # Validar usuario
    if user_id < 1 or user_id > len(usuarios_df):
        raise HTTPException(
            status_code=404, 
            detail=f"Usuario {user_id} no encontrado. Rango válido: 1-{len(usuarios_df)}"
        )
    
    # Obtener historial
    historial = interacciones_df[interacciones_df['user_id'] == user_id]
    
    if len(historial) == 0:
        return {
            "user_id": user_id,
            "mensaje": "Usuario sin historial de interacciones",
            "total_interacciones": 0,
            "productos": []
        }
    
    # Agregar información de productos
    historial_detallado = []
    for _, row in historial.iterrows():
        producto_info = productos_df[productos_df['product_id'] == row['product_id']]
        if not producto_info.empty:
            historial_detallado.append({
                "producto_id": int(row['product_id']),
                "nombre_producto": producto_info.iloc[0]['nombre_producto'],
                "categoria": producto_info.iloc[0]['categoria'],
                "tipo_interaccion": row['tipo_interaccion'],
                "timestamp": row['timestamp']
            })
    
    return {
        "user_id": user_id,
        "total_interacciones": len(historial_detallado),
        "productos": historial_detallado
    }

@app.get("/recomendar/{user_id}")
async def recomendar_productos(user_id: int):
    """
    Genera 5 recomendaciones para un usuario usando filtrado colaborativo
    """
    
    # Verificar que los datos estén cargados
    if usuarios_df is None or productos_df is None or interacciones_df is None:
        raise HTTPException(status_code=503, detail="Datos no disponibles")
    
    # Validar rango de usuario
    if user_id < 1 or user_id > len(usuarios_df):
        raise HTTPException(
            status_code=404, 
            detail=f"Usuario {user_id} no encontrado. Rango válido: 1-{len(usuarios_df)}"
        )
    
    try:
        print(f"🔍 Generando recomendaciones para usuario {user_id}...")
        
        # Generar recomendaciones
        recomendaciones = generar_recomendaciones_colaborativas(user_id, 5)
        
        if not recomendaciones:
            raise HTTPException(
                status_code=500,
                detail="No se pudieron generar recomendaciones"
            )
        
        # Agregar información de productos recomendados
        recomendaciones_detalladas = []
        for rec in recomendaciones:
            producto_info = productos_df[productos_df['product_id'] == rec['producto_id']]
            if not producto_info.empty:
                producto = producto_info.iloc[0]
                recomendaciones_detalladas.append({
                    "producto_id": rec['producto_id'],
                    "nombre": producto['nombre_producto'],
                    "categoria": producto['categoria'],
                    "precio": f"${producto['precio']:.2f}",
                    "puntuacion": rec['puntuacion'],
                    "metodo": rec['metodo']
                })
        
        print(f"✅ {len(recomendaciones_detalladas)} recomendaciones generadas para usuario {user_id}")
        
        return {
            "user_id": user_id,
            "total_recomendaciones": len(recomendaciones_detalladas),
            "recomendaciones": recomendaciones_detalladas,
            "metodo": "filtrado_colaborativo + popularidad",
            "algoritmo": "sin_spark"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

# --- INICIALIZACIÓN ---

@app.on_event("startup")
async def startup_event():
    """Carga los datos al iniciar la API"""
    print("🔧 Inicializando API sin Spark...")
    
    if not cargar_datos_locales():
        raise Exception("No se pudieron cargar los datos locales")
    
    print("🎉 ¡API lista para servir recomendaciones!")

# --- FUNCIÓN PRINCIPAL ---

if __name__ == "__main__":
    print("🌐 Iniciando servidor API sin Spark...")
    try:
        # Configuración para Docker (0.0.0.0 para aceptar conexiones externas)
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", 8000))
        
        print(f"🚀 Servidor iniciando en {host}:{port}")
        
        uvicorn.run(
            "api_nospark:app", 
            host=host,
            port=port, 
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")