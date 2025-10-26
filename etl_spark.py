import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lit
from pyspark.sql.types import IntegerType, DoubleType, TimestampType

# --- CONFIGURACIÓN IMPORTANTE ---

# ¡¡CAMBIA ESTO!! Pon el nombre exacto de tu bucket
MI_BUCKET = "mi-proyecto-mlops-juangraciano-25-10-2025" 

# No necesitas tocar esto. Son las librerías mágicas que necesita Spark
# para poder leer y escribir en S3 (s3a) usando tus credenciales de AWS.
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell'

# --- 1. Creación de la Sesión de Spark ---
print("Iniciando sesión de Spark...")

# Aquí estamos configurando Spark para que use las credenciales
# que guardaste con 'aws configure'.
spark = SparkSession.builder \
    .appName("ETL E-Commerce MLOps") \
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

# Definimos las rutas de nuestro Data Lake
ruta_bronze = f"s3a://{MI_BUCKET}/bronze/"
ruta_silver = f"s3a://{MI_BUCKET}/silver/"
ruta_gold = f"s3a://{MI_BUCKET}/gold/"


# --- 2. PROCESO BRONZE -> SILVER ---
print(f"Iniciando ETL de Bronze a Silver...")

# Leemos nuestros 3 archivos CSV crudos desde S3
try:
    df_usuarios = spark.read.csv(f"{ruta_bronze}usuarios.csv", header=True, inferSchema=True)
    df_productos = spark.read.csv(f"{ruta_bronze}productos.csv", header=True, inferSchema=True)
    df_interacciones = spark.read.csv(f"{ruta_bronze}interacciones.csv", header=True, inferSchema=True)

    print("Datos leídos de la capa Bronze:")
    df_usuarios.printSchema()
    df_productos.printSchema()
    df_interacciones.printSchema()

except Exception as e:
    print(f"Error leyendo de S3. ¿Están los archivos en la carpeta 'bronze'?")
    print(f"Error: {e}")
    spark.stop()
    exit()


# ---- Transformación (Limpieza) ----
# Aquí es donde haríamos la limpieza. Nuestros datos ficticios
# ya están limpios, pero vamos a hacer las conversiones de tipos
# de datos para asegurarnos (¡buena práctica!)

# Convertir tipos de datos de productos
df_productos_silver = df_productos \
    .withColumn("product_id", col("product_id").cast(IntegerType())) \
    .withColumn("precio", col("precio").cast(DoubleType()))

# Convertir tipos de datos de usuarios
df_usuarios_silver = df_usuarios \
    .withColumn("user_id", col("user_id").cast(IntegerType())) \
    .withColumn("fecha_registro", col("fecha_registro").cast(TimestampType()))

# Convertir tipos de datos de interacciones
df_interacciones_silver = df_interacciones \
    .withColumn("user_id", col("user_id").cast(IntegerType())) \
    .withColumn("product_id", col("product_id").cast(IntegerType())) \
    .withColumn("timestamp", col("timestamp").cast(TimestampType()))

# ---- Escritura en Silver ----
# Guardamos los datos limpios en formato Parquet.
# Parquet es mucho más rápido y eficiente que CSV.
print("Guardando datos limpios en capa Silver (Formato Parquet)...")
df_usuarios_silver.write.mode("overwrite").parquet(f"{ruta_silver}usuarios/")
df_productos_silver.write.mode("overwrite").parquet(f"{ruta_silver}productos/")
df_interacciones_silver.write.mode("overwrite").parquet(f"{ruta_silver}interacciones/")

print("¡Capa Silver completada!")


# --- 3. PROCESO SILVER -> GOLD ---
print("Iniciando ETL de Silver a Gold...")

# Ahora que los datos están limpios (en Parquet), los leemos de Silver
df_interacciones_limpias = spark.read.parquet(f"{ruta_silver}interacciones/")
df_productos_limpios = spark.read.parquet(f"{ruta_silver}productos/")

# ---- Creación de "Features" para ML ----
# Esta es la parte más importante para Data Science.
# Vamos a crear 2 tablas "Gold" (listas para el modelo):

# Tabla 1: "user_features"
# Crearemos un "puntaje" simple para cada usuario basado en sus interacciones
# (compra=4, carrito=3, clic=2, visto=1)
from pyspark.sql.functions import when

df_puntajes = df_interacciones_limpias.withColumn("puntaje",
    when(col("tipo_interaccion") == "compra", 4)
    .when(col("tipo_interaccion") == "agregado_al_carrito", 3)
    .when(col("tipo_interaccion") == "clic", 2)
    .otherwise(1)
)

# Agrupamos por usuario y producto, y sumamos los puntajes
df_rating = df_puntajes.groupBy("user_id", "product_id") \
    .sum("puntaje") \
    .withColumnRenamed("sum(puntaje)", "rating")

print("Tabla 'ratings' (user_id, product_id, rating) creada.")
df_rating.show(5)

# Tabla 2: "product_features"
# Vamos a unir las interacciones con las categorías de productos
# para saber qué categorías ve o compra cada usuario.
df_interacciones_categoria = df_interacciones_limpias \
    .join(df_productos_limpios, "product_id") \
    .select("user_id", "categoria", "tipo_interaccion")

print("Tabla 'interacciones_categoria' creada.")
df_interacciones_categoria.show(5)

# ---- Escritura en Gold ----
print("Guardando tablas agregadas en capa Gold (Formato Parquet)...")

# Guardamos nuestras dos tablas de features
df_rating.write.mode("overwrite").parquet(f"{ruta_gold}ratings/")
df_interacciones_categoria.write.mode("overwrite").parquet(f"{ruta_gold}interacciones_categoria/")

print("¡Capa Gold completada!")
print("¡Proceso ETL de Spark finalizado con éxito!")

# --- 4. Finalizar Sesión ---
spark.stop()