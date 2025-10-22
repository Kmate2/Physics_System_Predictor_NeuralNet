# Projectile Surrogate — Training & Serving (Flask)

A tiny end‑to‑end project that **learns a surrogate model** for *ideal projectile motion* and **serves predictions** via a **Flask** API.

**Inputs:** velocity *(m/s)*, angle *(deg)* → **Outputs:** range *(m)*, max height *(m)*, flight time *(s)*.

The frontend can overlay the analytic parabola vs. the AI surrogate.

---

## Features

* **PyTorch** MLP (**2 → 64 → 32 → 3**), **Adam**, **early stopping**
* **scikit‑learn** `StandardScaler` for **inputs** and **targets**
* **Flask** (+ `flask-cors`) serving **/predict** and **/health**
* Reproducible training, saved **artifacts**, and **evaluation** helpers
* Lightweight data tooling with **NumPy / pandas / matplotlib**

---

## Tech Stack

* **PyTorch** — model + training loop
* **scikit‑learn** — `StandardScaler`
* **Flask** + **flask-cors** — inference API
* **NumPy / pandas / matplotlib** — data & plots

---

## Project Structure

```text
project/
  backend/
    app.py              # Flask API (inference only) – loads artifacts once
    model_def.py        # ProjectileNet architecture
    predict_utils.py    # scale → model → inverse-scale
  training/
    train.py            # main training pipeline (reproducible)
    data.py             # simulate/load dataset
    prep.py             # split_and_scale + DataLoaders (saves scalers)
    eval.py             # evaluate() + metrics + plot_history()
  artifacts/            # outputs (weights, scalers, metrics, curve, csv)
  requirements/
    serve.txt           # minimal deps to serve
    train.txt           # all deps to train (includes serve.txt)
  README.md
```

---

## Artifacts Produced

Saved to `./artifacts/` by `training/train.py`:

* `projectile_net.pt` — model weights (`state_dict`)
* `projectile_scaler_X.pkl` — input `StandardScaler`
* `projectile_scaler_y.pkl` — target `StandardScaler`
* `projectile_metrics.json` — config, best epoch, test **RMSE/MAE** (real units)
* `training_curve.png` — train/val loss vs. epoch
* `projectile_dataset.csv` — generated if missing

---

## Quickstart

### 1) Install (training)

```bash
cd project
python -m pip install -r requirements/train.txt
```

### 2) Train (writes artifacts into `./artifacts/`)

```bash
 python -m training.train
```

### 3) Serve the model (Flask API)

```bash
cd project(if not there already)
python -m pip install -r requirements/serve.txt

python  flask --app backend.app run
```

### 4) Try it

```bash
curl -X POST http://localhost:5000/predict \
  -H 'Content-Type: application/json' \
  -d '{"velocity":50, "angle_deg":45}'
```

**Response:**

```json
{
  "prediction": {
    "range_m": 188.2,
    "max_height_m": 41.3,
    "flight_time_s": 5.4
  }
}
```

**Health check:**

```bash
curl http://localhost:5000/health
```

---

## API (single input only)

### POST `/predict`

**Body**

```json
{ "velocity": 50.0, "angle_deg": 45.0 }
```

**Returns**

```json
{ "prediction": { "range_m": 0.0, "max_height_m": 0.0, "flight_time_s": 0.0 } }
```

### GET `/health`

Returns a status payload like:

```json
{ "status": "ok", "device": "cpu|cuda", "model_path": "./artifacts/projectile_net.pt" }
```

> **CORS** is enabled for dev so a browser UI on another port can call the API.

---

##️ Configuration

If no env vars are set, the API uses defaults relative to `project/artifacts/`.
Override with:

* `MODEL_PATH`
* `SCALER_X_PATH`
* `SCALER_Y_PATH`

**Device** is auto‑selected (**cuda** if available else **cpu**).

---

## Reproducibility & Data Leakage

* `training/train.py` seeds **Python / NumPy / PyTorch** (deterministic cuDNN flags).
* **Train/val/test** split with scalers **fit on train only**; train‑fitted scalers transform val/test to avoid leakage.
* **Best checkpoint** (by validation loss) is reloaded before test evaluation.

---

## Tests (pytest)

`tests/`:

* **Model forward** shape `(N,2) → (N,3)`
* **Scaler round‑trip** `inverse_transform(transform(X)) ≈ X`
* **Splits** add up and are disjoint
* **Predict pipeline** returns real‑unit `(N,3)` and sane values
* **API**: `/health` 200; `/predict` 200 for valid input; 400 for bad payloads

**Run:**

```bash
cd project
python -m pip install pytest
python -m pytest -q      
 ```

---

##Notes & Limitations

* Physics assumes **no drag**. The NN is a surrogate; extend the dataset & architecture to handle **drag/wind/sloped ground**.
* In serving, the **model/scalers are loaded once** and kept in memory for low‑latency requests.

---

## License

**MIT**