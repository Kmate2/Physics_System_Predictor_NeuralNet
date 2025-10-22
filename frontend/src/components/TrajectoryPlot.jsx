import React, { useEffect, useMemo, useRef, useState } from "react";
import { sampleTimeParam, toSvgPath, clamp } from "../utils/physics";

export default function TrajectoryPlot({ phys, ai, playing, onDone }) {
  const width = 900,
    height = 480,
    padding = 56;

  const maxR = Math.max(phys?.R || 0, ai?.R || 0, 1);
  const maxH = Math.max(phys?.H || 0, ai?.H || 0, 1);

  const xScale = (x) => padding + (x / maxR) * (width - 2 * padding);
  const yScale = (y) => padding + (y / maxH) * (height - 2 * padding);

  const physPts = useMemo(
    () => sampleTimeParam(phys?.R, phys?.H, phys?.T),
    [phys]
  );
  const aiPts = useMemo(() => sampleTimeParam(ai?.R, ai?.H, ai?.T), [ai]);

  const physPath = useMemo(
    () => toSvgPath(physPts, xScale, yScale, height),
    [physPts]
  );
  const aiPath = useMemo(
    () => toSvgPath(aiPts, xScale, yScale, height),
    [aiPts]
  );

  const [t, setT] = useState(0);
  const reqRef = useRef(null),
    startRef = useRef(null);
  const Tmax = Math.max(phys?.T || 0, ai?.T || 0);

  useEffect(() => {
    if (!playing || !(Tmax > 0)) return;
    startRef.current = null;
    const step = (ts) => {
      if (startRef.current == null) startRef.current = ts;
      const elapsed = (ts - startRef.current) / 1000;
      const tNow = Math.min(elapsed, Tmax);
      setT(tNow);
      if (tNow < Tmax) reqRef.current = requestAnimationFrame(step);
      else onDone && onDone();
    };
    reqRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(reqRef.current);
  }, [playing, Tmax, onDone]);

  const physPos = useMemo(() => {
    if (!phys || !(phys.T > 0)) return null;
    const tp = clamp(t, 0, phys.T);
    const x = (phys.R / phys.T) * tp;
    const y = 4 * phys.H * (tp / phys.T) * (1 - tp / phys.T);
    return [xScale(x), height - yScale(y)];
  }, [t, phys]);

  const aiPos = useMemo(() => {
    if (!ai || !(ai.T > 0)) return null;
    const tp = clamp(t, 0, ai.T);
    const x = (ai.R / ai.T) * tp;
    const y = 4 * ai.H * (tp / ai.T) * (1 - tp / ai.T);
    return [xScale(x), height - yScale(y)];
  }, [t, ai]);

  return (
    <svg
      width={width}
      height={height}
      style={{ width: "100%", height: "auto" }}
    >
      <line
        x1={padding}
        y1={height - padding}
        x2={width - padding}
        y2={height - padding}
        stroke="#e5e7eb"
      />
      <line
        x1={padding}
        y1={height - padding}
        x2={padding}
        y2={padding}
        stroke="#e5e7eb"
      />
      <text x={width / 2} y={height - 12} textAnchor="middle" fontSize="12">
        Distance x (m)
      </text>
      <text
        x={18}
        y={height / 2}
        transform={`rotate(-90 18 ${height / 2})`}
        textAnchor="middle"
        fontSize="12"
      >
        Height y (m)
      </text>

      {/* Curves */}
      {physPath && (
        <path d={physPath} stroke="#111827" strokeWidth={2} fill="none" />
      )}
      {aiPath && (
        <path
          d={aiPath}
          stroke="#2563eb"
          strokeWidth={2}
          fill="none"
          strokeDasharray="6 4"
        />
      )}

      {/* Moving dots */}
      {physPos && (
        <circle cx={physPos[0]} cy={physPos[1]} r={6} fill="#111827" />
      )}
      {aiPos && <circle cx={aiPos[0]} cy={aiPos[1]} r={6} fill="#2563eb" />}

      {/* Legend */}
      <g transform={`translate(${padding}, ${padding - 16})`}>
        <rect x={0} y={-12} width={240} height={26} fill="white" />
        <line x1={10} y1={2} x2={40} y2={2} stroke="#111827" strokeWidth={2} />
        <text x={48} y={6} fontSize="12">
          Physics
        </text>
        <line
          x1={120}
          y1={2}
          x2={150}
          y2={2}
          stroke="#2563eb"
          strokeWidth={2}
          strokeDasharray="6 4"
        />
        <text x={158} y={6} fontSize="12">
          AI
        </text>
      </g>
    </svg>
  );
}
