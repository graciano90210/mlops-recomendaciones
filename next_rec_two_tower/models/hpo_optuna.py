"""
Optimización de Hiperparámetros con Optuna + MLflow
Busca la mejor combinación de dim, lr, epochs, batch_size para maximizar Recall@10.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict

try:
    import optuna
    OPTUNA_AVAILABLE = True
    # MLflowCallback es opcional
    try:
        from optuna.integration.mlflow import MLflowCallback
        MLFLOW_CALLBACK_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        MLflowCallback = None
        MLFLOW_CALLBACK_AVAILABLE = False
except ImportError as e:
    optuna = None
    MLflowCallback = None
    OPTUNA_AVAILABLE = False
    MLFLOW_CALLBACK_AVAILABLE = False
    OPTUNA_IMPORT_ERROR = str(e)

try:
    import mlflow
except ImportError:
    mlflow = None

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
except Exception:
    torch = None
    nn = None

# Importar funciones del script de entrenamiento
import sys
sys.path.append(str(Path(__file__).parent))
from train_two_tower import (
    load_data, train_val_split, compute_metrics,
    InteractionsDataset, TwoTower
)


def train_trial(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    n_users: int,
    n_items: int,
    dim: int,
    lr: float,
    epochs: int,
    batch_size: int
) -> Dict[str, float]:
    """Entrena un trial y retorna métricas de validación."""
    if torch is None:
        raise RuntimeError("Torch no disponible. HPO requiere PyTorch.")
    
    model = TwoTower(n_users=n_users, n_items=n_items, dim=dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    ds = InteractionsDataset(train_df, n_users, n_items)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=True)
    
    model.train()
    final_loss = 0.0
    for ep in range(epochs):
        total = 0.0
        for u, i, y in dl:
            u = u.long()
            i = i.long()
            y = y.float()
            pred = model(u, i)
            loss = ((pred - y)**2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * len(u)
        final_loss = total / len(ds)
    
    # Evaluar
    user_vecs = model.user_vectors()
    item_vecs = model.item_vectors()
    val_metrics = compute_metrics(user_vecs, item_vecs, val_df, k_list=[5, 10, 20])
    val_metrics["final_train_loss"] = final_loss
    
    return val_metrics


def objective(trial: "optuna.Trial", train_df: pd.DataFrame, val_df: pd.DataFrame, n_users: int, n_items: int) -> float:
    """Función objetivo de Optuna: maximizar Recall@10."""
    # Espacio de búsqueda
    dim = trial.suggest_int("dim", 8, 64, step=8)
    lr = trial.suggest_float("lr", 1e-4, 1e-1, log=True)
    epochs = trial.suggest_int("epochs", 3, 15)
    batch_size = trial.suggest_categorical("batch_size", [128, 256, 512])
    
    # Entrenar
    val_metrics = train_trial(train_df, val_df, n_users, n_items, dim, lr, epochs, batch_size)
    
    # Log métricas adicionales (Optuna soporta set_user_attr)
    trial.set_user_attr("recall_at_5", val_metrics["recall@5"])
    trial.set_user_attr("recall_at_10", val_metrics["recall@10"])
    trial.set_user_attr("ndcg_at_10", val_metrics["ndcg@10"])
    trial.set_user_attr("mrr", val_metrics["mrr"])
    trial.set_user_attr("final_train_loss", val_metrics["final_train_loss"])
    
    # Objetivo: maximizar Recall@10
    return val_metrics["recall@10"]


def main():
    parser = argparse.ArgumentParser(description="Optuna HPO para Two-Tower Recommender")
    parser.add_argument("--data-root", type=str, default=".")
    parser.add_argument("--n-trials", type=int, default=20, help="Número de trials de Optuna")
    parser.add_argument("--timeout", type=int, default=None, help="Timeout en segundos (opcional)")
    parser.add_argument("--mlflow-tracking", action="store_true", help="Integrar con MLflow")
    parser.add_argument("--experiment-name", type=str, default="two-tower-hpo")
    parser.add_argument("--study-name", type=str, default="hpo-study", help="Nombre del estudio Optuna")
    parser.add_argument("--storage", type=str, default=None, help="SQLite storage para Optuna (opcional)")
    args = parser.parse_args()
    
    if not OPTUNA_AVAILABLE:
        print(f"Error: Optuna no disponible. Detalle: {OPTUNA_IMPORT_ERROR}")
        raise RuntimeError("Optuna no instalado. Ejecuta: pip install optuna")
    
    # Cargar datos
    data_root = Path(args.data_root)
    users, items, inter = load_data(data_root)
    train_df, val_df = train_val_split(inter, test_ratio=0.2, seed=42)
    
    n_users = int(users["user_id"].max()) + 1
    n_items = int(items["product_id"].max()) + 1
    
    print(f"Datos: {len(train_df)} train, {len(val_df)} val")
    print(f"Usuarios: {n_users}, Items: {n_items}")
    print(f"Iniciando Optuna HPO con {args.n_trials} trials...")
    
    # MLflow callback (si habilitado y disponible)
    mlflc = None
    if args.mlflow_tracking and mlflow and MLFLOW_CALLBACK_AVAILABLE:
        mlflow.set_experiment(args.experiment_name)
        # MLflowCallback registra cada trial como run en MLflow
        mlflc = MLflowCallback(
            tracking_uri=mlflow.get_tracking_uri(),
            metric_name="recall_at_10",
            create_experiment=False,
            mlflow_kwargs={"nested": True}
        )
    elif args.mlflow_tracking and not MLFLOW_CALLBACK_AVAILABLE:
        print("Advertencia: MLflowCallback no disponible. Instala: pip install optuna-integration[mlflow]")
        print("Continuando sin callback MLflow...")
    
    # Crear estudio Optuna
    study = optuna.create_study(
        study_name=args.study_name,
        direction="maximize",
        storage=args.storage,
        load_if_exists=True,
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    # Optimizar
    callbacks = [mlflc] if mlflc else []
    study.optimize(
        lambda trial: objective(trial, train_df, val_df, n_users, n_items),
        n_trials=args.n_trials,
        timeout=args.timeout,
        callbacks=callbacks,
        show_progress_bar=True
    )
    
    # Resultados
    print("\n" + "="*60)
    print("OPTIMIZACIÓN COMPLETADA")
    print("="*60)
    print(f"Mejor trial: {study.best_trial.number}")
    print(f"Mejor Recall@10: {study.best_value:.4f}")
    print("\nMejores hiperparámetros:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value}")
    
    print("\nMétricas del mejor trial:")
    for key, value in study.best_trial.user_attrs.items():
        print(f"  {key}: {value:.4f}")
    
    # Guardar resultados
    results_path = Path(".") / "hpo_results.json"
    results = {
        "best_trial": study.best_trial.number,
        "best_value": study.best_value,
        "best_params": study.best_params,
        "best_metrics": study.best_trial.user_attrs,
        "n_trials": len(study.trials),
    }
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResultados guardados en: {results_path}")
    
    # Visualizaciones (si optuna.visualization disponible)
    try:
        import optuna.visualization as vis
        # Guardar gráficos como HTML
        fig_history = vis.plot_optimization_history(study)
        fig_history.write_html("hpo_history.html")
        
        fig_importance = vis.plot_param_importances(study)
        fig_importance.write_html("hpo_param_importance.html")
        
        fig_parallel = vis.plot_parallel_coordinate(study)
        fig_parallel.write_html("hpo_parallel_coordinate.html")
        
        print("\nVisualizaciones guardadas:")
        print("  - hpo_history.html (evolución)")
        print("  - hpo_param_importance.html (importancia)")
        print("  - hpo_parallel_coordinate.html (coordenadas paralelas)")
    except Exception as e:
        print(f"\nNo se pudieron generar visualizaciones: {e}")
    
    # Re-entrenar con mejores params y guardar modelo
    print("\n" + "="*60)
    print("RE-ENTRENANDO CON MEJORES HIPERPARÁMETROS")
    print("="*60)
    
    best_params = study.best_params
    best_metrics = train_trial(
        train_df, val_df, n_users, n_items,
        dim=best_params["dim"],
        lr=best_params["lr"],
        epochs=best_params["epochs"],
        batch_size=best_params["batch_size"]
    )
    
    # Entrenar en train+val combinados para producción
    full_df = pd.concat([train_df, val_df], ignore_index=True)
    final_model = TwoTower(n_users=n_users, n_items=n_items, dim=best_params["dim"])
    opt_final = torch.optim.Adam(final_model.parameters(), lr=best_params["lr"])
    ds_final = InteractionsDataset(full_df, n_users, n_items)
    dl_final = DataLoader(ds_final, batch_size=best_params["batch_size"], shuffle=True)
    
    final_model.train()
    for ep in range(best_params["epochs"]):
        for u, i, y in dl_final:
            u = u.long()
            i = i.long()
            y = y.float()
            pred = final_model(u, i)
            loss = ((pred - y)**2).mean()
            opt_final.zero_grad()
            loss.backward()
            opt_final.step()
    
    # Guardar artefactos finales
    artifacts_dir = Path(".artifacts_best")
    artifacts_dir.mkdir(exist_ok=True)
    
    user_vecs = final_model.user_vectors()
    item_vecs = final_model.item_vectors()
    np.save(artifacts_dir / "user_vecs.npy", user_vecs)
    np.save(artifacts_dir / "item_vecs.npy", item_vecs)
    
    meta = {
        "best_params": best_params,
        "val_metrics": {k: float(v) for k, v in best_metrics.items()},
        "n_users": n_users,
        "n_items": n_items,
        "trained_on": "train+val",
    }
    with open(artifacts_dir / "model_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    
    if mlflow and args.mlflow_tracking:
        torch.save(final_model.state_dict(), artifacts_dir / "best_model.pth")
        with mlflow.start_run(run_name="best-hpo-model"):
            mlflow.log_params(best_params)
            for k, v in best_metrics.items():
                mlflow.log_metric(k.replace("@", "_at_"), v)
            mlflow.log_artifacts(str(artifacts_dir))
            mlflow.pytorch.log_model(final_model, "model")
    
    print(f"\nModelo final guardado en: {artifacts_dir}")
    print("Listo para deployment!")


if __name__ == "__main__":
    main()
