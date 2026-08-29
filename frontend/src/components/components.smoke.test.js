// happy-dom crashes inside Svelte 5's checkbox row mounting (null firstChild
// in its Node implementation); jsdom is the battle-tested DOM for component
// tests, so this file opts into it (installed as a dev dependency).
// @vitest-environment jsdom

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/svelte";
import { createRawSnippet } from "svelte";

// Components read the module-level store and i18n directly, so tests drive
// behavior by seeding store state and (for RenameButton) mocking lib/api.js.
vi.mock("../lib/api.js", () => ({
  listFiles: vi.fn(),
  listDirs: vi.fn(),
  homeDir: vi.fn(),
  preview: vi.fn(),
  check: vi.fn(),
  rename: vi.fn(),
}));

import * as api from "../lib/api.js";
import { state, showDialog } from "../lib/state/store.svelte.js";
import { setLanguage } from "../lib/i18n/index.svelte.js";
import FileList from "./FileList.svelte";
import Dialog from "./Dialog.svelte";
import RenameButton from "./RenameButton.svelte";
import ModifierCard from "./ModifierCard.svelte";

const FILES = [
  { name: "a.txt", size: 1, mtime: 0 },
  { name: "b.log", size: 2, mtime: 0 },
];

const MIXED = [
  { name: "a.txt", type: "file", size: 1, mtime: 0 },
  { name: "Photos", type: "dir", size: 0, mtime: 0 },
  { name: "b.log", type: "file", size: 2, mtime: 0 },
  { name: "Videos", type: "dir", size: 0, mtime: 0 },
];

function resetStore() {
  state.files = [...FILES];
  state.selection = [];
  state.previews = {};
  state.duplicateNames = [];
  state.showFiles = true;
  state.showDirs = false;
  state.treeVersion = 0;
  state.dialog = { open: false, title: "", message: "", variant: "info", buttons: [], dismissId: null };
  state.error = "";
  state.renaming = false;
  state.currentPath = "/tmp/somewhere";
}

beforeEach(() => {
  cleanup();
  setLanguage("en");
  resetStore();
  api.listFiles.mockReset();
  api.listFiles.mockResolvedValue({ files: FILES });
  api.homeDir.mockReset();
  api.preview.mockReset();
  api.preview.mockResolvedValue({});
  api.check.mockReset();
  api.check.mockResolvedValue({ names: [] });
  api.rename.mockReset();
  api.rename.mockResolvedValue({ renamed: 1, errors: [] });
});

describe("FileList", () => {
  it("renders one row per file with its name", async () => {
    render(FileList);
    // Each row shows the name twice (Name + New Name preview columns), so use
    // the *All* variant of the query.
    expect(screen.getAllByText("a.txt").length).toBeGreaterThan(0);
    expect(screen.getAllByText("b.log").length).toBeGreaterThan(0);
  });

  it("reflects the current selection after toggling a row", async () => {
    render(FileList);
    // Click the Name cell (first match); rows are clickable for selection.
    const row = screen.getAllByText("a.txt")[0];
    await fireEvent.click(row);
    expect(state.selection).toContain("a.txt");
    await fireEvent.click(row);
    expect(state.selection).not.toContain("a.txt");
  });

  it("hides directory rows by default and shows them with the toggle", async () => {
    state.files = [...MIXED];
    render(FileList);
    expect(screen.queryByText("Photos")).toBeNull(); // dirs hidden by default
    expect(screen.getAllByText("a.txt").length).toBeGreaterThan(0); // files shown

    await fireEvent.click(screen.getByLabelText("Directories"));
    expect(screen.getAllByText("Photos").length).toBeGreaterThan(0); // both rows now
    expect(screen.getAllByText("Videos").length).toBeGreaterThan(0);
  });

  it("marks directory rows with a type badge", async () => {
    state.files = [...MIXED];
    state.showDirs = true;
    render(FileList);
    // Badge text ("dir") appears once per directory row.
    expect(screen.getAllByText("dir").length).toBe(2);
  });

  it("deselects hidden entries when their type is toggled off", async () => {
    state.files = [...MIXED];
    state.showDirs = true;
    state.selection = ["a.txt", "Photos", "Videos"]; // select all (visible)
    render(FileList);

    await fireEvent.click(screen.getByLabelText("Directories")); // hide dirs
    expect(state.selection).toEqual(["a.txt"]); // hidden entries pruned

    await fireEvent.click(screen.getByLabelText("Files")); // hide files too
    expect(state.selection).toEqual([]);
  });
});

describe("Dialog", () => {
  it("renders nothing while closed", () => {
    render(Dialog);
    expect(screen.queryByText("Warn")).toBeNull();
  });

  it("renders title/message/buttons when open and closes on button click", async () => {
    state.dialog = {
      open: true,
      title: "Warn",
      message: "Watch out",
      variant: "warning",
      buttons: [{ id: "abort", label: "Abort" }],
      dismissId: "abort",
    };
    render(Dialog);
    expect(screen.getByText("Warn")).toBeTruthy();
    expect(screen.getByText("Watch out")).toBeTruthy();

    await fireEvent.click(screen.getByText("Abort"));
    expect(state.dialog.open).toBe(false);
  });
});

// All mocked api calls are pre-resolved, so a single 0ms macrotask wait flushes the
// whole microtask chain (click -> store actions -> dialogs) started by the click.
const settle = () => new Promise((r) => setTimeout(r, 0));

describe("RenameButton", () => {
  it("renders the rename control with the selection count", () => {
    state.selection = ["a.txt"];
    render(RenameButton);
    const btn = screen.getByRole("button", { name: /Rename/ });
    // the count sits in a pill span, not in the button label
    expect(btn.querySelector(".pill")?.textContent).toBe("1");
  });

  it("is disabled without a selection", () => {
    state.selection = [];
    const { getByRole } = render(RenameButton);
    expect(getByRole("button").disabled).toBe(true);
  });

  it("runs /check and opens the confirmation dialog on click", async () => {
    state.selection = ["a.txt"];
    render(RenameButton);
    render(Dialog); // dialog host: RenameButton drives the store, Dialog renders it
    await fireEvent.click(screen.getByRole("button"));
    await settle();

    expect(api.check).toHaveBeenCalledTimes(1);
    // No duplicates from the mocked check -> the confirmation dialog is open.
    expect(state.dialog.open).toBe(true);
    expect(screen.getByText("Rename 1 Item(s)?")).toBeTruthy();
  });

  it("shows the blocking duplicate warning instead of confirming", async () => {
    state.selection = ["a.txt"];
    api.check.mockResolvedValue({ duplicates: 1, names: ["a.txt"] });
    render(RenameButton);
    render(Dialog); // dialog host: RenameButton drives the store, Dialog renders it
    await fireEvent.click(screen.getByRole("button"));
    await settle();

    // The warning (not the confirmation) is shown, the clobbering names are
    // stored for row highlighting, and no rename happens.
    expect(screen.getByText("Found existing entries for 1 new name(s)!")).toBeTruthy();
    expect(state.duplicateNames).toEqual(["a.txt"]);
    expect(api.rename).not.toHaveBeenCalled();
  });

  it("aborts without renaming when Abort is chosen in the confirmation", async () => {
    state.selection = ["a.txt"];
    render(RenameButton);
    render(Dialog); // dialog host: RenameButton drives the store, Dialog renders it
    await fireEvent.click(screen.getByRole("button"));
    await settle();
    await fireEvent.click(screen.getByText("Abort"));
    await settle();

    expect(state.dialog.open).toBe(false);
    expect(api.rename).not.toHaveBeenCalled();
  });

  // The core action: check → confirm → Ok → /rename → success → re-list + tree bump.
  it("renames on Ok: success dialog, re-list, tree bump", async () => {
    state.selection = ["a.txt"];
    api.check.mockResolvedValue({ duplicates: 0, names: [] });
    api.rename.mockResolvedValue({ renamed: 1, errors: [] });
    render(RenameButton);
    render(Dialog); // dialog host: RenameButton drives the store, Dialog renders it
    await fireEvent.click(screen.getByRole("button"));
    await settle();
    await fireEvent.click(screen.getByText("Ok")); // confirm
    await settle();

    expect(api.rename).toHaveBeenCalledTimes(1);
    expect(screen.getByText("Successfully renamed 1 Item(s)!")).toBeTruthy();

    await fireEvent.click(screen.getByText("Ok")); // close the success dialog
    await settle();

    expect(api.listFiles).toHaveBeenCalledTimes(1); // re-list the directory
    expect(state.treeVersion).toBe(1); // let the tree refresh labels
    expect(state.dialog.open).toBe(false);
  });

  it("notes individual failures in the success dialog", async () => {
    state.selection = ["a.txt", "b.log"];
    api.check.mockResolvedValue({ duplicates: 0, names: [] });
    api.rename.mockResolvedValue({ renamed: 1, errors: ["boom"] });
    render(RenameButton);
    render(Dialog); // dialog host: RenameButton drives the store, Dialog renders it
    await fireEvent.click(screen.getByRole("button"));
    await settle();
    await fireEvent.click(screen.getByText("Ok"));
    await settle();
    expect(screen.getByText(/1 item\(s\) could not be renamed/)).toBeTruthy();
  });

  it("shows the duplicate warning again when /rename fails with a 409", async () => {
    state.selection = ["a.txt", "b.log"];
    api.check.mockResolvedValue({ duplicates: 0, names: [] });
    api.rename.mockRejectedValue(
      new Error(JSON.stringify({ duplicates: 2, names: ["a.txt", "b.log"] }))
    );
    render(RenameButton);
    render(Dialog); // dialog host: RenameButton drives the store, Dialog renders it
    await fireEvent.click(screen.getByRole("button"));
    await settle();
    await fireEvent.click(screen.getByText("Ok")); // confirm
    await settle();

    // The 409 safety net: warning with the clobbering names, no re-list,
    // no tree bump (nothing was renamed).
    expect(state.dialog.open).toBe(true);
    expect(state.duplicateNames).toEqual(["a.txt", "b.log"]);
    expect(screen.getByText("Found existing entries for 2 new name(s)!")).toBeTruthy();
    expect(api.listFiles).not.toHaveBeenCalled();
    expect(state.treeVersion).toBe(0);
  });
});

describe("Dialog promise wiring (showDialog)", () => {
  it("resolves the pending promise with the clicked button id", async () => {
    const p = showDialog({
      title: "T",
      message: "M",
      buttons: [{ id: "ok", label: "Ok" }, { id: "abort", label: "Abort" }],
      dismissId: "abort",
    });
    render(Dialog);
    await fireEvent.click(screen.getByText("Abort"));
    await expect(p).resolves.toBe("abort");
    expect(state.dialog.open).toBe(false);
  });

  it("resolves with the dismissId on Escape", async () => {
    const p = showDialog({
      title: "T",
      message: "M",
      buttons: [{ id: "ok", label: "Ok" }],
      dismissId: "abort",
    });
    render(Dialog);
    await settle(); // the $effect registers the keydown listener asynchronously
    await fireEvent.keyDown(window, { key: "Escape" });
    await expect(p).resolves.toBe("abort");
  });
});

describe("ModifierCard (drag & drop)", () => {
  // The drop handler defers the reorder to the next frame so the browser
  // finishes the drag first — run it synchronously in the test.
  const origRaf = globalThis.requestAnimationFrame;
  beforeEach(() => {
    state.config.pipeline_order = ["replace", "case", "ifthen"];
    globalThis.requestAnimationFrame = (fn) => (fn(), 0);
  });
  afterEach(() => {
    globalThis.requestAnimationFrame = origRaf;
  });

  /** A drag event with a mock dataTransfer (jsdom's is a poor fit). */
  function dragEvent(type, data, props = {}) {
    const ev = new Event(type, { bubbles: true, cancelable: true });
    Object.defineProperty(ev, "dataTransfer", {
      value: {
        setData: vi.fn(),
        getData: vi.fn().mockReturnValue(data),
        dropEffect: null,
        effectAllowed: null,
      },
    });
    Object.assign(ev, props);
    return ev;
  }

  // Slot content as a raw snippet: a plain `() => "panel"` renders nothing, because
  // Svelte 5 snippets are side-effecting anchor renderers, not value-returning
  // functions — createRawSnippet is the programmatic equivalent of <template>.
  const panel = () => createRawSnippet(() => ({ render: () => "panel" }));

  it("renders the grip handle and the slot content; the card is only draggable while the grip is pressed", () => {
    const { container } = render(ModifierCard, {
      id: "replace",
      index: 0,
      children: panel(),
    });
    const card = container.querySelector(".card");
    expect(container.querySelector(".grip")).toBeTruthy();
    expect(screen.getByText("panel")).toBeTruthy();
    expect(card.draggable).toBe(false);
    fireEvent.mouseDown(container.querySelector(".grip"));
    expect(card.draggable).toBe(true);
  });

  it("dragstart / dragend toggle the dragging state", async () => {
    const { container } = render(ModifierCard, {
      id: "replace",
      index: 0,
      children: panel(),
    });
    const card = container.querySelector(".card");
    card.dispatchEvent(dragEvent("dragstart", null));
    await settle(); // the class:dragging update flushes asynchronously
    expect(card.className).toContain("dragging");
    card.dispatchEvent(dragEvent("dragend"));
    await settle();
    expect(card.className).not.toContain("dragging");
  });

  // jsdom rects are all 0×0, so clientY < 0 hits the "above" half and
  // clientY > 0 the "below" half of the card.
  it("a drop in the gap above this card inserts the dragged card before it", async () => {
    const { container } = render(ModifierCard, { id: "case", index: 1, children: panel() });
    const card = container.querySelector(".card");
    card.dispatchEvent(dragEvent("dragover", "ifthen", { clientX: 0, clientY: -1 }));
    await settle(); // the class:over update flushes asynchronously
    expect(card.className).toContain("over"); // the marker shows the insertion gap
    card.dispatchEvent(dragEvent("drop", "ifthen"));
    await settle();
    expect(state.config.pipeline_order).toEqual(["replace", "ifthen", "case"]);
  });

  it("a drop in the gap below this card is a no-op when the card was originally adjacent", () => {
    const { container } = render(ModifierCard, { id: "case", index: 1, children: panel() });
    const card = container.querySelector(".card");
    card.dispatchEvent(dragEvent("dragover", "ifthen", { clientX: 0, clientY: 1 }));
    card.dispatchEvent(dragEvent("drop", "ifthen"));
    // "ifthen" (index 2) into slot 2 == its original position -> unchanged
    expect(state.config.pipeline_order).toEqual(["replace", "case", "ifthen"]);
  });

  it("ignores a drop of the card onto itself", () => {
    const { container } = render(ModifierCard, { id: "case", index: 1, children: panel() });
    const card = container.querySelector(".card");
    card.dispatchEvent(dragEvent("dragover", "case", { clientX: 0, clientY: -1 }));
    card.dispatchEvent(dragEvent("drop", "case"));
    expect(state.config.pipeline_order).toEqual(["replace", "case", "ifthen"]);
  });
});
