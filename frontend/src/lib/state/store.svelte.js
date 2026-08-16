/**
 * Central application store (Svelte 5 runes).
 *
 * A single module-level `$state` object shared by every component — the modern
 * equivalent of the original app's static modifier state + `Renamer::files`. It holds:
 *   - navigation:  currentPath, files (the directory listing)
 *   - selection:   the filenames chosen for renaming (in list order)
 *   - config:      the full modifier recipe (mirrors backend `Config.to_dict()`)
 *   - previews:    per-file new-name results from `/api/preview` (keyed by name)
 *   - ui:          busy / error flags
 *
 * The exported functions are the only way components mutate state, so behavior stays
 * consistent. Live preview is triggered reactively from `App.svelte` (see the `$effect`
 * there) whenever config or selection changes.
 */

// Note: `$state` is a Svelte 5 rune (global, not imported) — which is why this
// file uses the `.svelte.js` extension so the Svelte plugin compiles it.
import * as api from "../api.js";

/** A fresh, all-disabled modifier config matching the backend's `Config.to_dict()`. */
export function defaultConfig() {
  return {
    add: { enabled: false, prefix: "", suffix: "", insert: "", pos: 0 },
    ifthen: {
      enabled: false,
      mode: "contains", // "contains" | "not_contains"
      expression: "",
      regex: false,
      case_sensitive: true,
      action: "prefix", // "prefix" | "insert" | "suffix"
      string: "",
      pos: 0,
    },
    replace: { enabled: false, search: "", replacement: "", regex: false, case_sensitive: true },
    remove: { enabled: false, first_n: 0, last_n: 0, range_enabled: false, start: 1, end: 1, until_end: false },
    counting: { enabled: false, position: "suffix", start_num: 1, padding: 0, insert_pos: 0 },
    date: { enabled: false, format: "YYYY-MM-DD", separator: "-", source: "today", custom_date: "", position: "suffix", pos: 0 },
  };
}

export const state = $state({
  currentPath: "",
  files: [], // [{ name, size, mtime }] in list order
  selection: [], // selected filenames (array; numbering re-derived in list order)
  config: defaultConfig(),
  previews: {}, // { [name]: { new_base, ext, full_new_name, changed } }
  busy: false,
  error: "",
});

// --- navigation / browsing ------------------------------------------------- #

/** Load a directory into the file list (re-rooting clears the selection). */
export async function loadDir(path) {
  if (!path) return;
  state.busy = true;
  state.error = "";
  try {
    const res = await api.listFiles(path);
    state.currentPath = path;
    state.files = res.files;
    state.selection = [];
    state.previews = {};
  } catch (e) {
    state.error = e.message || String(e);
  } finally {
    state.busy = false;
  }
}

/** Load the user's home directory (default starting point). */
export async function openHome() {
  try {
    const res = await api.homeDir();
    await loadDir(res.path);
  } catch (e) {
    state.error = e.message || String(e);
  }
}

// --- selection ------------------------------------------------------------- #

export function toggleSelect(name) {
  const i = state.selection.indexOf(name);
  if (i >= 0) state.selection.splice(i, 1); // was selected -> deselect
  else state.selection.push(name); // wasn't selected -> select
}

export function selectAll() {
  state.selection = state.files.map((f) => f.name);
}

export function clearSelection() {
  state.selection = [];
}

// --- preview --------------------------------------------------------------- #

/** Recompute previews for the current selection (in list order) via `/api/preview`. */
export async function refreshPreview() {
  if (!state.currentPath || state.selection.length === 0) {
    state.previews = {};
    return;
  }
  const selectedInOrder = state.files.map((f) => f.name).filter((n) => state.selection.includes(n));
  if (selectedInOrder.length === 0) {
    state.previews = {};
    return;
  }
  try {
    const res = await api.preview({ path: state.currentPath, files: selectedInOrder, config: state.config });
    state.previews = res.previews;
  } catch (e) {
    state.error = e.message || String(e);
  }
}
