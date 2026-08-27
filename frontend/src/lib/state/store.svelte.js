/**
 * Central application store (Svelte 5 runes).
 *
 * A single module-level `$state` object shared by every component — the modern
 * equivalent of the original app's static modifier state + `Renamer::files`. It holds:
 *   - navigation:  currentPath, files (the directory listing: files *and* dirs)
 *   - selection:   the entry names chosen for renaming (in list order)
 *   - view:        showFiles / showDirs toggles (which entry types the list renders)
 *   - config:      the full modifier recipe (shape from `lib/config.js`, mirrors backend `Config.to_dict()`)
 *   - previews:    per-entry new-name results from `/api/preview` (keyed by name)
 *   - ui:          busy / error flags, treeVersion (bumped after renames so the
 *                  directory tree can refresh its labels)
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
  files: [], // [{ name, type: "file"|"dir", size, mtime }] in list order
  selection: [], // selected entry names (array; numbering re-derived in list order)
  showFiles: true, // view toggle: render file rows (default view = files only)
  showDirs: false, // view toggle: render directory rows
  treeVersion: 0, // bumped after renames so the directory tree can re-fetch labels
  config: defaultConfig(),
  previews: {}, // { [name]: { type, new_base, ext, full_new_name, changed } }
  duplicateNames: [], // original names that would clobber an existing entry (row highlight)
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

/** Entries currently rendered given the file/dir view toggles. */
function visibleFiles() {
  return state.files.filter((f) => (f.type === "dir" ? state.showDirs : state.showFiles));
}

/**
 * Select every *visible* entry. Hidden entries must never enter the selection —
 * they would be renamed invisibly (the Rename button counts the selection).
 */
export function selectAll() {
  state.selection = visibleFiles().map((f) => f.name);
}

export function clearSelection() {
  state.selection = [];
}

/** Drop all hidden entries from selection, previews and duplicate highlights. */
function pruneHidden() {
  const visible = new Set(visibleFiles().map((f) => f.name));
  state.selection = state.selection.filter((n) => visible.has(n));
  state.duplicateNames = state.duplicateNames.filter((n) => visible.has(n));
  state.previews = Object.fromEntries(Object.entries(state.previews).filter(([n]) => visible.has(n)));
}

/** Show/hide file rows; turning files off prunes them from the selection. */
export function setShowFiles(on) {
  if (state.showFiles === on) return;
  state.showFiles = on;
  if (!on) pruneHidden();
}

/** Show/hide directory rows; turning dirs off prunes them from the selection. */
export function setShowDirs(on) {
  if (state.showDirs === on) return;
  state.showDirs = on;
  if (!on) pruneHidden();
}

// --- modifier pipeline order ----------------------------------------------- #

/**
 * Move a modifier card to a new slot in `config.pipeline_order` (drag & drop).
 * `to` is the insertion *slot*: insert before whatever currently sits at
 * index `to` (so `to` may be `order.length`, i.e. append at the end). Slots
 * match the on-screen insertion-line indicator.
 */
export function reorderModifier(from, to) {
  if (from < 0 || to < 0) return;
  const order = [...state.config.pipeline_order];
  if (from >= order.length || to === from || to === from + 1) return;
  const [moved] = order.splice(from, 1);
  order.splice(to > from ? to - 1 : to, 0, moved);
  state.config.pipeline_order = order;
}

/** Reset the modifier order to the canonical pipeline order (undo drag & drop changes). */
export function resetModifierOrder() {
  state.config.pipeline_order = [...defaultConfig().pipeline_order];
}

// --- preview --------------------------------------------------------------- #

/** The selected entry names in on-screen list order (the payload for check/rename/preview). */
function selectedInOrder() {
  return state.files.map((f) => f.name).filter((n) => state.selection.includes(n));
}

/** Of the selection, the names that are directories (the `dirs` payload field). */
function selectedDirs() {
  const dirNames = new Set(state.files.filter((f) => f.type === "dir").map((f) => f.name));
  return selectedInOrder().filter((n) => dirNames.has(n));
}

/**
 * Payload for `/api/preview` etc.: the selected names in list order plus which of
 * them are directories (extension-less rename entries) and the sanitized config.
 */
function requestPayload() {
  return {
    path: state.currentPath,
    files: selectedInOrder(),
    dirs: selectedDirs(),
    config: sanitizeConfig(state.config),
  };
}

/** Recompute previews for the current selection (in list order) via `/api/preview`. */
export async function refreshPreview() {
  if (!state.currentPath || state.selection.length === 0) {
    state.previews = {};
    return;
  }
  if (selectedInOrder().length === 0) {
    state.previews = {};
    return;
  }
  try {
    const res = await api.preview(requestPayload());
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

/** `POST /api/check` — which of the selection would clobber an existing entry. */
export async function checkDuplicates() {
  const res = await api.check(requestPayload());
  state.duplicateNames = res.names; // for row highlighting in the file list
  return res; // { duplicates, names }
}

/** `POST /api/rename` — perform the renames on disk. Returns `{ renamed, errors }`. */
export async function performRename() {
  state.renaming = true;
  try {
    return await api.rename(requestPayload());
  } finally {
    state.renaming = false;
  }
}

/** Tell the directory tree to refresh its labels (call after a successful rename). */
export function bumpTreeVersion() {
  state.treeVersion++;
}
