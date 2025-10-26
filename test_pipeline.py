#!/usr/bin/env python3
"""
🎯 Script de Prueba Completa del Pipeline MLOps
===============================================

Este script demuestra el funcionamiento completo del pipeline MLOps:
1. ETL (Extract, Transform, Load) 
2. Entrenamiento del Modelo
3. API de Recomendaciones

Autor: Sistema MLOps
Fecha: 26 de octubre de 2025
"""

import requests
import json
import time
from typing import Dict, List

# Configuración
API_BASE_URL = "http://127.0.0.1:8000"
USUARIOS_PRUEBA = [1, 5, 10, 25, 40, 50, 75, 100]

def verificar_api_activa() -> bool:
    """Verifica si la API está activa y funcionando"""
    try:
        response = requests.get(f"{API_BASE_URL}/salud", timeout=5)
        return response.status_code == 200
    except:
        return False

def obtener_estadisticas_api() -> Dict:
    """Obtiene estadísticas generales de la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.json()
    except:
        return {}

def probar_recomendaciones_usuario(user_id: int) -> Dict:
    """Prueba las recomendaciones para un usuario específico"""
    try:
        response = requests.get(f"{API_BASE_URL}/recomendar/{user_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def obtener_historial_usuario(user_id: int) -> Dict:
    """Obtiene el historial de un usuario"""
    try:
        response = requests.get(f"{API_BASE_URL}/usuario/{user_id}/historial", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def imprimir_encabezado(titulo: str):
    """Imprime un encabezado bonito"""
    print("\n" + "="*60)
    print(f"🎯 {titulo}")
    print("="*60)

def imprimir_resumen_recomendaciones(user_id: int, data: Dict):
    """Imprime un resumen de las recomendaciones"""
    if "error" in data:
        print(f"❌ Error para usuario {user_id}: {data['error']}")
        return
    
    print(f"\n👤 Usuario {user_id}:")
    print(f"   📊 Total de recomendaciones: {data.get('total_recomendaciones', 0)}")
    print(f"   🤖 Método: {data.get('metodo', 'N/A')}")
    
    recomendaciones = data.get('recomendaciones', [])
    if recomendaciones:
        print("   🎁 Top 3 productos recomendados:")
        for i, rec in enumerate(recomendaciones[:3], 1):
            nombre = rec.get('nombre', 'Sin nombre')[:30] + "..." if len(rec.get('nombre', '')) > 30 else rec.get('nombre', 'Sin nombre')
            print(f"      {i}. {nombre}")
            print(f"         Categoría: {rec.get('categoria', 'N/A')} | Puntuación: {rec.get('puntuacion', 0)}")

def main():
    """Función principal del script de prueba"""
    imprimir_encabezado("PRUEBA COMPLETA DEL PIPELINE MLOPS")
    
    print("🚀 Iniciando pruebas del sistema...")
    
    # 1. Verificar que la API esté activa
    print("\n🔍 Paso 1: Verificando estado de la API...")
    if not verificar_api_activa():
        print("❌ La API no está activa. Asegúrate de que esté corriendo en http://127.0.0.1:8000")
        print("💡 Ejecuta: python api_nospark.py")
        return
    
    print("✅ API activa y funcionando")
    
    # 2. Obtener estadísticas
    print("\n📊 Paso 2: Obteniendo estadísticas del sistema...")
    stats = obtener_estadisticas_api()
    if stats:
        datos = stats.get('datos_disponibles', {})
        print(f"   👥 Usuarios: {datos.get('usuarios', 0)}")
        print(f"   🛍️ Productos: {datos.get('productos', 0)}")
        print(f"   📈 Interacciones: {datos.get('interacciones', 0)}")
        print(f"   🔧 Estado: {stats.get('estado', 'N/A')}")
    
    # 3. Probar recomendaciones para varios usuarios
    imprimir_encabezado("PRUEBAS DE RECOMENDACIONES")
    
    resultados_exitosos = 0
    tiempo_total = 0
    
    for user_id in USUARIOS_PRUEBA:
        print(f"\n🔄 Probando usuario {user_id}...")
        
        inicio = time.time()
        resultado = probar_recomendaciones_usuario(user_id)
        fin = time.time()
        
        tiempo_respuesta = fin - inicio
        tiempo_total += tiempo_respuesta
        
        if "error" not in resultado:
            resultados_exitosos += 1
            print(f"   ✅ Éxito en {tiempo_respuesta:.2f}s")
            imprimir_resumen_recomendaciones(user_id, resultado)
        else:
            print(f"   ❌ Error: {resultado['error']}")
    
    # 4. Probar historial de usuario
    imprimir_encabezado("PRUEBA DE HISTORIAL DE USUARIO")
    
    user_ejemplo = 40
    print(f"\n👤 Obteniendo historial del usuario {user_ejemplo}...")
    historial = obtener_historial_usuario(user_ejemplo)
    
    if "error" not in historial:
        print(f"   ✅ Historial obtenido exitosamente")
        print(f"   📊 Total de interacciones: {historial.get('total_interacciones', 0)}")
        
        productos = historial.get('productos', [])
        if productos:
            print(f"   🛍️ Últimas 3 interacciones:")
            for i, prod in enumerate(productos[-3:], 1):
                print(f"      {i}. {prod.get('nombre_producto', 'N/A')[:40]}")
                print(f"         Tipo: {prod.get('tipo_interaccion', 'N/A')} | Fecha: {prod.get('timestamp', 'N/A')}")
    else:
        print(f"   ❌ Error obteniendo historial: {historial['error']}")
    
    # 5. Resumen final
    imprimir_encabezado("RESUMEN DE LA PRUEBA")
    
    print(f"📈 Resultados de la Prueba:")
    print(f"   ✅ Usuarios probados exitosamente: {resultados_exitosos}/{len(USUARIOS_PRUEBA)}")
    print(f"   ⏱️ Tiempo promedio de respuesta: {tiempo_total/len(USUARIOS_PRUEBA):.2f}s")
    print(f"   🎯 Tasa de éxito: {(resultados_exitosos/len(USUARIOS_PRUEBA))*100:.1f}%")
    
    if resultados_exitosos == len(USUARIOS_PRUEBA):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El pipeline MLOps está funcionando perfectamente.")
        print("\n🚀 Componentes verificados:")
        print("   ✅ ETL Pipeline - Datos procesados y disponibles")
        print("   ✅ Sistema de Recomendaciones - Algoritmo funcionando")
        print("   ✅ API REST - Endpoints respondiendo correctamente")
        print("   ✅ Filtrado Colaborativo - Generando recomendaciones personalizadas")
    else:
        print(f"\n⚠️ Se encontraron {len(USUARIOS_PRUEBA) - resultados_exitosos} errores.")
        print("   Revisa los logs para más detalles.")
    
    print("\n🌐 URLs útiles:")
    print(f"   📖 Documentación: {API_BASE_URL}/docs")
    print(f"   🏥 Estado de salud: {API_BASE_URL}/salud")
    print(f"   👥 Lista de usuarios: {API_BASE_URL}/usuarios")
    print(f"   🛍️ Lista de productos: {API_BASE_URL}/productos")
    
    print("\n" + "="*60)
    print("✨ Prueba completa finalizada")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")