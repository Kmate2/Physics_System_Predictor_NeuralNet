# Physics System Simulator — Projectile Surrogate (Full-Stack)

An end-to-end demo that **trains a PyTorch surrogate model** for *ideal projectile motion* and **serves predictions** via a **Flask** API, with a small **React + Vite** frontend that visualizes and compares **analytic physics** vs. **AI predictions**.

**Inputs:** velocity *(m/s)*, angle *(deg)* → **Outputs:** range *(m)*, max height *(m)*, flight time *(s)*.

The frontend overlays the analytic parabola against the AI surrogate.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Repo Layout](#repo-layout)
- [Quickstart (TL;DR)](#quickstart-tldr)
- [Backend (Training & Serving)](#backend-training--serving)
  - [Artifacts](#artifacts)
  - [API](#api)
  - [Configuration](#configuration)
  - [Reproducibility & Leakage](#reproducibility--data-leakage)
  - [Tests](#tests)
- [Frontend (React + Vite)](#frontend-react--vite)
  - [Backend URL / Env](#backend-url--environment)
  - [App Flow](#app-flow)
- [Notes & Limitations](#notes--limitations)
- [License](#license)

---

## Features

**Backend**
- **PyTorch** MLP (**2 → 64 → 32 → 3**), **Adam**, **early stopping**
- **scikit-learn** `StandardScaler` for **inputs** and **targets**
- **Flask** (+ `flask-cors`) with **`/predict`** and **`/health`**
- Reproducible training, saved **artifacts**, and **evaluation** helpers
- Lightweight data tooling with **NumPy / pandas / matplotlib**

**Frontend**
- **Plugin-style model registry** — add new physics systems without touching core
- **Analytic vs. AI comparison** — compute physics baselines and overlay predictions
- **SVG plots + lightweight animation**
- **Plain CSS** styling (easy to theme later)

---

## Tech Stack

- **Backend:** PyTorch, scikit-learn, Flask, flask-cors, NumPy, pandas, matplotlib
- **Frontend:** React **19**, React Router DOM **7**, Vite **7**, plain CSS

---

## Repo Layout

```text
.
├─ backend/
│  ├─ app.py              # Flask API (loads artifacts once; inference only)
│  ├─ model_def.py        # ProjectileNet architecture
│  └─ predict_utils.py    # scale → model → inverse-scale
├─ training/
│  ├─ train.py            # main training pipeline (reproducible)
│  ├─ data.py             # simulate/load dataset
│  ├─ prep.py             # split_and_scale + DataLoaders (saves scalers)
│  └─ eval.py             # evaluate() + metrics + plot_history()
├─ frontend/
│  ├─ src/                # components, model registry, utils, views
│  ├─ public/
│  ├─ index.html
│  ├─ package.json
│  └─ vite.config.js
├─ artifacts/             # outputs (weights, scalers, metrics, curve, csv)
├─ requirements/
│  ├─ serve.txt           # minimal deps to serve
│  └─ train.txt           # all deps to train (includes serve.txt)
├─ tests/                 # pytest suite
└─ README.md
```

---

## Quickstart (TL;DR)

> Prereqs: **Python 3.9+**, **Node 18+** (or newer), **pip**, **npm**

```bash
# 1) Install backend deps (training)
cd project
python pip install -r requirements/train.txt

# 2) Train (writes ./artifacts/*)
python -m training.train
```

```bash
# 3) Serve the model (Flask)
 cd project
 pip install -r requirements/serve.txt
 flask --app backend.app run    
```

```bash
# 4) Try the API
curl -X POST http://127.0.0.1:5000/predict   -H 'Content-Type: application/json'   -d '{"velocity":50, "angle_deg":45}'

curl http://127.0.0.1:5000/health
```

```bash
# 5) Frontend
cd frontend
npm i
# point the app at your backend (see "Backend URL / Environment" below)
npm run dev  # opens http://127.0.0.1:5173/
```

---

## Backend (Training & Serving)

### Artifacts

Created by `python -m training.train`, saved to `./artifacts/`:

- `projectile_net.pt` — model weights (`state_dict`)
- `projectile_scaler_X.pkl` — input `StandardScaler`
- `projectile_scaler_y.pkl` — target `StandardScaler`
- `projectile_metrics.json` — config, best epoch, test **RMSE/MAE** (real units)
- `training_curve.png` — train/val loss vs. epoch
- `projectile_dataset.csv` — generated if missing

### API

#### `POST /predict`  *(single input)*
**Body**
```json
{ "velocity": 50.0, "angle_deg": 45.0 }
```

**Returns**
```json
{
  "prediction": {
    "range_m": 188.2,
    "max_height_m": 41.3,
    "flight_time_s": 5.4
  }
}
```

#### `GET /health`
Example:
```json
{ "status": "ok", "device": "cpu", "model_path": "./artifacts/projectile_net.pt" }
```

> **CORS** is enabled for dev so the frontend (different port) can call the API.

### Configuration

If unset, the API looks under `./artifacts/`. Override via env:

- `MODEL_PATH` — path to `projectile_net.pt`
- `SCALER_X_PATH` — path to input scaler
- `SCALER_Y_PATH` — path to target scaler

**Device** is auto-selected (**cuda** if available, else **cpu**).

### Reproducibility & Data Leakage

- Seeds **Python / NumPy / PyTorch** (deterministic cuDNN where applicable).
- **Train/val/test** split with scalers **fit on train only**; train-fitted scalers
  transform val/test to avoid leakage.
- **Best checkpoint** (by validation loss) is reloaded before test evaluation.

### Tests

`tests/` include:

- **Model forward** shape `(N,2) → (N,3)`
- **Scaler round-trip** `inverse_transform(transform(X)) ≈ X`
- **Splits** add up and are disjoint
- **Predict pipeline** returns real-unit `(N,3)` with sane values
- **API**: `/health` 200; `/predict` 200 for valid input; 400 for bad payloads

Run:
```bash
python -m pip install pytest
python -m pytest -q
```

---

## Frontend (React + Vite)

### Backend URL / Environment

The app reads the backend base URL from a Vite env variable:

- **`VITE_API_BASE`** — e.g. `http://127.0.0.1:5000`

Create a local env file in `frontend/` (not committed):

```bash
# frontend/.env.local
VITE_API_BASE=http://127.0.0.1:5000
```

If not set, the app **defaults to** `http://127.0.0.1:5000`.

### Project Structure (frontend)

```text
frontend/
├─ public/
├─ src/
│  ├─ components/
│  │  ├─ FormProjectile.jsx
│  │  ├─ StatBlock.jsx
│  │  ├─ Tiles.jsx
│  │  └─ TrajectoryPlot.jsx
│  ├─ models/
│  │  └─ index.jsx          
│  ├─ utils/
│  │  ├─ api.js            
│  │  └─ physics.js        
│  ├─ views/
│  │  ├─ Landing.jsx
│  │  └─ ModelRunner.jsx
│  ├─ App.jsx
│  ├─ ModelRoute.jsx
│  ├─ main.jsx
│  └─ index.css
├─ index.html
├─ package.json
└─ vite.config.js
```

### App Flow

1. **Landing** renders a grid of models via **`<Tiles/>`** powered by the **model registry**.
2. Clicking a tile routes to `/:modelId`. **`ModelRoute.jsx`** looks up the model config and passes it to **`ModelRunner.jsx`**.
3. **ModelRunner**:
   - renders the model **Form** (e.g., `FormProjectile.jsx`),
   - computes **analytic** baselines (via `utils/physics.js` or model-provided fns),
   - calls the backend via `utils/api.js` for **AI predictions**,
   - renders the **TrajectoryPlot** and **StatBlock**s.

### Scripts

```bash
cd frontend
npm run dev     # start Vite dev server (default http://127.0.0.1:5173/)

```

---

## Notes & Limitations

- Physics assumes **no drag** (flat ground). The NN is a surrogate for this regime.
  Extend the dataset & architecture to handle **drag/wind/sloped ground**.
- In serving, the **model and scalers are loaded once** and kept in memory for
  low-latency requests.

---

## License

**MIT** 
