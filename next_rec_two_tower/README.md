# Two‑Tower Recommender System (Deep Learning) – MLOps Edition

Este módulo extiende el proyecto `Proyecto_MLOps` con un recomendador Two‑Tower (user tower + item tower) listo para MLOps.

## Objetivos
- Entrenamiento reproducible (PyTorch Lightning + MLflow)
- Features gestionadas (Feast, opcional en esta etapa)
- Recuperación ANN (FAISS) + re‑rank simple
- Serving en tiempo real (FastAPI) y pipeline (Prefect)
- Validación de datos (Great Expectations)

## Estructura
```
next_rec_two_tower/
├── models/                 # Entrenamiento y export
│   └── train_two_tower.py  
├── services/
│   └── api/
│       └── main.py         # API de inferencia
├── pipelines/
│   └── prefect_flow.py     # Orquestación (esqueleto)
├── monitoring/
│   └── evidently_report.py # Reporte de drift (placeholder)
├── infra/                  # Config (MLflow/Feast/Terraform opcional)
└── requirements-tt.txt     # Dependencias
```

## Quickstart

1) Crear entorno e instalar dependencias
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r next_rec_two_tower/requirements-tt.txt
```

2) Entrenar un baseline y construir índice
```bash
python next_rec_two_tower/models/train_two_tower.py --data-root . --artifacts ./.artifacts --epochs 1 --dim 32
```

3) Levantar la API
```bash
uvicorn next_rec_two_tower.services.api.main:app --host 0.0.0.0 --port 8001 --reload
```

4) Probar
```bash
curl http://localhost:8001/health
curl http://localhost:8001/rec/40?k=5
```

## Roadmap (4 sprints)
- S1: Baseline Lightning + MLflow + FAISS + API mínima
- S2: Optuna HPO, métricas (Recall@K, NDCG), validación GX
- S3: Feast (offline→online), materialización, Prefect
- S4: Despliegue KServe/ECS, Evidently + Prometheus/Grafana
