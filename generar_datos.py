import pandas as pd
from faker import Faker
import random
from datetime import datetime

# Inicializamos Faker
fake = Faker('es_ES') # Usemos datos en español

# --- 1. Generar Usuarios ---
print("Generando usuarios...")
num_usuarios = 100
usuarios_data = []
for i in range(1, num_usuarios + 1):
    usuarios_data.append({
        'user_id': i,
        'nombre': fake.name(),
        'ciudad': fake.city(),
        'email': fake.email(),
        'fecha_registro': fake.date_between(start_date='-2y', end_date='today')
    })

usuarios_df = pd.DataFrame(usuarios_data)
usuarios_df.to_csv('usuarios.csv', index=False)
print(f"-> 'usuarios.csv' creado con {len(usuarios_df)} filas.")


# --- 2. Generar Productos ---
print("Generando productos...")
num_productos = 50
categorias = ['Electrónica', 'Ropa', 'Hogar', 'Juguetes', 'Deportes']
productos_data = []
for i in range(1, num_productos + 1):
    productos_data.append({
        'product_id': 1000 + i, # Empezamos desde 1001
        'nombre_producto': fake.catch_phrase(), # Nombres "creativos"
        'categoria': random.choice(categorias),
        'precio': round(random.uniform(5.99, 500.99), 2)
    })

productos_df = pd.DataFrame(productos_data)
productos_df.to_csv('productos.csv', index=False)
print(f"-> 'productos.csv' creado con {len(productos_df)} filas.")


# --- 3. Generar Interacciones ---
print("Generando interacciones...")
num_interacciones = 5000
tipos_interaccion = ['visto', 'clic', 'agregado_al_carrito', 'compra']
interacciones_data = []

# Creamos listas de IDs para hacer la selección aleatoria más rápido
lista_user_ids = usuarios_df['user_id'].tolist()
lista_product_ids = productos_df['product_id'].tolist()

for _ in range(num_interacciones):
    interacciones_data.append({
        'user_id': random.choice(lista_user_ids),
        'product_id': random.choice(lista_product_ids),
        'timestamp': fake.date_time_between(start_date='-1y', end_date='now'),
        'tipo_interaccion': random.choices(tipos_interaccion, weights=[0.5, 0.3, 0.15, 0.05], k=1)[0] # Damos pesos para que 'visto' sea más común
    })

interacciones_df = pd.DataFrame(interacciones_data)
# Ordenamos por fecha
interacciones_df = interacciones_df.sort_values(by='timestamp')
interacciones_df.to_csv('interacciones.csv', index=False)
print(f"-> 'interacciones.csv' creado con {len(interacciones_df)} filas.")

print("\n¡Listo! Los 3 archivos CSV han sido creados.")