from pathlib import Path
from prefect import flow, task
import subprocess

@task
def validate_data(data_root: str) -> None:
    # Placeholder: aquí integrarías Great Expectations
    for f in ["usuarios.csv", "productos.csv", "interacciones.csv"]:
        p = Path(data_root) / f
        if not p.exists():
            raise FileNotFoundError(f"Falta {f}")

@task
def train(data_root: str, artifacts: str) -> None:
    cmd = [
        "python",
        "next_rec_two_tower/models/train_two_tower.py",
        "--data-root",
        data_root,
        "--artifacts",
        artifacts,
        "--epochs",
        "1",
        "--dim",
        "32",
    ]
    subprocess.check_call(cmd)

@flow(name="Two‑Tower Offline Pipeline")
def tt_pipeline(data_root: str = ".", artifacts: str = ".artifacts"):
    validate_data(data_root)
    train(data_root, artifacts)

if __name__ == "__main__":
    tt_pipeline()