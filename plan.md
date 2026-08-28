# Plan: Directory (folder) renaming + show/hide toggles

Branch: `feat/folder-editing` (checked out).

## Goal

Today only *files* are listed and can be selected/renamed. Extend the app so that
**directories are first-class entries**: they show up in the file list, can be
selected, and are transformed by the exact same seven modifiers. The list view gets
two toggles — **show files** / **show directories**. Default: files shown,
directories hidden (i.e. the default view is exactly today's behavior).

## Key design decisions

1. **Typed entries from `/api/list`.** The list endpoint returns *both* files and
   subdirectories, each entry gaining `type: "file" | "dir"` (dirs report
   `size: 0`, real `mtime`). Filtering is done **client-side** by the two view
   toggles — no extra requests, instant toggling. Backend stays authoritative
   about what exists; the UI only filters visibility.
2. **Engine: directories have no extension.** New `RenameFile.is_dir: bool`.
   For directories `base = name` and `ext = ""` *always* — a dir named
   `backup.tar` renames to `x_backup.tar` (whole name is the base). The
   file rule (split at last dot) is unchanged. All seven modifiers then work
   unchanged, since they operate on `base`.
3. **Request contract extension (backward compatible).** Preview/check/rename
   requests gain an optional `dirs: list[str]` (names in `files` that are
   directories). `files` still carries *all* selected names **in on-screen
   list order**, so numbering/rows keep following list order, now across a
   mixed file+dir selection. Omitted `dirs` ⇒ everything is a file (old
   clients/tests keep working).
4. **Duplicate detection covers cross-type collisions.** `os.path.exists(target)`
   already returns true whether the target is a file *or* a directory, so the
   existing safety net catches dir→existing-file, dir→existing-dir and
   file→existing-dir. No engine change needed beyond `is_dir` bookkeeping;
   document it in §4.
5. **Selection safety.** "Select all" selects only *visible* entries; toggling a
   type off **prunes** its entries from the selection (hidden entries must never
   be renamed invisibly).
6. **Dialog copy generalizes** "File(s)" → "Item(s)" (selection may mix files and
   dirs); i18n gets fresh keys in en + de (identical key sets, per convention).
7. **Tree stays as-is, refreshed after rename.** The directory tree uses the
   unchanged `/api/dirs`. Renaming a dir makes cached tree node labels stale,
   so the store bumps a `treeVersion`; the tree re-fetches children of its
   loaded nodes (cheap, keeps labels fresh).
8. **Default view = files only.** `showFiles: true`, `showDirs: false` in the
   store — a *view* preference, not modifier config, so it does **not** enter
   `config.js`/`defaultConfig()` (that shape must mirror the backend recipe).

## API surface (after this work)

| Endpoint | Change |
|---|---|
| `GET /api/list` | returns files **and** dirs; entries gain `type` (`"file"`/`"dir"`) |
| `GET /api/dirs` | unchanged (tree navigation) |
| `POST /api/preview` | request: + optional `dirs: []`; response item: + `type` |
| `POST /api/check` | request: + optional `dirs: []` |
| `POST /api/rename` | request: + optional `dirs: []`; `renamed` counts files **and** dirs |

## Milestones & commit plan

Five commits, one per concern (all `feat`/`docs` conventional types ⇒ release
tooling bumps **minor**). Each commit leaves `./do test` green (pytest + vitest).

### M1 — Engine: directory-aware rename core
**Commit: `feat(engine): support renaming directories as extension-less entries`**

- `backend/engine/models.py`
  - `RenameFile.is_dir: bool = False`; `__post_init__`/`set_name` apply the
    no-extension rule for dirs; `new_full_name` unchanged (empty ext).
- `backend/engine/pipeline.py`
  - `build_files(path, names, dirs=None)` — `dirs` = names marked as
    directories (list or set; `row` = position in `names`).
  - `preview()` result items gain `"type": "file" | "dir"`.
- `backend/engine/__init__.py` — docstring note (exports unchanged:
  `build_files` signature stays source-compatible).
- **Tests** `tests/backend/test_engine.py` — new `TestDirectories` class:
  - dir with dot in name → `base == name`, `ext == ""` (`backup.tar` → `x_backup.tar`);
  - `build_files(..., dirs=[...])` marks only the named entries; row order preserved;
  - preview of a dir (add prefix / case / remove: remove acts on the *full* name);
  - numbering across a **mixed** files+dirs selection follows combined list order;
  - date modifier reads a real directory's mtime (`tmp_path`);
  - If-Then condition tests the full dir name (original base);
  - `find_duplicates` on tmp dirs: dir→existing dir **and** dir→existing file both detected;
  - `perform_rename` actually renames a dir (content preserved), returns `renamed` count;
  - `set_name` re-derives base (no ext) after rename.
  - Existing tests untouched (files keep old behavior).

### M2 — API: typed listing + `dirs` in rename workflow
**Commit: `feat(api): list directories with type, accept `dirs` in preview/check/rename`**

- `backend/api/schemas.py` — `FileEntry.type: str = "file"`; `PreviewItem.type`;
  `dirs: list[str] = Field(default_factory=list)` on the three POST requests.
- `backend/api/routes.py`
  - `/list` includes subdirs (stat each entry; dir ⇒ `type="dir"`, `size=0`).
  - `/preview`, `/check`, `/rename` pass `dirs` through to `build_files`.
- **Tests** `tests/backend/test_api.py`:
  - `/list` returns dirs with `type` + files with `type`, both sorted by name;
  - `/preview` with `dirs` (dir preview is extension-less);
  - `/check` collision matrix: dir→existing dir, dir→existing file, file→existing dir;
  - `/rename` on a dir succeeds (dir + content present), unchanged-dir is a no-op;
  - `/rename` refuses (409) a dir rename onto an existing file;
  - backward compat: requests **without** `dirs` still work (existing tests cover it).

### M3 — Frontend store + client + i18n
**Commit: `feat(frontend): show/hide toggles for files and directories in the store`**

- `frontend/src/lib/api.js` — `listFiles` docs/shape note (typed entries);
  preview/check/rename payloads carry `dirs`.
- `frontend/src/lib/state/store.svelte.js`
  - `state.files` entries now `{name, type, size, mtime}`.
  - new state: `showFiles: true`, `showDirs: false`, `treeVersion: 0`.
  - new actions: `toggleShowFiles()` / `toggleShowDirs()` (toggling off prunes
    that type from `selection`); `bumpTree()`.
  - derived `visibleFiles` (filter by toggles); `selectAll()` selects visible
    entries only; `selectedInOrder()` + `selectedDirs()`; preview/check/rename
    send `{path, files, dirs, config}`.
  - after successful rename flow the store bumps `treeVersion` (RenameButton
    triggers it via the existing `loadDir` + a new call, M4 wires the tree).
- `frontend/src/lib/i18n/en.js` + `de.js` (identical key sets):
  - `fileList.showFiles`, `fileList.showDirs`, `fileList.dirBadge`,
    `fileList.emptyDirs` (empty state when all toggles off / no matches);
  - rename dialog copy: `File(s)` → `Item(s)` (`rename.confirmMsg`,
    `rename.successMsg`, `rename.errorNote`, `rename.dupMsg`), de equivalents.
- **Tests** `frontend/src/lib/state/store.svelte.test.js`:
  - `loadDir` keeps typed entries;
  - `selectAll` respects toggles (dirs hidden ⇒ only files selected);
  - turning `showFiles` off prunes selected files (and keeps dirs selection if shown);
  - preview/check/rename payloads include the `dirs` subset in list order;
  - `toggleShow*` defaults are files-on/dirs-off.

### M4 — Frontend UI: toggles, dir rows, tree refresh
**Commit: `feat(frontend): directory rows with type badge, view toggles, tree refresh`**

- `frontend/src/components/FileList.svelte`
  - toolbar: two checkbox-style toggles (Files / Directories), default checked
    state per M3; `allSelected` computed over **visible** entries.
  - rows: folder glyph/badge on dir entries (monospace-safe icon or `📁`);
    empty-state text adapts to active toggles.
- `frontend/src/components/DirectoryTree.svelte` — watch
  `appState.treeVersion`; on bump, re-fetch children of all loaded nodes
  (keeps renamed dir labels fresh). Small: keep a node registry in the
  component.
- `frontend/src/components/RenameButton.svelte` — no logic change (copy comes
  from i18n, M3); success flow triggers `bumpTree()` + `loadDir`.
- **Tests** `frontend/src/components/components.smoke.test.js`:
  - toggles render with correct default states;
  - hiding directories removes dir rows (visible list shrinks);
  - `Select all` with one type hidden selects only the visible type;
  - dir rows show the badge; renaming a dir (mocked) completes the dialog flow.

### M5 — Documentation
**Commit: `docs: document directory renaming and list view toggles`**

- `AGENTS.md`
  - §1 What this program is: files **and directories**; view toggles.
  - §2 Pipeline: dir extension rule (whole name is base, ext empty).
  - §3 Features: toggles, select-all/clear over visible entries, "N Item(s)"
    copy, mixed-list numbering.
  - §4 Behavior decisions (new entries): *Dirs are extension-less — the whole
    name is the base*; *numbering spans files and dirs in list order*;
    *duplicate check is cross-type via os.path.exists*; *default view shows
    files only*; *tree refresh after rename*.
  - §5 Layout: `/list` typed-entry contract, `dirs` request field, store state
    (`showFiles`/`showDirs`/`treeVersion`), FileList toggles + badge, updated
    test-file descriptions and test counts.
  - §7 Milestones: add row 10 (directory renaming) ✅.
- `README.md` — feature list note (dirs selectable, view toggles).

## Verification

After each commit (at minimum M1/M2/M4):

```sh
./do test                       # pytest (engine + api) + frontend vitest
cd frontend && npm run build    # production build, after M4
```

Manual smoke (macOS, `python run.py`): enable "Directories" in a folder →
select a dir → Add prefix + Case UPPER → preview shows extension-less new name
→ duplicate warning when target exists (file or dir) → rename succeeds, tree
label refreshes, contents intact.

## Release notes

- All commits are `feat`/`docs` ⇒ `do bump` on the `release/*` PR decides a
  **minor** version bump. Suggested release title: *"Directory renaming"*.
- Breaking-ish note for the API (not for the app, which ships both sides):
  `/api/list` entries gain `type`, and the POST requests accept `dirs`.
  Unknown/absent fields stay safe (`Config.from_dict` semantics unchanged).

## Explicitly out of scope (follow-ups)

- Nested/recursive directory selection (list always shows immediate children).
- Drag-drop reordering of list rows (numbering follows current order only).
- Persisting the show/hide preference across sessions (per session, like
  pipeline order — could join milestone 8 polish).
- Per-file vs per-dir numbering sequences (single combined sequence by list
  order is the documented behavior).
---

## Execution log (completed)

| # | Commit | Notes vs plan |
|---|--------|---------------|
| M1 | `020a12f` `feat(engine): support renaming directories as extension-less entries` | As planned. 20 new engine tests (suite: 116). |
| M2 | `c237921` `feat(api): list directories with type, accept dirs in preview/check/rename` | As planned. 7 new API tests (suite: 17). |
| M3 | `7400b3a` `feat(frontend): view toggles for files and directories in the store` | Deviations: actions are `setShowFiles(on)` / `setShowDirs(on)` (setter, not toggle) — a toggle is just `setShowFiles(!state.showFiles)`; pruning is a shared `pruneHidden()`; badge key is `fileList.typeDir` (not `dirBadge`); no separate `emptyDirs` key (empty state generalized to "entries"); no `fileList.showFiles/showDirs` label keys — the toggle labels live in `fileList.toggleFiles/toggleDirs`. 8 new store tests (suite: 43). |
| M4 | `83ebeed` `feat(frontend): directory rows with type badge, view toggles, tree refresh` | As planned; tree refresh re-fetches children of every loaded node on `treeVersion` bump; `bumpTreeVersion()` called from RenameButton after a successful rename. 3 new smoke tests (suite: 46). |
| M5 | this commit | AGENTS.md + README updated; plan finalized. |

Verification: `./do test` green at every commit (133 backend + 46 frontend tests total).
