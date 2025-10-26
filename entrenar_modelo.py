import os
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import col

# --- CONFIGURACIÓN IMPORTANTE ---

# ¡¡CAMBIA ESTO!! Pon el nombre exacto de tu bucket
MI_BUCKET = "mi-proyecto-mlops-juangraciano-25-10-2025" 

# No necesitas tocar esto. Son las librerías mágicas que necesita Spark
# para poder leer y escribir en S3 (s3a) usando tus credenciales de AWS.
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell'

# --- 1. Creación de la Sesión de Spark ---
print("Iniciando sesión de Spark para ENTRENAMIENTO...")

# ¡¡Usamos la MISMA configuración que nos funcionó en el ETL!!
# Incluyendo el arreglo del 'timeout'
spark = SparkSession.builder \
    .appName("Entrenamiento de Modelo ALS") \
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
ruta_gold = f"s3a://{MI_BUCKET}/gold/"
ruta_modelos = f"s3a://{MI_BUCKET}/models/"


# --- 2. Leer los Datos "Dorados" ---
print(f"Leyendo la tabla 'ratings' de la capa Gold...")

try:
    # Leemos la tabla 'ratings' que creamos en el paso anterior
    df_ratings = spark.read.parquet(f"{ruta_gold}ratings/")

    # Spark ML necesita que las columnas se llamen 'user', 'item' y 'rating'
    # Así que vamos a renombrarlas
    df_ratings_als = df_ratings \
        .withColumnRenamed("user_id", "user") \
        .withColumnRenamed("product_id", "item") \
        .withColumn("rating", col("rating").cast("float")) # Nos aseguramos que sea un número flotante

    print("Datos de ratings leídos y preparados:")
    df_ratings_als.printSchema()
    df_ratings_als.show(5)

except Exception as e:
    print(f"Error leyendo de S3. ¿Existe la carpeta 'gold/ratings'?")
    print(f"Error: {e}")
    spark.stop()
    exit()


# --- 3. Entrenamiento del Modelo ALS ---
print("Iniciando entrenamiento del modelo ALS...")

# (Opcional) Dividimos los datos: 80% para entrenar, 20% para probar
(training_data, test_data) = df_ratings_als.randomSplit([0.8, 0.2])

# Creamos la "receta" de nuestro modelo
# maxIter = 5 (cuántas veces "practica" con los datos)
# regParam = 0.01 (una configuración para evitar que "sobre-aprenda")
als = ALS(maxIter=5, regParam=0.01, userCol="user", itemCol="item", ratingCol="rating",
          coldStartStrategy="drop") # "drop" = ignora usuarios nuevos que no conoce

# ¡¡La magia!! Le decimos al modelo que "aprenda" de nuestros datos
# Esto puede tardar un poquito
model = als.fit(training_data)

print("¡Modelo entrenado con éxito!")


# --- 4. Guardar el Modelo Entrenado en S3 ---
print("Guardando el modelo entrenado en S3...")

# Definimos la ruta completa donde se guardará el "cerebro" del modelo
ruta_guardado_modelo = f"{ruta_modelos}modelo_als_v1"

try:
    # Le decimos a Spark que guarde el modelo
    # .write().overwrite() = si ya existía uno, lo reemplaza
    model.write().overwrite().save(ruta_guardado_modelo)

    print(f"¡Modelo guardado exitosamente en: {ruta_guardado_modelo}")
    
except Exception as e:
    print(f"Error guardando el modelo: {e}")


# --- 5. Finalizar Sesión ---
print("¡Proceso de entrenamiento finalizado!")
spark.stop()