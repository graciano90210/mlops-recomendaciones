import argparse
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, List
from collections import defaultdict

try:
    import mlflow
    import mlflow.pytorch
except Exception:
    mlflow = None

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
except Exception:
    torch = None
    nn = None
    Dataset = object  # placeholder
    DataLoader = None

# Minimal placeholder Lightning-free training to keep it runnable anywhere
# (You can upgrade to PyTorch Lightning Trainer later.)

if torch is not None:
    class InteractionsDataset(Dataset):
        def __init__(self, interactions: pd.DataFrame, n_users: int, n_items: int):
            self.df = interactions
            self.n_users = n_users
            self.n_items = n_items

        def __len__(self):
            return len(self.df)

        def __getitem__(self, idx):
            row = self.df.iloc[idx]
            return int(row["user_id"]), int(row["product_id"]), float(row.get("puntuacion", 1.0))

    class TwoTower(nn.Module):
        def __init__(self, n_users: int, n_items: int, dim: int = 32):
            super().__init__()
            self.user_emb = nn.Embedding(n_users + 1, dim)
            self.item_emb = nn.Embedding(n_items + 1, dim)

        def forward(self, user_ids, item_ids):
            u = self.user_emb(user_ids)
            i = self.item_emb(item_ids)
            # Dot product similarity
            return (u * i).sum(dim=-1)

        def user_vectors(self):
            return self.user_emb.weight.detach().cpu().numpy()

        def item_vectors(self):
            return self.item_emb.weight.detach().cpu().numpy()


def load_data(data_root: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    users = pd.read_csv(data_root / "usuarios.csv")
    items = pd.read_csv(data_root / "productos.csv")
    inter = pd.read_csv(data_root / "interacciones.csv")
    # Asegurar nombres (soporta español/inglés)
    inter = inter.rename(columns={"usuario_id": "user_id", "producto_id": "product_id", "rating": "puntuacion"})
    if "producto_id" in items.columns:
        items = items.rename(columns={"producto_id": "product_id"})
    if "usuario_id" in users.columns:
        users = users.rename(columns={"usuario_id": "user_id"})
    # Tipos
    users = users.copy()
    users["user_id"] = users["user_id"].astype(int)
    items = items.copy()
    items["product_id"] = items["product_id"].astype(int)
    inter["user_id"] = inter["user_id"].astype(int)
    inter["product_id"] = inter["product_id"].astype(int)
    return users, items, inter


def train_val_split(inter: pd.DataFrame, test_ratio: float = 0.2, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split por usuario: últimas interacciones de cada usuario para validación."""
    rng = np.random.default_rng(seed)
    # Ordenar por timestamp si existe
    if "timestamp" in inter.columns:
        inter = inter.sort_values("timestamp")
    
    train_list, val_list = [], []
    for uid, grp in inter.groupby("user_id"):
        n = len(grp)
        n_val = max(1, int(n * test_ratio))
        val_list.append(grp.iloc[-n_val:])
        train_list.append(grp.iloc[:-n_val])
    
    train_df = pd.concat(train_list, ignore_index=True) if train_list else inter.iloc[:0]
    val_df = pd.concat(val_list, ignore_index=True) if val_list else inter.iloc[:0]
    return train_df, val_df


def compute_metrics(user_vecs: np.ndarray, item_vecs: np.ndarray, val_df: pd.DataFrame, k_list: List[int] = [5, 10, 20]) -> Dict[str, float]:
    """
    Calcula Recall@K, NDCG@K, MRR para cada usuario en val_df.
    Retorna promedios sobre todos los usuarios.
    """
    # Normalizar vectores para similitud coseno
    user_norms = np.linalg.norm(user_vecs, axis=1, keepdims=True) + 1e-8
    item_norms = np.linalg.norm(item_vecs, axis=1, keepdims=True) + 1e-8
    user_vecs_n = user_vecs / user_norms
    item_vecs_n = item_vecs / item_norms
    
    # Ground truth por usuario
    user_items_gt = defaultdict(set)
    for _, row in val_df.iterrows():
        user_items_gt[int(row["user_id"])].add(int(row["product_id"]))
    
    metrics = {f"recall@{k}": [] for k in k_list}
    metrics.update({f"ndcg@{k}": [] for k in k_list})
    metrics["mrr"] = []
    
    for uid, gt_items in user_items_gt.items():
        if uid >= user_vecs_n.shape[0]:
            continue
        u = user_vecs_n[uid:uid+1]
        scores = (item_vecs_n @ u.T).ravel()
        top_indices = np.argsort(-scores)
        
        # MRR: primer item relevante
        rank_first = None
        for rank, iid in enumerate(top_indices, start=1):
            if iid in gt_items:
                rank_first = rank
                break
        if rank_first:
            metrics["mrr"].append(1.0 / rank_first)
        else:
            metrics["mrr"].append(0.0)
        
        # Recall@K y NDCG@K
        for k in k_list:
            topk = top_indices[:k]
            hits = sum(1 for iid in topk if iid in gt_items)
            metrics[f"recall@{k}"].append(hits / len(gt_items) if gt_items else 0.0)
            
            # NDCG@K
            dcg = sum((1 if topk[i] in gt_items else 0) / np.log2(i + 2) for i in range(k))
            idcg = sum(1 / np.log2(i + 2) for i in range(min(k, len(gt_items))))
            metrics[f"ndcg@{k}"].append(dcg / idcg if idcg > 0 else 0.0)
    
    # Promediar
    return {key: float(np.mean(vals)) if vals else 0.0 for key, vals in metrics.items()}


def train_baseline(users: pd.DataFrame, items: pd.DataFrame, inter: pd.DataFrame, dim: int = 32, epochs: int = 1, lr: float = 1e-2):
    n_users = int(users["user_id"].max()) + 1
    n_items = int(items["product_id"].max()) + 1

    if torch is None:
        # Fallback sencillo: inicializar embeddings aleatorios reproducibles
        rng = np.random.default_rng(42)
        user_vecs = rng.normal(size=(n_users + 1, dim)).astype(np.float32)
        item_vecs = rng.normal(size=(n_items + 1, dim)).astype(np.float32)
        print("Torch no disponible. Se generaron embeddings aleatorios para demo.")
        return user_vecs, item_vecs, []

    model = TwoTower(n_users=n_users, n_items=n_items, dim=dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    ds = InteractionsDataset(inter, n_users, n_items)
    dl = DataLoader(ds, batch_size=512, shuffle=True)

    epoch_losses = []
    model.train()
    for ep in range(epochs):
        total = 0.0
        for u, i, y in dl:
            u = u.long()
            i = i.long()
            y = y.float()
            pred = model(u, i)
            loss = ((pred - y)**2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item() * len(u)
        avg_loss = total / len(ds)
        epoch_losses.append(avg_loss)
        print(f"epoch={ep+1} loss={avg_loss:.4f}")
    return model, epoch_losses


def build_faiss_index(item_vecs: np.ndarray, artifacts: Path):
    try:
        import faiss  # type: ignore
    except Exception as e:
        print("FAISS no disponible, se omitirá el índice.", e)
        return None
    d = item_vecs.shape[1]
    index = faiss.IndexFlatIP(d)  # inner product
    # normalizar para usar IP como coseno
    norms = np.linalg.norm(item_vecs, axis=1, keepdims=True) + 1e-8
    normed = item_vecs / norms
    index.add(normed.astype(np.float32))
    faiss.write_index(index, str(artifacts / "faiss_item.index"))
    np.save(artifacts / "item_vecs.npy", item_vecs)
    return str(artifacts / "faiss_item.index")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=str, default=".")
    parser.add_argument("--artifacts", type=str, default=".artifacts")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--dim", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-2)
    parser.add_argument("--mlflow-tracking", action="store_true", help="Enable MLflow tracking")
    parser.add_argument("--experiment-name", type=str, default="two-tower-recommender")
    args = parser.parse_args()

    data_root = Path(args.data_root)
    artifacts = Path(args.artifacts)
    artifacts.mkdir(parents=True, exist_ok=True)

    # MLflow setup
    if args.mlflow_tracking and mlflow:
        mlflow.set_experiment(args.experiment_name)
        mlflow.start_run()
        mlflow.log_params({
            "dim": args.dim,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": 512,
        })

    users, items, inter = load_data(data_root)
    train_df, val_df = train_val_split(inter, test_ratio=0.2, seed=42)
    
    print(f"Train: {len(train_df)} interacciones, Val: {len(val_df)} interacciones")
    
    model_or_vecs, epoch_losses = train_baseline(users, items, train_df, dim=args.dim, epochs=args.epochs, lr=args.lr)

    # Export embeddings
    if torch is not None and isinstance(model_or_vecs, nn.Module):
        user_vecs = model_or_vecs.user_vectors()
        item_vecs = model_or_vecs.item_vectors()
    else:
        user_vecs, item_vecs = model_or_vecs
    
    np.save(artifacts / "user_vecs.npy", user_vecs)
    np.save(artifacts / "item_vecs.npy", item_vecs)

    # Compute validation metrics
    val_metrics = compute_metrics(user_vecs, item_vecs, val_df, k_list=[5, 10, 20])
    print("\n=== Validation Metrics ===")
    for k, v in val_metrics.items():
        print(f"{k}: {v:.4f}")
    
    # MLflow logging
    if args.mlflow_tracking and mlflow:
        for ep, loss in enumerate(epoch_losses, start=1):
            mlflow.log_metric("train_loss", loss, step=ep)
        # MLflow no acepta @ en nombres, usar _
        for metric_name, metric_val in val_metrics.items():
            mlflow_name = metric_name.replace("@", "_at_")
            mlflow.log_metric(mlflow_name, metric_val)
        
        # Log artifacts
        mlflow.log_artifact(str(artifacts / "user_vecs.npy"))
        mlflow.log_artifact(str(artifacts / "item_vecs.npy"))
        
        # Log model if torch available
        if torch is not None and isinstance(model_or_vecs, nn.Module):
            mlflow.pytorch.log_model(model_or_vecs, "model")

    index_path = build_faiss_index(item_vecs, artifacts)

    meta = {
        "dim": args.dim,
        "epochs": args.epochs,
        "lr": args.lr,
        "n_users": int(users["user_id"].max()) + 1,
        "n_items": int(items["product_id"].max()) + 1,
        "index_path": index_path,
        "val_metrics": val_metrics,
    }
    with open(artifacts / "model_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    
    if args.mlflow_tracking and mlflow:
        mlflow.log_artifact(str(artifacts / "model_meta.json"))
        mlflow.end_run()
    
    print(f"\nArtefactos guardados en {artifacts}")
    print(f"Recall@10: {val_metrics.get('recall@10', 0):.4f}, NDCG@10: {val_metrics.get('ndcg@10', 0):.4f}, MRR: {val_metrics.get('mrr', 0):.4f}")

if __name__ == "__main__":
    main()
