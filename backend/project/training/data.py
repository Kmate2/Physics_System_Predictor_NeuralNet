import os
import numpy as np
import pandas as pd


def simulate_projectile_data(n=2000, path="project/artifacts/projectile_dataset.csv", rng_seed=42):
    np.random.seed(rng_seed)
    v = np.random.uniform(10, 100, n)
    a = np.random.uniform(10, 80, n)
    g = 9.81
    theta = np.radians(a)
    t = 2 * v * np.sin(theta) / g
    h = (v**2) * (np.sin(theta)**2) / (2 * g)
    r = (v**2) * np.sin(2 * theta) / g

    df = pd.DataFrame({
        "velocity": v,
        "angle_deg": a,
        "range": r,
        "max_height": h,
        "flight_time": t,
    })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return df


def load_or_simulate_dataframe(path="project/artifacts/projectile_dataset.csv"):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        print(f"[INFO] Data not found at {path}. Simulating dataset…")
        return simulate_projectile_data(path=path)