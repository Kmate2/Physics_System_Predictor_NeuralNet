
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple
import joblib, torch
from pydantic_settings import BaseSettings

from project.backend.model_def import ProjectileNet

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_ARTIFACTS = (REPO_ROOT / "project" / "artifacts").resolve()

class Settings(BaseSettings):
    artifacts_dir: str = str(DEFAULT_ARTIFACTS)
    model_path: Optional[str] = None
    scaler_x_path: Optional[str] = None
    scaler_y_path: Optional[str] = None
    device: str = "cuda" if torch.cuda.is_available() else "cpu"

    def model_post_init(self, *_):
        base = Path(self.artifacts_dir)
        self.model_path    = self.model_path    or str(base / "projectile_net.pt")
        self.scaler_x_path = self.scaler_x_path or str(base / "projectile_scaler_X.pkl")
        self.scaler_y_path = self.scaler_y_path or str(base / "projectile_scaler_y.pkl")

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_artifacts() -> Tuple[torch.nn.Module, object, object, torch.device]:
    s = get_settings()
    device = torch.device(s.device)

    for p in [s.model_path, s.scaler_x_path, s.scaler_y_path]:
        rp = Path(p).resolve()
        if not rp.exists() or not rp.is_file():
            raise FileNotFoundError(p)
        if Path(s.artifacts_dir).resolve() not in rp.parents:
            raise ValueError(f"Artifact outside artifacts_dir: {rp}")

    sx = joblib.load(s.scaler_x_path)
    sy = joblib.load(s.scaler_y_path)

    model = ProjectileNet()
    state = torch.load(s.model_path, map_location=device)
    model.load_state_dict(state)
    model.to(device).eval()
    _ = model(torch.zeros(1, 2, device=device))  # warmup
    return model, sx, sy, device
