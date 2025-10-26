#!/usr/bin/env python3
"""
🔍 ANALIZADOR DE RECOMENDACIONES MLOps
====================================

Este script te ayuda a interpretar las recomendaciones de forma práctica.
"""

import requests
import json

def analizar_recomendaciones(user_id: int):
    """Analiza y explica las recomendaciones para un usuario"""
    
    try:
        # Obtener recomendaciones
        response = requests.get(f"http://127.0.0.1:8000/recomendar/{user_id}")
        if response.status_code != 200:
            print(f"❌ Error obteniendo recomendaciones: {response.status_code}")
            return
        
        data = response.json()
        
        # Obtener historial para contexto
        hist_response = requests.get(f"http://127.0.0.1:8000/usuario/{user_id}/historial")
        historial = hist_response.json() if hist_response.status_code == 200 else {}
        
        print("="*70)
        print(f"🎯 ANÁLISIS DE RECOMENDACIONES PARA USUARIO {user_id}")
        print("="*70)
        
        # Contexto del usuario
        total_interacciones = historial.get('total_interacciones', 0)
        print(f"\n📊 CONTEXTO DEL USUARIO:")
        print(f"   👤 ID del Usuario: {user_id}")
        print(f"   📈 Total de interacciones: {total_interacciones}")
        
        if total_interacciones > 0:
            productos_hist = historial.get('productos', [])
            categorias_hist = {}
            for prod in productos_hist:
                cat = prod.get('categoria', 'Sin categoría')
                categorias_hist[cat] = categorias_hist.get(cat, 0) + 1
            
            print(f"   🎯 Categorías de interés:")
            for cat, count in sorted(categorias_hist.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"      • {cat}: {count} interacciones")
        
        # Análisis de recomendaciones
        recomendaciones = data.get('recomendaciones', [])
        metodo_general = data.get('metodo', 'N/A')
        
        print(f"\n🤖 MÉTODO GENERAL: {metodo_general}")
        print(f"📦 TOTAL DE RECOMENDACIONES: {len(recomendaciones)}")
        
        print(f"\n🔍 ANÁLISIS DETALLADO:")
        print("-" * 70)
        
        for i, rec in enumerate(recomendaciones, 1):
            nombre = rec.get('nombre', 'Sin nombre')
            categoria = rec.get('categoria', 'Sin categoría')
            puntuacion = rec.get('puntuacion', 0)
            metodo = rec.get('metodo', 'N/A')
            precio = rec.get('precio', 'N/A')
            
            # Interpretar puntuación
            if puntuacion >= 4.8:
                nivel = "🥇 EXCELENTE"
                confianza = "MUY ALTA"
            elif puntuacion >= 4.4:
                nivel = "🥈 BUENA"
                confianza = "ALTA"
            elif puntuacion >= 3.0:
                nivel = "🥉 MODERADA"
                confianza = "MEDIA"
            else:
                nivel = "📊 BÁSICA"
                confianza = "BAJA"
            
            # Interpretar método
            if metodo == "colaborativo":
                explicacion_metodo = "Basado en usuarios similares a ti"
                personalizado = "✨ PERSONALIZADO"
            else:
                explicacion_metodo = "Basado en popularidad general"
                personalizado = "📈 GENÉRICO"
            
            print(f"\n#{i} - {nombre[:40]}{'...' if len(nombre) > 40 else ''}")
            print(f"     📊 Puntuación: {puntuacion} ({nivel})")
            print(f"     🎯 Confianza: {confianza}")
            print(f"     🏷️ Categoría: {categoria}")
            print(f"     💰 Precio: {precio}")
            print(f"     🤖 Método: {metodo} ({personalizado})")
            print(f"     💡 Explicación: {explicacion_metodo}")
            
            # Recomendación de acción
            if puntuacion >= 4.5 and metodo == "colaborativo":
                accion = "🎯 ALTAMENTE RECOMENDADO - Pruébalo!"
            elif puntuacion >= 4.0:
                accion = "✅ BUENA OPCIÓN - Vale la pena considerarlo"
            elif puntuacion >= 3.0:
                accion = "🤔 OPCIÓN ALTERNATIVA - Si tienes curiosidad"
            else:
                accion = "⚠️ OPCIÓN DE RESPALDO - Solo si nada más te interesa"
            
            print(f"     🎬 Acción sugerida: {accion}")
        
        # Análisis general
        print(f"\n🧠 INTERPRETACIÓN GENERAL:")
        print("-" * 70)
        
        puntuaciones = [rec.get('puntuacion', 0) for rec in recomendaciones]
        metodos = [rec.get('metodo', 'N/A') for rec in recomendaciones]
        categorias_rec = [rec.get('categoria', 'N/A') for rec in recomendaciones]
        
        # Análisis de calidad
        promedio_puntuacion = sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0
        colaborativas = sum(1 for m in metodos if m == "colaborativo")
        
        print(f"📊 Calidad promedio: {promedio_puntuacion:.2f}")
        if promedio_puntuacion >= 4.5:
            print("   ✨ EXCELENTE: Recomendaciones muy confiables")
        elif promedio_puntuacion >= 4.0:
            print("   ✅ BUENA: Recomendaciones sólidas")
        elif promedio_puntuacion >= 3.0:
            print("   🤔 MODERADA: Recomendaciones aceptables")
        else:
            print("   ⚠️ BÁSICA: Recomendaciones genéricas")
        
        print(f"\n🎯 Personalización: {colaborativas}/{len(recomendaciones)} colaborativas")
        if colaborativas >= 3:
            print("   ✨ ALTA: El sistema te conoce bien")
        elif colaborativas >= 1:
            print("   📊 MEDIA: El sistema está aprendiendo sobre ti")
        else:
            print("   📈 BAJA: Necesitas más interacciones para mejorar")
        
        # Diversidad de categorías
        categorias_unicas = len(set(categorias_rec))
        print(f"\n🎨 Diversidad: {categorias_unicas} categorías diferentes")
        if categorias_unicas >= 4:
            print("   🌈 ALTA: Recomendaciones variadas")
        elif categorias_unicas >= 2:
            print("   🎯 MEDIA: Balance entre especialización y diversidad")
        else:
            print("   📍 BAJA: Enfocado en una categoría específica")
        
        # Consejos personalizados
        print(f"\n💡 CONSEJOS PERSONALIZADOS:")
        print("-" * 70)
        
        if total_interacciones < 10:
            print("🆕 Como usuario nuevo:")
            print("   • Interactúa más con productos para mejorar recomendaciones")
            print("   • Prueba las opciones con puntuación >4.0")
            print("   • Explora diferentes categorías")
        elif colaborativas == 0:
            print("📈 Para obtener recomendaciones más personalizadas:")
            print("   • Necesitas más interacciones en tu historial")
            print("   • Intenta comprar/ver productos de tu interés")
        else:
            print("✨ Estrategias para ti:")
            if promedio_puntuacion >= 4.5:
                print("   • ¡Excelentes recomendaciones! Confía en las top 3")
            else:
                print("   • Enfócate en recomendaciones colaborativas")
            print("   • Considera probar la recomendación #1 primero")
        
        print("\n" + "="*70)
        print("✨ Análisis completado")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error analizando recomendaciones: {e}")

def main():
    """Función principal"""
    print("🔍 ANALIZADOR DE RECOMENDACIONES MLOps")
    print("=====================================")
    
    while True:
        try:
            user_id = input("\n👤 Ingresa el ID del usuario (1-100) o 'q' para salir: ")
            
            if user_id.lower() == 'q':
                print("👋 ¡Hasta luego!")
                break
            
            user_id = int(user_id)
            if 1 <= user_id <= 100:
                analizar_recomendaciones(user_id)
            else:
                print("❌ ID debe estar entre 1 y 100")
                
        except ValueError:
            print("❌ Por favor ingresa un número válido")
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()