# MLflow Tracking y Evaluación - Two-Tower Recommender

## Descripción

El módulo Two-Tower ahora incluye:
- ✅ **Train/Val split** automático por usuario (últimas 20% interacciones)
- ✅ **Métricas de evaluación**: Recall@K, NDCG@K, MRR
- ✅ **MLflow tracking**: params, métricas, artefactos, modelo

## Uso

### 1. Entrenar con tracking (recomendado)

```powershell
# Activa el venv de Python 3.11
. .\.venv311\Scripts\Activate.ps1

# Entrena con MLflow tracking habilitado
python next_rec_two_tower\models\train_two_tower.py `
  --data-root . `
  --artifacts .\.artifacts `
  --epochs 5 `
  --dim 32 `
  --lr 0.01 `
  --mlflow-tracking `
  --experiment-name "two-tower-baseline"
```

Parámetros:
- `--mlflow-tracking`: Activa logging en MLflow
- `--experiment-name`: Nombre del experimento (agrupa runs)
- `--epochs`: Número de épocas de entrenamiento
- `--dim`: Dimensión de embeddings
- `--lr`: Learning rate

### 2. Visualizar experimentos en MLflow UI

```powershell
# Desde la raíz del proyecto
mlflow ui --backend-store-uri file:///./mlruns --port 5000
```

Luego abre en tu navegador: http://localhost:5000

Verás:
- Todos los experimentos y runs
- Parámetros (dim, lr, epochs, batch_size)
- Métricas (train_loss, recall_at_5, recall_at_10, ndcg_at_10, mrr)
- Artefactos (user_vecs.npy, item_vecs.npy, model, model_meta.json)
- Gráficos de comparación entre runs

### 3. Entrenar sin tracking (rápido)

```powershell
python next_rec_two_tower\models\train_two_tower.py `
  --data-root . `
  --artifacts .\.artifacts `
  --epochs 1 `
  --dim 16
```

## Métricas disponibles

### Recall@K
Proporción de items relevantes recuperados en top-K recomendaciones.
- `recall_at_5`: Recall en top 5
- `recall_at_10`: Recall en top 10
- `recall_at_20`: Recall en top 20

### NDCG@K (Normalized Discounted Cumulative Gain)
Calidad de ranking considerando posición de items relevantes.
- `ndcg_at_5`, `ndcg_at_10`, `ndcg_at_20`

### MRR (Mean Reciprocal Rank)
Promedio del inverso de la posición del primer item relevante.

## Interpretación

### Valores esperados (baseline inicial)
- **Recall@10**: 0.005-0.02 (0.5%-2%)
- **NDCG@10**: 0.005-0.015 (0.5%-1.5%)
- **MRR**: 0.01-0.05 (1%-5%)

Estos valores son bajos porque:
- Dataset pequeño (5K interacciones)
- Modelo simple (Two-Tower vanilla sin features)
- 1-3 épocas de entrenamiento

### Mejoras esperadas
Con optimización (Optuna) y más épocas (10-20):
- **Recall@10**: 0.05-0.15 (5%-15%)
- **NDCG@10**: 0.03-0.10 (3%-10%)
- **MRR**: 0.10-0.25 (10%-25%)

## Comparar experimentos en MLflow UI

1. Selecciona múltiples runs (checkbox)
2. Click en "Compare"
3. Ve métricas lado a lado, gráficos de scatter, parallel coordinates

## Próximos pasos

1. **Optuna HPO**: Optimizar dim, lr, epochs automáticamente
2. **Negative sampling**: Mejorar calidad de entrenamiento
3. **Features**: Agregar metadata de usuarios/items
4. **Producción**: Deploy del mejor modelo desde MLflow Model Registry

## Estructura de artefactos MLflow

```
mlruns/
├── 0/                          # Experimento Default
├── <experiment_id>/            # Tu experimento (ej: two-tower-baseline)
│   ├── <run_id>/
│   │   ├── artifacts/
│   │   │   ├── model/          # Modelo PyTorch
│   │   │   ├── user_vecs.npy
│   │   │   ├── item_vecs.npy
│   │   │   └── model_meta.json
│   │   ├── metrics/
│   │   │   ├── train_loss
│   │   │   ├── recall_at_10
│   │   │   └── ...
│   │   └── params/
│   │       ├── dim
│   │       ├── lr
│   │       └── epochs
```

## Comandos útiles

```powershell
# Ver experimentos desde CLI
mlflow experiments list

# Buscar runs por métrica
mlflow runs search --experiment-name "two-tower-baseline" --filter "metrics.recall_at_10 > 0.01"

# Cargar modelo desde Python
import mlflow
model = mlflow.pytorch.load_model("runs:/<run_id>/model")
```

## Tips

- Usa nombres descriptivos para experimentos: `two-tower-{feature}` (ej: two-tower-hpo, two-tower-features)
- Documenta cambios en tags de MLflow: `mlflow.set_tag("description", "Added user demographics")`
- Exporta métricas para reportes: MLflow UI → Download CSV
