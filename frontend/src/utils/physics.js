export const g = 9.81; // m/s^2

export function physicsFrom(v, deg) {
  const th = (deg * Math.PI) / 180;
  const T = (2 * v * Math.sin(th)) / g;
  const R = (v * v * Math.sin(2 * th)) / g;
  const H = (v * v * Math.sin(th) * Math.sin(th)) / (2 * g);
  return { R, H, T };
}

export function sampleTimeParam(R, H, T, N = 200) {
  if (!(R > 0) || !(H >= 0) || !(T > 0)) return [];
  const pts = [];
  for (let i = 0; i <= N; i++) {
    const t = (T * i) / N;
    const x = (R / T) * t;
    const y = 4 * H * (t / T) * (1 - t / T);
    pts.push([x, y]);
  }
  return pts;
}

export function toSvgPath(points, xScale, yScale, height) {
  if (!points.length) return "";
  const [x0, y0] = points[0];
  let d = `M ${xScale(x0)} ${height - yScale(y0)}`;
  for (let i = 1; i < points.length; i++) {
    const [x, y] = points[i];
    d += ` L ${xScale(x)} ${height - yScale(y)}`;
  }
  return d;
}

export const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
