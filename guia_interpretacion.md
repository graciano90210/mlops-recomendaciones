"""
🎯 GUÍA DE INTERPRETACIÓN DE RECOMENDACIONES MLOps
=================================================

📊 CÓMO INTERPRETAR TUS RECOMENDACIONES:

1. PUNTUACIÓN (Score):
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🥇 5.0 - 4.8  → EXCELENTE: Muy probable que te guste
   🥈 4.7 - 4.4  → BUENA: Recomendación sólida
   🥉 4.3 - 3.0  → MODERADA: Vale la pena considerar
   📊 2.9 - 1.0  → BÁSICA: Opción alternativa

2. MÉTODO DE RECOMENDACIÓN:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
   🤝 COLABORATIVO:
   • Se basa en usuarios con gustos similares al tuyo
   • "A otros usuarios como tú también les gustó esto"
   • MÁS PERSONALIZADO ✨
   
   📈 POPULAR:
   • Se basa en productos más comprados/vistos globalmente
   • "Esto es lo que está de moda"
   • MENOS PERSONALIZADO pero SEGURO

3. ORDEN DE RECOMENDACIONES:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
   🎯 POSICIÓN 1: Tu mejor match (más confianza)
   🎯 POSICIÓN 2-3: Opciones muy sólidas
   🎯 POSICIÓN 4-5: Alternativas interesantes

4. CATEGORÍAS RECOMENDADAS:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
   Si ves varias recomendaciones de la misma categoría:
   → El sistema detectó que te gusta esa categoría
   
   Si ves categorías variadas:
   → El sistema está explorando tus gustos

5. EJEMPLOS PRÁCTICOS:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   EJEMPLO A - Usuario con Historial Rico:
   ┌─────────────────────────────────────────┐
   │ Recomendación 1: Puntuación 5.0        │
   │ Método: colaborativo                    │
   │ → INTERPRETACIÓN: Muy confiable         │
   └─────────────────────────────────────────┘

   EJEMPLO B - Usuario Nuevo:
   ┌─────────────────────────────────────────┐
   │ Recomendación 1: Puntuación 4.2        │
   │ Método: popular                         │
   │ → INTERPRETACIÓN: Segura pero genérica  │
   └─────────────────────────────────────────┘

6. PATRONES A OBSERVAR:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ✅ BUENAS SEÑALES:
   • Puntuaciones altas (>4.5)
   • Método "colaborativo"
   • Categorías que ya te interesan

   ⚠️ SEÑALES DE PRECAUCIÓN:
   • Puntuaciones bajas (<3.0)
   • Solo método "popular"
   • Categorías muy diferentes a tu historial

7. CÓMO USAR LAS RECOMENDACIONES:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   🎯 ESTRATEGIA CONSERVADORA:
   → Prueba solo las recomendaciones con puntuación >4.5

   🎯 ESTRATEGIA EXPLORADORA:
   → Prueba las top 3 recomendaciones sin importar puntuación

   🎯 ESTRATEGIA DIVERSA:
   → Elige una de cada categoría diferente

8. MEJORANDO LAS RECOMENDACIONES:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   📈 Para obtener mejores recomendaciones:
   • Interactúa más con productos (clics, vistas, compras)
   • Mantén un historial diverso pero consistente
   • El sistema aprende de tus patrones de comportamiento

9. CASOS ESPECIALES:
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   🆕 USUARIO NUEVO (pocas interacciones):
   → Recibirás principalmente recomendaciones "populares"
   → Las puntuaciones pueden ser más conservadoras

   👑 USUARIO EXPERIMENTADO (muchas interacciones):
   → Recibirás recomendaciones más "colaborativas"
   → Las puntuaciones serán más precisas

   🔄 USUARIO CON GUSTOS DIVERSOS:
   → Mezcla de métodos colaborativo y popular
   → Recomendaciones de categorías variadas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RESUMEN EJECUTIVO:

1. Confía más en puntuaciones altas (>4.5) y método "colaborativo"
2. La posición 1 es siempre tu mejor opción
3. El sistema mejora con más interacciones
4. Las categorías repetidas indican preferencias detectadas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""