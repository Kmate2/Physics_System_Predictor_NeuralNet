export const getAPIBase = () =>
    import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:5000";
  
  export async function fetchJSON(path, options = {}) {
    const base = getAPIBase();
    const url = path.startsWith("http") ? path : `${base}${path}`;
    const res = await fetch(url, options);
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${res.statusText} ${text}`);
    }
    return res.json();
  }
  