import os
from fastapi import FastAPI
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
import uvicorn

# --- CONFIGURACIÓN IMPORTANTE ---

# ¡¡CAMBIA ESTO!! Pon el nombre exacto de tu bucket
MI_BUCKET = "mi-proyecto-mlops-juangraciano-25-10-2025" 

# No necesitas tocar esto. Son las librerías mágicas que necesita Spark
# para poder leer y escribir en S3 (s3a) usando tus credenciales de AWS.
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell'

# --- 1. Inicialización de la App y Spark ---

print("Iniciando API de Recomendación...")
app = FastAPI(title="API de Recomendación MLOps")

print("Iniciando sesión de Spark para la API...")
# ¡¡Usamos la MISMA configuración que nos funcionó!!
spark = SparkSession.builder \
    .appName("API de Recomendación ALS") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.block.size", "134217728") \
    .config("spark.hadoop.fs.s3a.multipart.size", "67108864") \
    .config("spark.hadoop.fs.s3a.fast.upload", "true") \
    .config("spark.hadoop.fs.s3a.fast.upload.buffer", "bytebuffer") \
    .config("spark.hadoop.fs.s3a.threads.max", "10") \
    .config("spark.hadoop.fs.s3a.threads.core", "5") \
    .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60") \
    .config("spark.hadoop.fs.s3a.max.total.tasks", "1000") \
    .config("spark.hadoop.fs.s3a.connection.maximum", "20") \
    .config("spark.hadoop.fs.s3a.connection.timeout", "200000") \
    .config("spark.hadoop.fs.s3a.connection.establish.timeout", "5000") \
    .config("spark.hadoop.fs.s3a.attempts.maximum", "3") \
    .config("spark.hadoop.fs.s3a.retry.interval", "500") \
    .config("spark.hadoop.fs.s3a.retry.limit", "5") \
    .config("spark.hadoop.fs.s3a.multipart.purge.age", "86400") \
    .config("spark.hadoop.fs.s3a.socket.send.buffer", "8192") \
    .config("spark.hadoop.fs.s3a.socket.recv.buffer", "8192") \
    .config("spark.hadoop.io.native.lib.available", "false") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

print("¡Sesión de Spark creada con éxito!")


# --- 2. Cargar el Modelo "Cerebro" desde S3 ---

# Esta es la parte clave: Cargamos el modelo UNA SOLA VEZ cuando la API arranca.
# Así, ya lo tenemos listo en memoria para hacer predicciones rápidas.

ruta_modelo = f"s3a://{MI_BUCKET}/models/modelo_als_v1"
print(f"Cargando modelo desde {ruta_modelo}...")

try:
    # ALSModel.load() es la función para cargar un modelo ALS guardado
    modelo_als = ALSModel.load(ruta_modelo)
    print("¡Modelo ALS cargado y listo para servir!")
except Exception as e:
    print(f"Error fatal: No se pudo cargar el modelo desde S3. {e}")
    # Si no podemos cargar el modelo, la API no sirve de nada.
    # En un caso real, esto debería alertar a un equipo de MLOps.
    modelo_als = None


# --- 3. Definir la "Ventanilla" (Endpoint) ---

# Esto es lo que la gente podrá "llamar" desde internet.
# @app.get(...) significa que es una petición GET.
# "/recomendar/{user_id}" es la URL que podrán usar.
@app.get("/recomendar/{user_id}")
async def recomendar_productos(user_id: int):
    """
    Entrega 5 recomendaciones de productos para un ID de usuario dado.
    """
    if modelo_als is None:
        return {"error": "Modelo no está disponible. Contacte a soporte."}

    try:
        # 1. Spark necesita un DataFrame para predecir.
        # Creamos un DataFrame "ficticio" solo con el usuario que nos piden.
        user_df = spark.createDataFrame([(user_id,)], ["user"])

        # 2. ¡La magia! Le pedimos al modelo las mejores 5 recomendaciones.
        # .recommendForUserSubset() es la función para pedir recomendaciones
        recomendaciones_df = modelo_als.recommendForUserSubset(user_df, 5)

        # 3. El resultado es complicado, así que lo limpiamos para que sea bonito.
        # Usamos .collect() para traer el resultado de Spark a Python
        recomendaciones_list = recomendaciones_df.collect()[0].recommendations
        
        # 4. Extraemos solo los IDs de los productos
        productos_recomendados = [row.item for row in recomendaciones_list]

        # 5. ¡Respondemos!
        return {
            "user_id": user_id,
            "productos_recomendados": productos_recomendados
        }

    except Exception as e:
        # Si el usuario no existe o algo falla
        return {"error": f"No se pudieron generar recomendaciones para el usuario {user_id}. ¿Es un usuario válido? Detalle: {e}"}

# --- 4. Correr el Servidor (Solo si ejecutamos este script directamente) ---
if __name__ == "__main__":
    print("Iniciando servidor Uvicorn en http://127.0.0.1:8000")
    # "api:app" = "El archivo 'api.py', y adentro, la variable 'app'"
    # host="0.0.0.0" = Acepta conexiones desde cualquier IP (importante para Docker)
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)