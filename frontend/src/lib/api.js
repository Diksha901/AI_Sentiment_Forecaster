function resolveApiBase() {
  const configuredBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_BACKEND_URL;
  if (configuredBase) {
    return configuredBase.replace(/\/$/, "");
  }

  if (typeof window !== "undefined") {
    const { hostname, origin } = window.location;
    const isLocalHost = hostname === "localhost" || hostname === "127.0.0.1";

    if (isLocalHost) {
      return "http://localhost:8000";
    }

    // Render convention fallback: <frontend>.onrender.com -> <frontend>-backend.onrender.com
    if (hostname.endsWith(".onrender.com") && !hostname.includes("-backend.")) {
      return `https://${hostname.replace(".onrender.com", "-backend.onrender.com")}`;
    }

    return origin;
  }

  return "http://localhost:8000";
}

export const API_BASE = resolveApiBase();

export function apiUrl(path) {
  if (!path) return API_BASE;
  if (/^https?:\/\//i.test(path)) return path;

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalizedPath}`;
}

export async function readJsonSafe(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

/**
 * Authenticated fetch wrapper.
 * - Injects Bearer token from localStorage automatically.
 * - Catches network errors (server offline / CORS) and throws a clear message.
 * - On 401, clears the stale token and redirects to /login.
 */
export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token");
  const skipAuthRedirect = options.skipAuthRedirect === true;

  const { skipAuthRedirect: _skipAuthRedirect, ...fetchOptions } = options;

  const headers = {
    ...(fetchOptions.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(apiUrl(path), {
      ...fetchOptions,
      headers,
    });
  } catch {
    // Network-level failure (server offline, CORS, DNS, etc.)
    throw new Error("Cannot reach the backend API. Check backend URL and CORS settings.");
  }

  // Token expired or missing — bounce to login
  if (response.status === 401) {
    if (!skipAuthRedirect) {
      localStorage.removeItem("token");
      localStorage.removeItem("is_admin");
      window.location.href = "/login";
      throw new Error("Session expired. Redirecting to login...");
    }
    throw new Error("Session expired. Please login again.");
  }

  return response;
}

/**
 * Convenience helper: fetch + parse JSON, throw on non-OK responses.
 */
export async function apiFetchJSON(path, options = {}) {
  const response = await apiFetch(path, options);
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      /* ignore parse error */
    }
    throw new Error(detail);
  }
  return response.json();
}

export function exportAsCsv(filename, rows) {
  if (!rows || !rows.length) return;

  const keys = Object.keys(rows[0]);
  const csv = [
    keys.join(","),
    ...rows.map((row) =>
      keys
        .map((key) => `"${String(row[key] ?? "").replace(/"/g, '""')}"`)
        .join(",")
    ),
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
