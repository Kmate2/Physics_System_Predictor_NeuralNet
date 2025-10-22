# Physics System Simulator — Frontend

A small, extensible **React + Vite** app that visualizes physics systems and compares **analytic (physics)** results with **AI model predictions**. Add new systems (pendulum, springs, etc.) by registering a form, a plot, and a few functions — **no rewiring**.

---

## Features

- **Plugin-style model registry** — drop in new models without touching the core app.
- **Analytic vs. AI comparison** — compute physics baselines and overlay AI predictions.
- **SVG plots + lightweight animation** — smooth visuals with no heavy chart libs.
- **Plain CSS** — simple styling you can theme later.

---

## Tech Stack

- React **19** + React DOM **19**
- Vite **7**
- React Router DOM **7**
- **Plain CSS** for styling

---

## Quickstart

```bash
cd frontend

npm i

npm run dev
```

By default Vite serves at [http://localhost:5173/](http://localhost:5173/).

---

## Backend URL / Environment

The app reads the backend base URL from a Vite env variable:

- **`VITE_API_BASE`** — e.g. `http://127.0.0.1:5000`

Create a local env file (not committed):

```bash
VITE_API_BASE=http://127.0.0.1:5000
```

If not set, the app **defaults to** `http://127.0.0.1:5000`.

---

## Project Structure

```text
frontend/
├─ node_modules/
├─ public/
├─ src/
│ ├─ components/
│ │ ├─ FormProjectile.jsx
│ │ ├─ StatBlock.jsx
│ │ ├─ Tiles.jsx
│ │ └─ TrajectoryPlot.jsx
│ ├─ models/
│ │ └─ index.jsx
│ ├─ utils/
│ │ ├─ api.js
│ │ └─ physics.js
│ │ ├─ Landing.jsx
│ │ └─ ModelRunner.jsx
│ ├─ App.jsx
│ ├─ main.jsx
│ ├─ ModelRoute.jsx
│ └─ index.css
├─ index.html
├─ package.json
├─ vite.config.js
└─ README.md
```

---

## App Flow

1. **Landing** (`views/Landing.jsx`) renders the home grid via **`<Tiles/>`** which is powered by the **model registry**.
2. Clicking a tile pushes the route to `/:modelId`. **`ModelRoute.jsx`** reads `:modelId`, looks it up in the registry, and passes the **model config** to **`ModelRunner.jsx`**.
3. **ModelRunner** orchestrates:

   - rendering the model **Form** (e.g., `FormProjectile.jsx`),
   - computing **analytic** baselines (via `utils/physics.js` or model-provided functions),
   - calling the backend via `utils/api.js` for **AI predictions**,
   - and rendering the **Plot** (e.g., `TrajectoryPlot.jsx`) plus **StatBlock**s.

---

## API Usage

All network calls should go through `utils/api.js` (which exports a small `fetchJSON` helper). Point the backend with `VITE_API_BASE` and implement the endpoints the models call (e.g., `/predict`). The runner passes the model’s `toApiPayload()` output directly to your API.

---

## Scripts (common)

```bash
npm run dev

npm run build
```

---

## License

**MIT** (or replace with your preferred license).
