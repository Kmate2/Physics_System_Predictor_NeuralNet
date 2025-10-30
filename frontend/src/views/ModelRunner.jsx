import React from "react";
import { fetchJSON } from "../utils/api";

export default function ModelRunner({ config, onBack }) {
  const {
    title,
    Form,
    Plot,
    computePhysics,
    buildRequest,
    mapResponse,
    renderStats,
  } = config;

  const [phys, setPhys] = React.useState(null);
  const [ai, setAi] = React.useState(null);
  const [playing, setPlaying] = React.useState(false);
  const [apiError, setApiError] = React.useState("");

  async function handleSubmit(inputs) {
    const p = computePhysics(inputs);
    setPhys(p);
    setApiError("");
    setPlaying(false);
    try {
      const req = buildRequest(inputs);
      const data = await fetchJSON(req.path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req.body),
      });
      const aiVals = mapResponse(data);
      setAi(aiVals);
      setPlaying(true);
    } catch (err) {
      setApiError(String(err));
      setAi(null);
      setPlaying(false);
    }
  }

  const canSimulate = !!phys && !!ai;

  return (
    <div className="container">
      <div style={{ marginBottom: 10 }}>
        <a className="back" onClick={onBack}>
          <span style={{ fontSize: 18 }}>←</span>
          <span>Back to Home</span>
        </a>
      </div>

      <div className="shell">
        <div className="panel">
          <h2 style={{ margin: 0 }}>{title}</h2>
          <Form onSubmit={handleSubmit} />
          {apiError && (
            <div className="error" style={{ marginTop: 8 }}>
              {apiError}
            </div>
          )}
        </div>

        <div className="panel">
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div className="muted" style={{ color: "#374151" }}>
              Visualization
            </div>
            {canSimulate && (
              <div className="row">
                <button
                  className="btnGhost"
                  onClick={() => {
                    setPlaying(false);
                    setTimeout(() => setPlaying(true), 0);
                  }}
                >
                  Replay
                </button>
                <button
                  className="btnGhost"
                  onClick={() => setPlaying((p) => !p)}
                >
                  {playing ? "Pause" : "Play"}
                </button>
              </div>
            )}
          </div>

          <div style={{ marginTop: 10 }}>
            {canSimulate ? (
              <Plot phys={phys} ai={ai} playing={playing} onDone={() => {}} />
            ) : (
              <div className="muted">Submit inputs to see the simulation.</div>
            )}
          </div>

          {canSimulate && renderStats && renderStats({ phys, ai })}
        </div>
      </div>
    </div>
  );
}
