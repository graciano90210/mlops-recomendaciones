import os
import json
from fastapi import FastAPI, HTTPException
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
import uvicorn

# --- CONFIGURACIÓN PARA WINDOWS ---

# ¡¡CAMBIA ESTO!! Pon el nombre exacto de tu bucket
MI_BUCKET = "mi-proyecto-mlops-juangraciano-25-10-2025" 

# Configuración mejorada para Windows
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell'

# --- 1. Inicialización de la App ---

print("🚀 Iniciando API de Recomendación Simplificada...")
app = FastAPI(title="API de Recomendación MLOps", version="2.0")

# Variable global para el modelo y spark
modelo_als = None
spark = None

def inicializar_spark():
    """Inicializa Spark con configuración optimizada para Windows"""
    global spark
    
    print("⚡ Iniciando sesión de Spark optimizada para Windows...")
    
    try:
        spark = SparkSession.builder \
            .appName("API-Recomendacion-Windows") \
            .master("local[1]") \
            .config("spark.sql.adaptive.enabled", "false") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "false") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.fast.upload", "true") \
            .config("spark.hadoop.fs.s3a.fast.upload.buffer", "bytebuffer") \
            .config("spark.hadoop.fs.s3a.connection.timeout", "200000") \
            .config("spark.hadoop.fs.s3a.connection.establish.timeout", "5000") \
            .config("spark.hadoop.fs.s3a.attempts.maximum", "3") \
            .config("spark.hadoop.io.native.lib.available", "false") \
            .config("spark.executor.heartbeatInterval", "20s") \
            .config("spark.network.timeout", "300s") \
            .config("spark.executor.instances", "1") \
            .config("spark.executor.cores", "1") \
            .config("spark.executor.memory", "1g") \
            .config("spark.driver.memory", "1g") \
            .getOrCreate()
        
        # Reducir el nivel de log para menos ruido
        spark.sparkContext.setLogLevel("ERROR")
        print("✅ Sesión de Spark creada correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear sesión de Spark: {e}")
        return False

def cargar_modelo():
    """Carga el modelo ALS desde S3"""
    global modelo_als
    
    if spark is None:
        print("❌ Spark no está inicializado")
        return False
    
    ruta_modelo = f"s3a://{MI_BUCKET}/models/modelo_als_v1"
    print(f"📁 Cargando modelo desde {ruta_modelo}...")
    
    try:
        modelo_als = ALSModel.load(ruta_modelo)
        print("🧠 ¡Modelo ALS cargado correctamente!")
        return True
    except Exception as e:
        print(f"❌ Error al cargar modelo: {e}")
        return False

# --- 2. Eventos de inicio de la aplicación ---

@app.on_event("startup")
async def startup_event():
    """Se ejecuta al iniciar la API"""
    print("🔧 Inicializando componentes...")
    
    if not inicializar_spark():
        raise Exception("No se pudo inicializar Spark")
    
    if not cargar_modelo():
        raise Exception("No se pudo cargar el modelo")
    
    print("🎉 ¡API lista para servir recomendaciones!")

@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta al cerrar la API"""
    global spark
    if spark:
        print("🛑 Cerrando sesión de Spark...")
        spark.stop()

# --- 3. Endpoints de la API ---

@app.get("/")
async def root():
    """Endpoint de verificación"""
    return {
        "mensaje": "API de Recomendación MLOps funcionando",
        "version": "2.0",
        "estado": "activo" if modelo_als else "modelo no cargado"
    }

@app.get("/salud")
async def verificar_salud():
    """Endpoint de salud del sistema"""
    return {
        "spark": "activo" if spark else "inactivo",
        "modelo": "cargado" if modelo_als else "no cargado",
        "bucket": MI_BUCKET
    }

@app.get("/recomendar/{user_id}")
async def recomendar_productos(user_id: int):
    """
    Entrega 5 recomendaciones de productos para un usuario.
    
    Args:
        user_id: ID del usuario (debe estar entre 1 y 100)
    
    Returns:
        JSON con recomendaciones de productos
    """
    
    # Validar que los componentes estén listos
    if spark is None:
        raise HTTPException(status_code=503, detail="Spark no está disponible")
    
    if modelo_als is None:
        raise HTTPException(status_code=503, detail="Modelo no está disponible")
    
    # Validar rango de usuario (asumiendo que tenemos usuarios 1-100)
    if user_id < 1 or user_id > 100:
        raise HTTPException(
            status_code=400, 
            detail=f"Usuario {user_id} fuera del rango válido (1-100)"
        )
    
    try:
        print(f"🔍 Generando recomendaciones para usuario {user_id}...")
        
        # 1. Crear DataFrame con el usuario
        user_df = spark.createDataFrame([(user_id,)], ["user"])
        
        # 2. Generar recomendaciones
        recomendaciones_df = modelo_als.recommendForUserSubset(user_df, 5)
        
        # 3. Verificar que hay recomendaciones
        if recomendaciones_df.count() == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron recomendaciones para el usuario {user_id}"
            )
        
        # 4. Extraer las recomendaciones
        recomendaciones_raw = recomendaciones_df.collect()[0].recommendations
        productos_recomendados = [
            {
                "producto_id": row.item,
                "puntuacion": round(float(row.rating), 3)
            }
            for row in recomendaciones_raw
        ]
        
        print(f"✅ Recomendaciones generadas para usuario {user_id}")
        
        return {
            "user_id": user_id,
            "productos_recomendados": productos_recomendados,
            "total_recomendaciones": len(productos_recomendados)
        }
        
    except HTTPException:
        # Re-lanzar HTTPExceptions 
        raise
    except Exception as e:
        print(f"❌ Error al generar recomendaciones para usuario {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al generar recomendaciones: {str(e)}"
        )

# --- 4. Función principal ---

if __name__ == "__main__":
    print("🌐 Iniciando servidor API...")
    try:
        uvicorn.run(
            "api_simple:app", 
            host="127.0.0.1",  # Solo local para evitar problemas de red en Windows
            port=8000, 
            reload=False,  # Desactivar reload para evitar problemas con Spark
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")