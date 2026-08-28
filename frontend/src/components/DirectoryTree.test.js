// @vitest-environment jsdom
// Regression tests for the directory tree:
//  1. nodes must expand to arbitrary depth and STAY expanded (an effect that
//     tracked `refreshLoaded`'s deep node reads used to re-run forever and
//     replace child nodes with fresh collapsed ones, so the tree collapsed to
//     its first level — "you can go to adrian, but repos never shows up");
//  2. a treeVersion bump (after a rename) refreshes labels and keeps the
//     expansion of entries whose name survives the rename.
import { afterEach, describe, expect, it, vi } from "vitest";
import { mount } from "svelte";
import DirectoryTree from "./DirectoryTree.svelte";

// Fake filesystem: /home -> adrian -> repos -> arenamer
const dirs = {
  "/home": ["/home/adrian"],
  "/home/adrian": ["/home/adrian/repos"],
  "/home/adrian/repos": ["/home/adrian/repos/arenamer"],
};

vi.mock("../lib/api.js", () => ({
  homeDir: async () => ({ path: "/home" }),
  listDirs: async (path) => ({ path, dirs: (dirs[path] || []).map((p) => ({ name: p.split("/").pop(), path: p })) }),
  listFiles: async (path) => ({ path, files: [] }),
  preview: async () => ({ path: "", previews: {} }),
  check: async () => ({ duplicates: 0, names: [] }),
  rename: async () => ({ renamed: 0, errors: [] }),
}));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// jsdom does not implement scrollIntoView; stub it so TreeNode's scroll effect works.
if (!Element.prototype.scrollIntoView) Element.prototype.scrollIntoView = () => {};

const rows = () => [...document.querySelectorAll(".label")].map((b) => b.textContent);
function twistyFor(name) {
  const row = [...document.querySelectorAll(".row")].find((r) => r.querySelector(".label")?.textContent === name);
  return row ? row.querySelector(".twisty") : null;
}
function ensureExpanded(name) {
  const t = twistyFor(name);
  expect(t, `twisty for ${name}`).toBeTruthy();
  if (t.getAttribute("aria-label") === "Expand") t.click();
}

afterEach(() => {
  document.body.innerHTML = "";
});

describe("DirectoryTree depth", () => {
  it("expands and keeps open to depth 3", async () => {
    const { state } = await import("../lib/state/store.svelte.js");
    state.currentPath = "/home";
    mount(DirectoryTree, { target: document.body });
    await sleep(100);

    // root auto-expands on mount -> depth 1 visible
    expect(rows()).toContain("home");
    expect(rows()).toContain("adrian");

    // expand depth 1 -> depth 2 appears
    ensureExpanded("adrian");
    await sleep(150);
    expect(rows()).toContain("repos");

    // expand depth 2 -> depth 3 appears
    ensureExpanded("repos");
    await sleep(150);
    expect(rows()).toContain("arenamer");

    // the regression: effect churn used to replace child nodes with fresh
    // collapsed objects, collapsing the tree after a moment. Give it time.
    await sleep(400);
    expect(rows()).toContain("adrian");
    expect(rows()).toContain("repos");
    expect(rows()).toContain("arenamer");
    expect(twistyFor("adrian").getAttribute("aria-label")).toBe("Collapse");
    expect(twistyFor("repos").getAttribute("aria-label")).toBe("Collapse");
  }, 10000);

  it("refreshes labels after a treeVersion bump, keeping surviving expansions", async () => {
    const { state, bumpTreeVersion } = await import("../lib/state/store.svelte.js");
    state.currentPath = "/home";
    mount(DirectoryTree, { target: document.body });
    await sleep(100);
    ensureExpanded("adrian");
    await sleep(150);
    expect(rows()).toContain("repos");

    // "rename" the repos dir in the fake fs, then tell the tree to refresh
    dirs["/home/adrian"] = ["/home/adrian/myrepos"];
    bumpTreeVersion();
    await sleep(200);

    // the renamed dir shows under its new name; its old (non-surviving) subtree
    // is collapsed, but the parent (adrian) kept its expansion
    expect(rows()).toContain("myrepos");
    expect(rows()).not.toContain("repos");
    expect(rows()).not.toContain("arenamer"); // renamed entry starts collapsed
    expect(twistyFor("adrian").getAttribute("aria-label")).toBe("Collapse");
  }, 10000);
});