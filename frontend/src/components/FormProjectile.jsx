import React, { useState } from "react";

export default function FormProjectile({
  initialV = 50,
  initialAngle = 45,
  onSubmit,
}) {
  const [velocity, setVelocity] = useState(initialV);
  const [angle, setAngle] = useState(initialAngle);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function validate(v, a) {
    const e = {};
    if (!(v > 0)) e.velocity = "Velocity must be > 0 m/s";
    if (!(a >= 1 && a <= 80)) e.angle = "Angle must be between 1° and 80°";
    return e;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const v = Number(velocity);
    const a = Number(angle);
    const eMap = validate(v, a);
    setErrors(eMap);
    if (Object.keys(eMap).length) return;
    setLoading(true);
    try {
      await onSubmit({ velocity: v, angle: a });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2 style={{ margin: 0 }}>Ideal Projectile (No Drag)</h2>
      <p className="muted">Enter inputs and compare analytic vs AI.</p>

      <div style={{ marginTop: 10 }}>
        <label className="label">Velocity (m/s)</label>
        <input
          type="number"
          className="input"
          value={velocity}
          onChange={(e) => setVelocity(e.target.value)}
          min={1}
          step="any"
        />
        {errors.velocity && <div className="error">{errors.velocity}</div>}
      </div>

      <div style={{ marginTop: 10 }}>
        <label className="label">Angle (deg)</label>
        <input
          type="number"
          className="input"
          value={angle}
          onChange={(e) => setAngle(e.target.value)}
          min={1}
          max={80}
          step="any"
        />
        {errors.angle && <div className="error">{errors.angle}</div>}
      </div>

      <div className="row" style={{ marginTop: 12 }}>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? "Predicting…" : "Simulate & Predict"}
        </button>
      </div>
    </form>
  );
}
