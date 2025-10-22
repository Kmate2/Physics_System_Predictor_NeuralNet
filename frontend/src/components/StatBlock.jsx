import React from "react";

export default function StatBlock({ title, R, H, T }) {
  return (
    <div className="statCard">
      <div className="statLabel">{title}</div>
      <div>
        <span className="statLabel">Range:</span>{" "}
        <span className="statValue">{R.toFixed(1)}</span> m
      </div>
      <div>
        <span className="statLabel">Max height:</span>{" "}
        <span className="statValue">{H.toFixed(1)}</span> m
      </div>
      <div>
        <span className="statLabel">Flight time:</span>{" "}
        <span className="statValue">{T.toFixed(2)}</span> s
      </div>
    </div>
  );
}
