import { describe, it, expect, vi, beforeEach } from "vitest";

// The store talks to the backend only through lib/api.js — mock it so tests
// run fully offline and deterministically.
vi.mock("../api.js", () => ({
  listFiles: vi.fn(),
  listDirs: vi.fn(),
  homeDir: vi.fn(),
  preview: vi.fn(),
  check: vi.fn(),
  rename: vi.fn(),
}));

import * as api from "../api.js";
import { sanitizeConfig } from "../config.js";

// `state` is a module-level $state singleton — every test gets a fresh module
// (and therefore fresh state) via resetModules + dynamic import.
async function freshStore() {
  vi.resetModules();
  const store = await import("./store.svelte.js");
  api.listFiles.mockReset();
  api.homeDir.mockReset();
  api.preview.mockReset();
  api.check.mockReset();
  api.rename.mockReset();
  return store;
}

const FILES = [
  { name: "a.txt", size: 1, mtime: 0 },
  { name: "b.log", size: 2, mtime: 0 },
  { name: "c.md", size: 3, mtime: 0 },
];

// A mixed listing: entries carry `type` ("file" | "dir") since /api/list
// returns both kinds; the view toggles decide which are rendered.
const MIXED = [
  { name: "a.txt", type: "file", size: 1, mtime: 0 },
  { name: "Photos", type: "dir", size: 0, mtime: 0 },
  { name: "b.log", type: "file", size: 2, mtime: 0 },
  { name: "Videos", type: "dir", size: 0, mtime: 0 },
];

beforeEach(() => {
  vi.resetModules();
});

describe("selection", () => {
  it("toggleSelect adds and removes files", async () => {
    const { state, toggleSelect } = await freshStore();
    state.files = [...FILES];

    toggleSelect("a.txt");
    expect(state.selection).toContain("a.txt");
    toggleSelect("c.md");
    expect(state.selection).toContain("c.md");

    toggleSelect("a.txt"); // toggles off
    expect(state.selection).not.toContain("a.txt");
    expect(state.selection).toContain("c.md");
  });

  it("selectAll selects every file in list order; clearSelection empties", async () => {
    const { state, selectAll, clearSelection } = await freshStore();
    state.files = [...FILES];

    selectAll();
    expect(state.selection).toEqual(["a.txt", "b.log", "c.md"]);

    clearSelection();
    expect(state.selection).toEqual([]);
  });
});

describe("pipeline order", () => {
  it("starts with the canonical order", async () => {
    const { state } = await freshStore();
    expect(state.config.pipeline_order).toEqual([
      "replace", "case", "ifthen", "remove", "add", "counting", "date",
    ]);
  });

  it("reorderModifier moves an entry (no loss, no reorder off the top)", async () => {
    const { state, reorderModifier } = await freshStore();
    reorderModifier(0, 2); // move "replace" (index 0) further down
    const order = state.config.pipeline_order;
    expect(order).toHaveLength(7);
    expect(new Set(order).size).toBe(7); // permutation — nothing lost
    expect(order[0]).toBe("case"); // "replace" left the top spot
  });

  it("resetModifierOrder restores the canonical order", async () => {
    const { state, reorderModifier, resetModifierOrder } = await freshStore();
    const canonical = [...state.config.pipeline_order];
    reorderModifier(0, 5);
    expect(state.config.pipeline_order).not.toEqual(canonical);

    resetModifierOrder();
    expect(state.config.pipeline_order).toEqual(canonical);
  });
});

describe("dialogs", () => {
  it("showDialog sets open, title, message, variant and buttons", async () => {
    const { state, showDialog } = await freshStore();
    expect(state.dialog.open).toBe(false);

    showDialog({
      title: "T",
      message: "M",
      variant: "warning",
      buttons: [{ id: "abort", label: "Abort" }],
      dismissId: "abort",
    });
    expect(state.dialog).toMatchObject({
      open: true,
      title: "T",
      message: "M",
      variant: "warning",
      dismissId: "abort",
    });
    expect(state.dialog.buttons).toHaveLength(1);
  });

  it("defaults variant to info", async () => {
    const { state, showDialog } = await freshStore();
    showDialog({ title: "T", message: "M" });
    expect(state.dialog.variant).toBe("info");
  });
});

describe("api-backed flows (mocked api)", () => {
  it("loadDir populates files from the listing", async () => {
    const { state, loadDir } = await freshStore();
    api.listFiles.mockResolvedValue({ files: FILES });

    await loadDir("/tmp/somewhere");
    expect(api.listFiles).toHaveBeenCalledWith("/tmp/somewhere");
    expect(state.files.map((f) => f.name)).toEqual(["a.txt", "b.log", "c.md"]);
    expect(state.error).toBe("");
  });

  it("loadDir records the error message on failure", async () => {
    const { state, loadDir } = await freshStore();
    api.listFiles.mockRejectedValue(new Error("no such directory"));

    await loadDir("/nope");
    expect(state.error).toContain("no such directory");
  });

  it("refreshPreview calls /preview with the selected names (list order) and stores the result", async () => {
    const { state, toggleSelect, refreshPreview } = await freshStore();
    state.files = [...FILES];
    state.currentPath = "/tmp/somewhere";
    toggleSelect("a.txt");
    const canned = { "a.txt": { name: "a.txt", new_base: "A", ext: ".txt" } };
    api.preview.mockResolvedValue({ previews: canned });

    await refreshPreview();
    expect(api.preview).toHaveBeenCalledTimes(1);
    const payload = api.preview.mock.calls[0][0];
    // The /preview contract: names as plain strings in list order, plus the
    // sanitized config (Svelte may have left number fields as null).
    expect(payload.files).toEqual(["a.txt"]);
    expect(payload.config).toEqual(sanitizeConfig(state.config));
    expect(state.previews).toEqual(canned);
  });

  it("checkDuplicates stores the clobbering names", async () => {
    const { state, toggleSelect, checkDuplicates } = await freshStore();
    state.files = [...FILES];
    state.currentPath = "/tmp/somewhere";
    toggleSelect("a.txt");
    api.check.mockResolvedValue({ names: ["a.txt"] });

    await checkDuplicates();
    expect(api.check).toHaveBeenCalledTimes(1);
    expect(state.duplicateNames).toEqual(["a.txt"]);
  });

  it("performRename calls /rename and clears the renaming flag", async () => {
    const { state, toggleSelect, performRename } = await freshStore();
    state.files = [...FILES];
    state.currentPath = "/tmp/somewhere";
    toggleSelect("a.txt");
    api.rename.mockResolvedValue({ renamed: 1, errors: [] });

    await performRename();
    expect(api.rename).toHaveBeenCalledTimes(1);
    expect(state.renaming).toBe(false);
  });
});

describe("view toggles (files / directories)", () => {
  it("defaults: files shown, dirs hidden (historical view)", async () => {
    const { state } = await freshStore();
    expect(state.showFiles).toBe(true);
    expect(state.showDirs).toBe(false);
  });

  it("selectAll only selects the visible entries", async () => {
    const { state, selectAll } = await freshStore();
    state.files = [...MIXED];
    selectAll();
    expect(state.selection).toEqual(["a.txt", "b.log"]); // dirs hidden by default
  });

  it("selectAll includes dirs once they are shown", async () => {
    const { state, setShowDirs, selectAll } = await freshStore();
    state.files = [...MIXED];
    setShowDirs(true);
    selectAll();
    expect(state.selection).toEqual(["a.txt", "Photos", "b.log", "Videos"]);
  });

  it("enabling a type does not change the existing selection", async () => {
    const { state, setShowDirs, selectAll } = await freshStore();
    state.files = [...MIXED];
    selectAll();
    setShowDirs(true);
    expect(state.selection).toEqual(["a.txt", "b.log"]); // untouched
  });

  it("disabling a type prunes it from selection, previews and duplicates", async () => {
    const { state, setShowDirs, setShowFiles, selectAll } = await freshStore();
    state.files = [...MIXED];
    setShowDirs(true);
    selectAll();
    state.previews = { "a.txt": {}, Photos: {}, "b.log": {}, Videos: {} };
    state.duplicateNames = ["Photos"];

    setShowFiles(false);
    expect(state.selection).toEqual(["Photos", "Videos"]);
    expect(Object.keys(state.previews).sort()).toEqual(["Photos", "Videos"]);
    expect(state.duplicateNames).toEqual(["Photos"]);

    setShowDirs(false); // prune the last visible type
    expect(state.selection).toEqual([]);
    expect(state.previews).toEqual({});
    expect(state.duplicateNames).toEqual([]);
  });

  it("api payloads carry the dirs field (selected dirs only)", async () => {
    const { state, toggleSelect, refreshPreview } = await freshStore();
    state.files = [...MIXED];
    state.currentPath = "/tmp/somewhere";
    toggleSelect("a.txt");
    toggleSelect("Photos");
    api.preview.mockResolvedValue({ previews: {} });

    await refreshPreview();
    const payload = api.preview.mock.calls[0][0];
    expect(payload.files).toEqual(["a.txt", "Photos"]); // list order
    expect(payload.dirs).toEqual(["Photos"]); // only the directory names
  });

  it("performRename payload carries the dirs field", async () => {
    const { state, toggleSelect, performRename } = await freshStore();
    state.files = [...MIXED];
    state.currentPath = "/tmp/somewhere";
    toggleSelect("b.log");
    toggleSelect("Videos");
    api.rename.mockResolvedValue({ renamed: 0, errors: [] });

    await performRename();
    const payload = api.rename.mock.calls[0][0];
    expect(payload.files).toEqual(["b.log", "Videos"]);
    expect(payload.dirs).toEqual(["Videos"]);
  });

  it("bumpTreeVersion increments treeVersion", async () => {
    const { state, bumpTreeVersion } = await freshStore();
    const before = state.treeVersion;
    bumpTreeVersion();
    expect(state.treeVersion).toBe(before + 1);
  });
});
