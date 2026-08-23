/**
 * Central application store (Svelte 5 runes).
 *
 * A single module-level `$state` object shared by every component — the modern
 * equivalent of the original app's static modifier state + `Renamer::files`. It holds:
 *   - navigation:  currentPath, files (the directory listing)
 *   - selection:   the filenames chosen for renaming (in list order)
 *   - config:      the full modifier recipe (shape from `lib/config.js`, mirrors backend `Config.to_dict()`)
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
import { defaultConfig, sanitizeConfig } from "../config.js";

export { defaultConfig };

export const state = $state({
  currentPath: "",
  files: [], // [{ name, size, mtime }] in list order
  selection: [], // selected filenames (array; numbering re-derived in list order)
  config: defaultConfig(),
  previews: {}, // { [name]: { new_base, ext, full_new_name, changed } }
  duplicateNames: [], // original names that would clobber an existing file (row highlight)
  renaming: false,
  dialog: { open: false, title: "", message: "", variant: "info", buttons: [], dismissId: null },
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
    state.duplicateNames = [];
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

/** Navigate to the parent of the current directory (no-op at the filesystem root). */
export function goUp() {
  const p = state.currentPath.replace(/\/+$/, "");
  if (!p || p === "/") return;
  loadDir(p.split("/").slice(0, -1).join("/") || "/");
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

// --- modifier pipeline order ----------------------------------------------- #

/** Move a modifier card to a new position in `config.pipeline_order` (drag & drop). */
export function reorderModifier(from, to) {
  if (from === to || from < 0 || to < 0) return;
  const order = [...state.config.pipeline_order];
  if (from >= order.length) return;
  const [moved] = order.splice(from, 1);
  order.splice(Math.min(to, order.length), 0, moved);
  state.config.pipeline_order = order;
}

// --- preview --------------------------------------------------------------- #

/** The selected filenames in on-screen list order (the payload for check/rename/preview). */
function selectedInOrder() {
  return state.files.map((f) => f.name).filter((n) => state.selection.includes(n));
}

/** Recompute previews for the current selection (in list order) via `/api/preview`. */
export async function refreshPreview() {
  if (!state.currentPath || state.selection.length === 0) {
    state.previews = {};
    return;
  }
  const files = selectedInOrder();
  if (files.length === 0) {
    state.previews = {};
    return;
  }
  try {
    const res = await api.preview({ path: state.currentPath, files, config: sanitizeConfig(state.config) });
    state.previews = res.previews;
  } catch (e) {
    state.error = e.message || String(e);
  }
}

// --- rename workflow -------------------------------------------------------- #

/**
 * Show a modal dialog (rendered by `components/Dialog.svelte`); resolves with the
 * clicked button id, or `dismissId` when dismissed via Esc / backdrop click.
 */
export function showDialog({ title, message, variant = "info", buttons, dismissId = null }) {
  return new Promise((resolve) => {
    state.dialog = { open: true, title, message, variant, buttons, dismissId, resolve };
  });
}

/** `POST /api/check` — which of the selection would clobber an existing file. */
export async function checkDuplicates() {
  const res = await api.check({ path: state.currentPath, files: selectedInOrder(), config: sanitizeConfig(state.config) });
  state.duplicateNames = res.names; // for row highlighting in the file list
  return res; // { duplicates, names }
}

/** `POST /api/rename` — perform the renames on disk. Returns `{ renamed, errors }`. */
export async function performRename() {
  state.renaming = true;
  try {
    return await api.rename({ path: state.currentPath, files: selectedInOrder(), config: sanitizeConfig(state.config) });
  } finally {
    state.renaming = false;
  }
}
