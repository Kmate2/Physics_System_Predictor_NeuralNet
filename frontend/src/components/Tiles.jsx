import React from "react";
import { Link } from "react-router-dom";
import { models } from "../models";

function isAvailable(cfg) {
  return (
    cfg.enabled !== false &&
    !!cfg.Form &&
    !!cfg.Plot &&
    !!cfg.computePhysics &&
    !!cfg.buildRequest &&
    !!cfg.mapResponse
  );
}

export default function Tiles() {
  const items = Object.values(models).sort(
    (a, b) => (a.order ?? 999) - (b.order ?? 999)
  );

  return (
    <div className="tilesRow">
      {items.map((cfg) => {
        const available = isAvailable(cfg);
        const title = cfg.tileTitle || cfg.title;
        const subtitle = cfg.tileSubtitle || "";

        return available ? (
          <Link
            key={cfg.id}
            to={`/models/${cfg.id}`}
            className="card clickable"
            aria-label={`Open ${title}`}
          >
            <div>
              <h2 style={{ margin: 0, fontSize: 18 }}>{title}</h2>
              {subtitle && <p className="muted">{subtitle}</p>}
              <p className="muted"></p>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <span className="btn">Open →</span>
            </div>
          </Link>
        ) : (
          <div key={cfg.id} aria-disabled="true" className="card disabled">
            <div>
              <h2 style={{ margin: 0, fontSize: 18 }}>{title}</h2>
              <p className="muted">MODEL COMING SOON</p>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button
                className="btn"
                style={{
                  background: "#9ca3af",
                  borderColor: "#9ca3af",
                  cursor: "not-allowed",
                }}
                disabled
              >
                Coming soon
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
