# Optimización de Hiperparámetros con Optuna

## Descripción

El script `hpo_optuna.py` automatiza la búsqueda de los mejores hiperparámetros para el modelo Two-Tower usando Optuna.

### Hiperparámetros optimizados
- **dim**: Dimensión de embeddings (8-64, step=8)
- **lr**: Learning rate (1e-4 a 1e-1, escala logarítmica)
- **epochs**: Número de épocas (3-15)
- **batch_size**: Tamaño de batch (128, 256, 512)

### Métrica objetivo
**Recall@10** (maximizar)

## Uso rápido

### 1. HPO básico (20 trials)

```powershell
# Activa venv de Python 3.11
. .\.venv311\Scripts\Activate.ps1

# Ejecuta HPO con 20 trials
python next_rec_two_tower\models\hpo_optuna.py `
  --data-root . `
  --n-trials 20
```

### 2. HPO con MLflow tracking

```powershell
python next_rec_two_tower\models\hpo_optuna.py `
  --data-root . `
  --n-trials 30 `
  --mlflow-tracking `
  --experiment-name "two-tower-hpo"
```

### 3. HPO con persistencia (SQLite storage)

```powershell
# Permite continuar estudios interrumpidos
python next_rec_two_tower\models\hpo_optuna.py `
  --data-root . `
  --n-trials 50 `
  --storage "sqlite:///hpo_study.db" `
  --study-name "two-tower-hpo-v1" `
  --mlflow-tracking
```

### 4. HPO con timeout

```powershell
# Limitar por tiempo (ej: 1 hora = 3600 segundos)
python next_rec_two_tower\models\hpo_optuna.py `
  --n-trials 100 `
  --timeout 3600 `
  --mlflow-tracking
```

## Qué hace el script

1. **Carga datos** y hace train/val split
2. **Crea estudio Optuna** con sampler TPE (Tree-structured Parzen Estimator)
3. **Ejecuta N trials**:
   - Sugiere combinación de hiperparámetros
   - Entrena modelo
   - Evalúa en validación (Recall@K, NDCG@K, MRR)
   - Registra resultados
4. **Selecciona mejor trial** (max Recall@10)
5. **Re-entrena con mejores params** en train+val combinados
6. **Guarda artefactos** en `.artifacts_best/`
7. **Genera visualizaciones** HTML interactivas

## Outputs

### Archivos generados

```
.artifacts_best/          # Modelo final optimizado
├── user_vecs.npy
├── item_vecs.npy
├── best_model.pth        # Pesos PyTorch
└── model_meta.json       # Metadata + best params

hpo_results.json          # Resultados del estudio
hpo_history.html          # Evolución de trials
hpo_param_importance.html # Importancia de hiperparámetros
hpo_parallel_coordinate.html # Coordenadas paralelas
```

### Visualizaciones

**hpo_history.html**
- Evolución de Recall@10 a través de trials
- Identifica convergencia

**hpo_param_importance.html**
- Qué hiperparámetros afectan más al Recall@10
- Basado en análisis ANOVA

**hpo_parallel_coordinate.html**
- Vista multidimensional de todos los trials
- Identifica patrones entre hiperparámetros

## Ejemplo de salida

```
Datos: 4042 train, 958 val
Usuarios: 102, Items: 1051
Iniciando Optuna HPO con 20 trials...

[I 2025-10-27 22:30:00,000] Trial 0 finished with value: 0.0085
[I 2025-10-27 22:31:00,000] Trial 1 finished with value: 0.0120
...
[I 2025-10-27 22:50:00,000] Trial 19 finished with value: 0.0230

============================================================
OPTIMIZACIÓN COMPLETADA
============================================================
Mejor trial: 15
Mejor Recall@10: 0.0230

Mejores hiperparámetros:
  dim: 48
  lr: 0.0089
  epochs: 10
  batch_size: 256

Métricas del mejor trial:
  recall_at_5: 0.0110
  recall_at_10: 0.0230
  ndcg_at_10: 0.0180
  mrr: 0.0520
  final_train_loss: 8.2341

Resultados guardados en: hpo_results.json

Visualizaciones guardadas:
  - hpo_history.html
  - hpo_param_importance.html
  - hpo_parallel_coordinate.html

============================================================
RE-ENTRENANDO CON MEJORES HIPERPARÁMETROS
============================================================

Modelo final guardado en: .artifacts_best
Listo para deployment!
```

## Integración con MLflow

Con `--mlflow-tracking`:
- Cada trial se registra como run anidado en MLflow
- El modelo final se guarda en MLflow Model Registry
- Puedes comparar trials en MLflow UI: http://localhost:5000

```powershell
mlflow ui --backend-store-uri file:///./mlruns
```

## Reanudar estudio interrumpido

Si usas `--storage sqlite:///hpo_study.db`:

```powershell
# Primera ejecución: 20 trials
python next_rec_two_tower\models\hpo_optuna.py `
  --n-trials 20 `
  --storage "sqlite:///hpo_study.db" `
  --study-name "my-study"

# Reanuda y añade 10 trials más
python next_rec_two_tower\models\hpo_optuna.py `
  --n-trials 10 `
  --storage "sqlite:///hpo_study.db" `
  --study-name "my-study"
```

## Tips

### Cuántos trials ejecutar
- **Exploración rápida**: 10-20 trials (~10-30 min)
- **Búsqueda estándar**: 30-50 trials (~30-60 min)
- **Búsqueda exhaustiva**: 100+ trials (1-2 horas)

### Optimizar tiempo de ejecución
- Reduce `--n-trials` para pruebas rápidas
- Usa `--timeout` para limitar por tiempo
- Ajusta rango de `epochs` (ej: 3-10 en vez de 3-15)

### Interpretar importancia de hiperparámetros
Si `hpo_param_importance.html` muestra:
- **dim** más importante → Aumenta rango de búsqueda (ej: 8-128)
- **lr** más importante → Ajusta bounds (ej: 1e-5 a 1e-1)
- **batch_size** poco importante → Fija a 256 y elimina del espacio

### Métricas típicas después de HPO
Con 30-50 trials en este dataset:
- **Recall@10**: 0.015-0.035 (1.5%-3.5%)
- **NDCG@10**: 0.012-0.025 (1.2%-2.5%)
- **MRR**: 0.04-0.08 (4%-8%)

## Próximos pasos

1. **Deploy del mejor modelo**: Usa `.artifacts_best/` en la API
2. **A/B testing**: Compara baseline vs modelo optimizado
3. **Re-entrenamiento periódico**: Ejecuta HPO semanalmente con nuevos datos
4. **Optimización multi-objetivo**: Modifica para optimizar Recall@10 + NDCG@10
5. **Pruning**: Añade callbacks para detener trials pobres tempranamente

## Comandos útiles

```powershell
# Ver dashboard Optuna (si instalas optuna-dashboard)
pip install optuna-dashboard
optuna-dashboard sqlite:///hpo_study.db

# Exportar resultados a CSV
python -c "import optuna; import pandas as pd; study = optuna.load_study('two-tower-hpo', 'sqlite:///hpo_study.db'); pd.DataFrame([t.params | t.user_attrs | {'value': t.value} for t in study.trials]).to_csv('hpo_trials.csv', index=False)"
```

## Troubleshooting

**Error: "Optuna no instalado"**
```powershell
pip install optuna
```

**Error: "Torch no disponible"**
- Asegúrate de usar `.venv311` con Torch instalado
- Ver guía: `next_rec_two_tower/README.md` sección Windows

**Trials muy lentos**
- Reduce `epochs` máximo: cambia `suggest_int("epochs", 3, 10)` en hpo_optuna.py
- Reduce dataset: usa sample del 50% de datos para HPO rápido

**Visualizaciones no se generan**
```powershell
pip install plotly kaleido
```
