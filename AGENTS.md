# AGENTS.md — A-Renamer Tool (Python + Svelte rebuild)

Authoritative reference for working on **this** repository: a modern, web-based
rebuild of the original Qt/C++ "A-Renamer Tool". It documents (1) what the program
does, (2) every feature/ability it must expose, and (3) how this codebase is
structured and built. Use it as the source of truth when adding features.

> The original Qt implementation lives in the sibling repo `../ARenamerTool` and is
> the behavioral reference. When in doubt about *intended* behavior, check there —
> but this rebuild intentionally fixes a few of its quirks (noted inline below).

---

## 1. What this program is

A desktop GUI for **bulk-renaming files and directories**. The user:

1. Selects a directory (folder browser or built-in directory tree).
2. Selects one or more entries in it — files and/or directories (multi-select,
   with Files/Directories show-hide toggles; default view shows files only).
3. Configures zero or more **modifiers** (text operations) that transform each name.
4. Sees a **live preview** of every selected entry's new name as they tweak modifiers.
5. Clicks **Rename** to apply all transformations on disk (with duplicate + confirmation safeguards).

Core value: batch rename with a composable set of text operations, instant per-entry
preview, and safe renaming — for files *and* folders. The UI is internationalized
(German + English) with a runtime language switcher.

### Delivery model (this rebuild)
- **Backend:** Python — FastAPI serves a small JSON API; the rename engine is pure,
  framework-agnostic Python (unit-tested). `pywebview` wraps it in a native desktop window.
- **Frontend:** Svelte (SPA) built by Vite, served by the backend. Talks to the API over `/api/*`.
- One command (`python run.py`) starts the server and opens the desktop window.

---

## 2. The rename pipeline (critical contract)

When a preview or rename is computed, the engine (`backend/engine/pipeline.py`) does:

1. **Reset** every file's `new_base` to its original base name.
2. **Sort** files by list row (deterministic, in-list-order numbering).
3. Apply each **active** modifier in pipeline order:

   `Replace → Case → If-Then → Remove → Add → Counting → Date`

The canonical order above is the **default** (`CANONICAL_ORDER` in
`backend/engine/pipeline.py`) and is locked in by `tests/test_engine.py`. It is
**user-adjustable**: `Config.pipeline_order` (an optional list of modifier ids,
`None` = canonical) lets the UI drag-and-drop the modifier cards into a custom
sequence. `resolve_order()` is defensive: unknown ids are dropped, missing ids
are appended in canonical order, so a partial/odd list never skips a modifier.
The order still applies to **all files uniformly** (there is no per-file order).

Only the **base name** is ever modified. The extension (everything from the last `.`
onward, dot included) is preserved and re-appended on rename. Files with no dot have
an empty extension; a leading-dot name like `.bashrc` yields an empty base.

**Directories are extension-less**: a `RenameFile` flagged `is_dir=True` keeps
`ext = ""` no matter what (a directory named `backup.tar` renames to
`x_backup.tar` — the dot is part of the name, not an extension). All seven modifiers
operate on the base name and therefore work unchanged for directories; the counting
modifier's number simply appends to the full name (`Photos` + suffix `02` → `Photos02`).
Numbering spans a mixed selection in on-screen list order (one combined sequence).

---

## 3. Features / abilities (the full checklist)

Every item below must work in the rebuilt UI. The engine side of most of these is
already implemented and tested (Milestone 2); the UI wiring lands in later milestones.

### Navigation & selection
- Browse/select a directory (native folder dialog and/or a directory tree).
- Directory tree navigation that re-roots the file list (and clears selection).
- Entry list (files and/or directories) with **multi-selection**; directory rows
  carry a small type badge.
- **Files / Directories show-hide toggles** (default: files shown, directories
  hidden — the historical view). Hidden entries are never rendered, never
  selectable, and are pruned from the selection, previews and duplicate
  highlights the moment their type is toggled off.
- "Select all" (selects the *visible* entries) and "Clear selection" actions.
- After a successful rename, the directory tree refreshes the labels of renamed
  directories (store `treeVersion` bump).
- Current-path display.

### Live preview
- Per-entry "new name" preview column, updated instantly on any control change.
- Preview reflects the full modifier pipeline in the correct order (§2).

### Modifiers (all seven, each independently toggleable; disabled controls greyed out)
- **Add / Insert** — prefix, suffix, and insert-at-position. (Insert applies first, then the name is wrapped `prefix + name + suffix`.)
- **If-Then** — condition (CONTAINS / CONTAINS-NOT, plain or regex, case option) evaluated against the file's *original* base name → consequence (add as PREFIX / INSERT-at-pos / SUFFIX).
- **Replace** — search (plain or regex, case option) → replacement; replaces all occurrences.
- **Case** — letter case of the base name: UPPERCASE / lowercase / Title Case / Sentence case, plus word cases (camelCase, PascalCase, snake_case, kebab-case, CONSTANT_CASE, train case) that split the name on delimiters and camelCase boundaries (digits never split; acronyms split naively, one letter per word).
- **Remove** — first-n chars, last-n chars, and a character range (start–end) with an "until end" option. Ranges that run past a shorter name clamp to the actual end (no out-of-bounds).
- **Counting / Number** — start number, zero-padding (e.g. `001`), placed as prefix / suffix / insert-at-pos. Numbers follow on-screen list order, not alphabetical.
- **Date** — format (DD-MM-YYYY / YYYY-MM-DD / MM-DD-YYYY), date separator, optional name separator (between the date and the rest of the name; empty = direct concatenation), source (created / last-modified / today / custom + date picker), placed as prefix / suffix / insert-at-pos.

### Safety & workflow (the Rename button)
Duplicate detection is **cross-type**: it compares against whatever exists on disk at
the target path, so dir→existing-file, dir→existing-dir and file→existing-dir are all
catched. (Copy was generalized: the original's "File(s)" dialogs now say "Item(s)" / de "Element(e)".)
1. **Duplicate check** — re-run the pipeline; if any resulting name already exists on disk (skipping unchanged entries), show a blocking **Warning** ("Found existing entries for N new name(s)!") with only an Abort button, and stop.
2. **Confirmation** — "Rename N Item(s)?" with Ok / Abort (N = selected count).
3. On Ok → perform the renames; only rename entries whose new name differs from the current one.
4. **Success** — "Successfully renamed N Item(s)!"

### UI/UX
- At-a-glance active-modifier indicator per modifier group (✓ / ✗).
- Disabled controls greyed out when their parent modifier is off.
- Internationalized UI (German + English) with a runtime language switcher and system-locale auto-detection.

---

## 4. Behavior decisions vs the original (quirks)

The original had a few quirks. This rebuild makes explicit choices:

- **Replace double-application — FIXED.** The original ran an extra unconditional
  plain/case-insensitive `replace()` after the regex branch, double-applying. This port
  applies the replacement exactly once per the selected mode (`backend/engine/replace.py`).
- **If-Then condition uses the original base name — PRESERVED.** The condition is tested
  against the immutable `base`, while the consequence applies to the evolving `new_base`.
- **Numbering follows list order — PRESERVED.**
- **Case modifier — ADDED (not in the original).** Placed right after Replace in the
  pipeline: case is a text transformation like Replace, so text *inserted* later
  (Add, numbers, dates, If-Then consequences) keeps its own casing. Title Case uses
  `str.title`, whose apostrophe quirk is documented and preserved (`it's` → `It'S`).
- **Preview shows the full name** (`base + extension`) in the preview column — FIXED (the
  original showed the base name only). More useful and unambiguous; a display choice only.
- **No separator between a name and an appended number — PRESERVED (faithful).** The
  original appends/prepends the value directly, so `name` + number-suffix `01` yields
  `name01`. If a nicer result is wanted, the user combines with **Add** (e.g. an `-` suffix).
- **Optional name separator for Date — ADDED.** The original concatenated the date directly
  (`name2024-05-01`); this rebuild adds an *optional* `name_separator` (default empty = the
  faithful direct concatenation). When set, it goes between the date and the name text on each
  side that exists (`photo-2024-05-01`, `2024-05-01-photo`), never leaving a dangling
  separator at an edge or against an empty base.
- **Adjustable pipeline order — ADDED (not in the original).** The canonical order
  (§2) stays the default and the test baseline; the UI additionally lets the user
  drag the modifier cards into a custom sequence (`Config.pipeline_order`). The
  order is per-session (no persistence — a fresh start always uses canonical).
- **Invalid regex is a no-op** (does not crash the live preview) — a deliberate safety choice.
- **Empty Replace search is a no-op** (a deliberate safety choice). `str.replace("", x)` would
  otherwise insert the replacement between every character and mangle names on disk.
- **Directory renaming — ADDED (not in the original).** The original listed files only.
  This rebuild lists *entries*: `/api/list` returns files **and** subdirectories, each
  with a `type: "file"|"dir"` field (dirs report `size: 0`, real `mtime`), and the
  preview/check/rename endpoints accept an optional `dirs[]` (the selected names that
  are directories) so the engine can flag them extension-less (`RenameFile.is_dir`).
  Omitting `dirs` ⇒ everything is a file, so old clients keep working. The **default
  view still shows files only** (toggles in §3), so the historical behavior is
  preserved out of the box.
- **View toggles are view state, not modifier config — ADDED.** `showFiles`/`showDirs`
  live in the frontend store (with `treeVersion`), deliberately **not** in
  `defaultConfig()`/`sanitizeConfig()`/the backend recipe: they are presentation,
  not part of the rename pipeline, and are per-session (no persistence).

---

## 5. Repository layout

```
arenamer/
├── run.py                     # one-command launcher (desktop window, or web fallback)
├── do                         # release tooling: bump/tag/changelog/build/test (pure stdlib)
├── requirements.txt           # runtime deps: fastapi, uvicorn, pywebview
├── requirements-dev.txt       # + pytest
├── backend/
│   ├── main.py                # FastAPI app: static mount, /api/health, pywebview bootstrap
│   ├── api/                   # API routes + Pydantic schemas (list/dirs/preview/check/rename)
│   ├── engine/                # PURE rename engine (no web deps) — the correctness core
│   │   ├── models.py          # RenameFile + Config dataclasses (+ JSON (de)serialization)
│   │   ├── pipeline.py        # compute/preview/find_duplicates/check_duplicates/perform_rename/build_files
│   │   ├── add.py remove.py replace.py case.py number.py ifthen.py date.py
│   └── static/                # built SPA (gitignored; `npm run build` output)
├── frontend/                  # Svelte SPA (Vite)
│   ├── package.json  vite.config.js  vitest.config.js  index.html
│   └── src/
│       ├── main.js            # mounts the Svelte app
│       ├── App.svelte         # root: path bar + tree | file list layout + modifier panels + live-preview effect
│       ├── lib/api.js         # fetch client for /api/*
│       ├── lib/config.js      # defaultConfig() + sanitizeConfig() (plain JS, no runes)
│       ├── lib/i18n/          # en.js + de.js (string tables) and index.svelte.js (language $state, t())
│       ├── lib/state/         # store.svelte.js — central $state (files, selection, view toggles, config, previews, dialog)
│       ├── components/        # FileList, DirectoryTree (+TreeNode), RenameButton, Dialog (done)
│       └── components/modifiers/  # all seven panels: Replace, Case, IfThen, Remove, Add, Counting, Date
├── .github/workflows/         # GitHub Actions: ci.yml (dev), release.yml (bump+tag), build.yml (3-OS releases)
└── tests/
    └── backend/
        ├── test_engine.py     # engine suite (116 tests) — modifiers, pipeline order (incl. custom), directories, edge cases
        └── test_api.py        # API suite (17 tests) — list/dirs/preview/check/rename over HTTP (incl. typed entries + dirs)
```

### Engine public API (`backend/engine/__init__.py`)
- `Config` / `RenameFile` and the seven modifier config dataclasses — from `models.py`.
  `RenameFile` has `is_dir: bool = False`: directories are extension-less entries.
- `compute(files, config)` — run the full pipeline (mutates each file's `new_base`).
- `build_files(path, names, dirs=None)` — build `RenameFile` objects (row = list position);
  the `dirs` names are flagged `is_dir=True`.
- `preview(files, config)` — per-entry new-name info keyed by original name (incl. `type`).
- `find_duplicates(files, config)` / `check_duplicates(...)` — names/count that would clobber an existing entry (cross-type).
- `perform_rename(files, config)` — rename on disk; returns `{renamed, errors}`.

The engine is **pure stdlib** (dataclasses, `re`, `os`, `datetime`) — no web deps — so it
is trivially unit-testable and reusable.

### API surface (`backend/api/routes.py`, all under `/api`)
- `GET  /list?path=` — the directory's entries: files **and** subdirectories, each with
  `type: "file"|"dir"` (dirs report `size: 0`, real `mtime`), sorted. The response field
  is still named `files`; filtering by type is client-side (the view toggles, §3).
- `GET  /dirs?path=` — immediate subdirectories (for lazy tree navigation).
- `GET  /home`       — the user's home directory (default starting point for the UI).
- `POST /preview`  `{path, files[], dirs[], config}` → per-entry new-name preview (incl. `type`).
- `POST /check`    `{path, files[], dirs[], config}` → duplicate names that would clobber an existing entry.
- `POST /rename`   `{path, files[], dirs[], config}` → renames on disk; **409** if any would clobber.

`files` carries the selected names in on-screen list order; `dirs` (optional) lists which
of them are directories — omitted ⇒ everything is a file (backward compatible).
`config` is a plain JSON object matching `Config.to_dict()` (see §3); the backend converts
it via `Config.from_dict`, so partial configs from the UI are fine. Unknown keys are ignored
and `null` values fall back to each field's default, so a cleared UI input never 500s. The
rename workflow is: UI calls `/check` (blocking warning if duplicates) → its own confirm
dialog → `/rename`.

### Frontend architecture (`frontend/src`)
- **`lib/state/store.svelte.js`** — the single source of truth. A module-level Svelte 5
  `$state` object (files, selection, **showFiles/showDirs view toggles**, **treeVersion**,
  config, previews, duplicateNames, dialog) plus action
  functions (`loadDir`, `openHome`, `goUp`, `toggleSelect`, `selectAll`, `clearSelection`,
  `setShowFiles`, `setShowDirs`, `bumpTreeVersion`,
  `refreshPreview`, `showDialog`, `checkDuplicates`, `performRename`). `selectAll` selects
  the *visible* entries only; hiding a type prunes it from selection/previews/duplicates.
  Preview/check/rename payloads include the `dirs` field. It uses the
  `.svelte.js` extension because `$state` is a rune (only compiled in `.svelte*` files).
- **`lib/api.js`** — thin `fetch` client for the `/api/*` endpoints.
- **`lib/config.js`** — `defaultConfig()` (the all-disabled recipe; its shape MUST mirror
  backend `Config.to_dict()`) and `sanitizeConfig()` (coerces every numeric field to an int
  before each API call — Svelte binds a cleared `<input type="number">` to `null`, which
  would otherwise crash the engine and 500 the live preview).
- **`lib/i18n/`** — runtime internationalization (German + English). `en.js` is the source
  of truth; `de.js` has the identical key set (wording taken from the original Qt app's
  `languages/ARenamerTool_de_DE.ts`, modernized to standard German capitalization).
  `index.svelte.js` holds the language as a `$state` property, so every `t("key")` call in
  a template is reactive — switching re-renders all strings. Startup detection mirrors the
  original's `QLocale::system()`: a saved user choice (localStorage) wins, otherwise
  `navigator.language` (`de*` → German). All UI strings go through `t()`; backend error
  messages stay English (technical, not user-facing copy).
  - **`components/FileList.svelte`** — Files/Directories view-toggle checkboxes, a
    Select-all/Clear toolbar, and the Name + New Name preview table of *visible* entries
    (multi-select; row/checkbox click toggles; header checkbox selects all; dir rows
    carry a type badge), with red highlighting of rows that would clobber an existing
    entry. The table fills the center column and scrolls
    internally (sticky header); `table-layout: fixed` + ellipsis keeps long names from stretching
    the view. **`components/modifiers/`** — all seven panels (Replace, Case, If-Then, Remove, Add,
    Counting/Number, Date), each a self-contained section with an enable toggle + ✓/✗ indicator
    and controls greyed out when disabled; panels are rendered in `App.svelte` in pipeline order
    (§2), stacked vertically in the right-hand sidebar.
- **`components/DirectoryTree.svelte`** (+ recursive `TreeNode.svelte`) — lazy directory tree
  rooted at home (`/api/dirs` per expansion); clicking a node re-roots the file list. It
  watches `treeVersion` and re-fetches the children of every loaded node, so renamed
  directories get fresh labels.
- **`components/RenameButton.svelte`** — drives the rename workflow: `/api/check` (blocking
  duplicate warning) → confirm dialog → `/api/rename` → success dialog, then re-lists the
  dir and bumps `treeVersion` (tree label refresh).
- **`components/Dialog.svelte`** — reusable modal (warning / confirm / info variants; Esc or
  backdrop click dismisses). Rendered once in `App.svelte`; driven by the store's `dialog` state.
- **`App.svelte`** — composes the header (title + language switcher), the path bar
  (Home / Up / Open) and a full-viewport three-pane layout: directory tree | file list
  | modifier sidebar. The page itself never scrolls — each pane scrolls internally
  (native-app feel); below ~980px it falls back to a stacked, page-scrolling layout.
  A debounced `$effect` re-runs `/api/preview` whenever config, selection or directory
  changes (live preview).

> **Preview shows the full name** (`base + extension`), a deliberate *fix* of the original's
> base-only preview column (see §4): it is more useful and unambiguous. The engine still returns
> `new_base`/`ext` separately, so this is a display choice only.

---

## 6. Build, run & test

### Backend / engine
```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt      # fastapi, uvicorn, pywebview, pytest
python run.py                            # desktop window (or web fallback at :8000)
```

### Tests (the engine is the verified core)
```sh
python3 -m pytest tests/ -v             # from repo root (pytest suite lives in tests/backend/)
```

`./do test` runs the pytest suite above plus the frontend vitest suite
(`cd frontend && npm run test`) — one command covers both.

### Frontend (Svelte)
```sh
cd frontend && npm install
npm run dev                             # Vite dev server on :5173 (proxies /api -> :8000)
npm run build                           # emits to ../backend/static for the desktop app
npm run test                            # vitest unit tests (also runs in CI, see below)
```

### Frontend tests (vitest)

`npm run test` in `frontend/` runs the vitest suite (currently 46 tests across
four files): `lib/config.test.js` (defaultConfig/sanitizeConfig),
`lib/i18n/languages.test.js` (en/de key parity, locale detection, `t()`),
`lib/state/store.svelte.test.js` (selection, pipeline order, dialogs, api-backed
flows with `vi.mock` of `lib/api.js`), and `components/components.smoke.test.js`
(FileList / Dialog / RenameButton render + interaction smoke tests against the
real module-level store).

Toolchain notes (keep these when changing the test setup):
- `vitest.config.js` is deliberately separate from `vite.config.js` so the
  production build is untouched. It aliases bare `svelte` to its **client entry** —
  under Vitest's SSR-style transform it otherwise resolves to `index-server.js`
  and `mount()` throws `lifecycle_function_unavailable`.
- `components.smoke.test.js` opts into **jsdom** via `// @vitest-environment jsdom`
  (happy-dom crashes inside Svelte 5 checkbox mounting); everything else runs on
  happy-dom.
- Store/i18n are module-level `$state` singletons: unit tests get fresh state via
  `vi.resetModules()` + dynamic import (store) or explicit resets (component smoke tests).
- Frontend tests stay **co-located under `frontend/src/`** (vitest convention). A shared
  `tests/frontend/` folder was tried and abandoned: Vite refuses to load test files outside
  its project root even with `root` lifted to the repo root. The Python suite lives in
  `tests/backend/`.

For a full desktop run: start the backend (`python run.py` or `uvicorn backend.main:app`)
and either open http://127.0.0.1:8000 (after `npm run build`) or use the Vite dev server.

### Packaging (distributable desktop app)

The app is a pywebview window around the Svelte SPA + in-process FastAPI server. To ship it
without requiring Python, `build/build.py` bundles everything with PyInstaller:

```sh
pip install -r requirements-build.txt   # pyinstaller (add to your venv)
python build/build.py                   # frontend -> PyInstaller -> versioned archive in dist/
```

`build/build.py` is a single cross-platform orchestrator (no shell differences). It builds the
frontend, runs `build/arenamer.spec`, then packages the result. Because **PyInstaller cannot
cross-compile, run it on each target OS** to get that OS's artifact:

| OS | Artifact in `dist/` | pywebview driver | End-user system requirement |
|----|---------------------|------------------|------------------------------|
| macOS | `A-Renamer.app` + `-macOS.zip` | `cocoa` (WKWebView) | none (system WebKit); unsigned → right-click→Open past Gatekeeper |
| Windows | `A-Renamer/` + `-win64.zip` | `edgechromium` (WebView2) | Edge WebView2 Runtime (preinstalled on Win10/11) |
| Linux | `A-Renamer/` + `-linux.tar.gz` | `gtk` (WebKit2GTK) | `libwebkit2gtk-4.x` system libs |

Packaging internals:
- **`build/arenamer.spec`** — the PyInstaller spec (one-folder bundle; a `.app` on macOS).
  Reads name/version from `pyproject.toml`. Set its top-level `CONSOLE = False` for release
  builds (no console window on Windows).
- **`build/_bundle.py`** — shared dependency collection: pywebview's JS bridge, uvicorn's
  dynamic loop modules, and (macOS only) the PyObjC frameworks behind WKWebView.
- **`build/_smoke.py`** + `build/smoke.spec` — a headless frozen-bundle test (imports the full
  stack, serves `/api/health` + `/`, exits). Useful to validate a build on an OS where you can't
  easily see the window: `python -m PyInstaller build/smoke.spec && dist/arenamer-smoke`.

The frozen app resolves its bundled SPA via `backend/main.py:_base_dir()` (uses `sys._MEIPASS`
when frozen), and picks a free localhost port in `run.py` so instances don't clash.

### CI & releases (GitHub Actions)

Three workflows in `.github/workflows/` cover development and release; they reuse
`do` (stdlib-only, so it runs in CI without installs) and `build/build.py` — keep both
self-contained if you change them. No branch protection is configured (solo development).

- **`ci.yml` — development pipeline.** Triggers: every PR + pushes to `develop`.
  Four parallel jobs: `backend-tests` (pytest, matrix over Python 3.10 + 3.12),
  `frontend-tests` (vitest, Node 22), `frontend-build` (production vite build), and
  `version-sync` (asserts `pyproject.toml` == `frontend/package.json`). pip/npm caching
  and cancel-in-progress concurrency are set.
- **`release.yml` — version bump + tag on master.** Trigger: a merged PR whose head
  branch starts with `release/` and whose base is `master`. It checks out the merge
  commit with `fetch-depth: 0` (`do bump` needs `git describe --tags` and
  `git log tag..HEAD`), then: (1) `do bump` → semver decision from the conventional
  commits since the last tag, version + changelog commit; (2) if HEAD moved, `do tag`
  → `v<version>` on that commit, and the commit + tag are pushed. Idempotent: nothing
  new since the last tag → no commit, no tag, job ends. Note: `do` imports `tomllib`,
  so the job sets up Python 3.12 first (runner system Python is older).
- **`build.yml` — desktop builds + GitHub Release.** Trigger: tag push `v<digit>*`
  (fired by `release.yml`). Three parallel OS jobs — `macos-latest`, `windows-latest`,
  `ubuntu-latest` (PyInstaller cannot cross-compile): install runtime + PyInstaller
  deps, `python do build` (frontend → bundle → versioned archive), then run the
  headless smoke test (`build/smoke.spec` → `dist/arenamer-smoke[.exe]`) as proof the
  frozen bundle imports and serves — the only CI signal that the app actually starts.
  Linux additionally apt-installs the WebKit2GTK runtime + typelibs for the `gtk` driver.
  A final `release` job attaches the three artifacts to the GitHub Release, using the
  matching `changelog.md` section as the release notes.

Release flow: branch `release/vX.Y.Z` off `develop` (conventional commits) → PR to
`master` → `release.yml` bumps + tags → `build.yml` publishes all three OS artifacts.
Artifacts are unsigned (Gatekeeper/SmartScreen notes from the Packaging section apply).

---

## 7. Milestone plan & status

| # | Scope | Status |
|---|-------|--------|
| 1 | Scaffold: FastAPI + pywebview backend, Vite+Svelte frontend, static mount, one-command run | ✅ done (scaffold) |
| 2 | Engine: port all 6 modifiers + pipeline order, pure Python, pytest suite green (59 tests) | ✅ done |
| 3 | API: `/api/list`, `/api/dirs`, `/api/preview`, `/api/check`, `/api/rename` (duplicate check + 409 safety net) | ✅ done |
| 4 | Frontend core: central store (files, selection, config), live preview column | ✅ done |
| 5 | UI: file list (multi-select), directory tree, select-all/clear, path bar, Rename button + dialogs | ✅ done |
| 6 | Modifier panels: all six with live preview + active indicators (✓/✗) | ✅ done |
| 7 | i18n: German + English, runtime switcher, system-locale auto-detect | ✅ done |
| 8 | Polish: dark mode, keyboard shortcuts, drag-and-drop, empty states, error handling | ⬜ next |
| 9 | CI: GitHub Actions (dev pipeline, automated bump + tag on master, 3-OS release builds) | ✅ done |
| 10 | Folder editing: directories are renamable extension-less entries (engine + typed `/api/list` + `dirs` payload), Files/Directories view toggles, type badges, tree label refresh | ✅ done |

### Conventions for future work
- CI reuses `do` and `build/build.py`: keep `do` stdlib-only and the build orchestrator
  self-contained so the workflows keep working; job display names in `ci.yml` /
  `release.yml` should stay stable.
- Keep the engine **pure** (no web/fs-side-effect deps beyond what a rename needs); put
  HTTP concerns in `backend/api/`. Add engine behavior changes **with tests**.
- The frontend is a single source of truth in `src/lib/state/`; components read/write the
  store and call `/api/*`. Never let a component compute rename results locally.
- Preserve the pipeline order (§2) and the behavior decisions in §4 unless explicitly told otherwise.
- **Never import `state` into a component and write `$state` in it.** Svelte 5 parses
  `$state` as the *legacy store* auto-subscription (`state.subscribe`) when a `state`
  binding is in scope, not as the `$state` rune — this crashed every `TreeNode` render
  (tree pane never appeared). Alias the import (`state as appState`) or use a plain
  `let` for DOM bindings.
