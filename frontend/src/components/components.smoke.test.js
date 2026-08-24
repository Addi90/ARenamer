// happy-dom crashes inside Svelte 5's checkbox row mounting (null firstChild
// in its Node implementation); jsdom is the battle-tested DOM for component
// tests, so this file opts into it (installed as a dev dependency).
// @vitest-environment jsdom

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/svelte";

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
import { state } from "../lib/state/store.svelte.js";
import { setLanguage } from "../lib/i18n/index.svelte.js";
import FileList from "./FileList.svelte";
import Dialog from "./Dialog.svelte";
import RenameButton from "./RenameButton.svelte";

const FILES = [
  { name: "a.txt", size: 1, mtime: 0 },
  { name: "b.log", size: 2, mtime: 0 },
];

function resetStore() {
  state.files = [...FILES];
  state.selection = [];
  state.previews = {};
  state.duplicateNames = [];
  state.dialog = { open: false, title: "", message: "", variant: "info", buttons: [], dismissId: null };
  state.error = "";
  state.renaming = false;
  state.path = "/tmp/somewhere";
}

beforeEach(() => {
  cleanup();
  setLanguage("en");
  resetStore();
  api.listFiles.mockReset();
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

describe("RenameButton", () => {
  it("renders the rename control", () => {
    render(RenameButton);
    expect(screen.getByRole("button")).toBeTruthy();
  });

  it("runs /check and opens the confirmation dialog on click", async () => {
    state.selection = ["a.txt"];
    render(RenameButton);

    await fireEvent.click(screen.getByRole("button"));
    await new Promise((r) => setTimeout(r, 250)); // let the async check flow settle

    expect(api.check).toHaveBeenCalled();
    // No duplicates from the mocked check -> a confirmation dialog should be open.
    expect(state.dialog.open).toBe(true);
  });

  it("shows the blocking duplicate warning instead of confirming", async () => {
    state.selection = ["a.txt"];
    api.check.mockResolvedValue({ names: ["a.txt"] });
    render(RenameButton);

    await fireEvent.click(screen.getByRole("button"));
    await new Promise((r) => setTimeout(r, 250));

    expect(state.dialog.open).toBe(true);
    expect(api.rename).not.toHaveBeenCalled();
  });
});
