/**
 * Thin client for the A-Renamer backend API.
 *
 * All calls hit `/api/*` (same origin in the desktop app; proxied to :8000 under
 * `npm run dev`). Errors are normalized into `Error` with the backend's detail.
 */

async function request(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const data = await res.json();
      if (data.detail !== undefined) detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch {
      /* non-JSON error body; keep the status text */
    }
    throw new Error(detail);
  }

  return res.status === 204 ? null : res.json();
}

const url = (endpoint, path) => `/api/${endpoint}?path=${encodeURIComponent(path)}`;

/** List the files (not subdirs) in a directory, sorted by name. */
export const listFiles = (path) => request("GET", url("list", path));

/** List the immediate subdirectories of a directory (for tree navigation). */
export const listDirs = (path) => request("GET", url("dirs", path));

/** The user's home directory — a sensible default starting point. */
export const homeDir = () => request("GET", "/api/home");

/** Compute per-file new-name previews for a selection under a config. */
export const preview = (payload) => request("POST", "/api/preview", payload);

/** Report which of the selection would clobber an existing file on rename. */
export const check = (payload) => request("POST", "/api/check", payload);

/** Perform the renames on disk. Throws (409) if any would clobber an existing file. */
export const rename = (payload) => request("POST", "/api/rename", payload);
