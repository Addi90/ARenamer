# AGENTS.md — A-Renamer Tool (Python + Svelte rebuild)

Authoritative reference for this repo: a web-based rebuild of the original Qt/C++
"A-Renamer Tool" (sibling repo `../ARenamerTool` — the *behavioral* reference; when
intended behavior is unclear, check there, but the intentional fixes below win).

Desktop GUI for **bulk-renaming files *and* directories**: pick a directory, multi-select
entries (Files/Directories show-hide toggles; default: files only), configure a pipeline of
text modifiers, get a live per-entry preview, then rename with duplicate + confirmation
safeguards. UI is internationalized (German + English, runtime switcher).

**Stack:** FastAPI JSON API + pure-Python rename engine (unit-tested), Svelte 5 SPA (Vite)
served by the backend, `pywebview` desktop window. One command: `python run.py`
(desktop window, or `:8000` web fallback).

---

## 1. Rename pipeline (the core contract)

`backend/engine/pipeline.py: compute(files, config)`:

1. Reset each file's `new_base` to its original base name.
2. Sort by list row (numbering follows **on-screen list order**, not alphabetical).
3. Apply **active** modifiers in canonical order `Replace → Case → If-Then → Remove → Add
   → Counting → Date` (`CANONICAL_ORDER`, locked by tests). User-adjustable via
   `Config.pipeline_order` (drag-and-drop cards; `None` = canonical; per-session, not
   persisted). `resolve_order()` is defensive: unknown ids dropped, missing appended
   canonically — a partial list never skips a modifier.

Rules:
- Only the **base name** is modified; the extension (from the last `.`) is preserved.
  A *leading* dot is not an extension (`.bashrc` → whole name is the base;
  `.hidden.tar` → base `.hidden`) — the `os.path.splitext` convention.
- **Directories** (`RenameFile.is_dir=True`) are always extension-less (`backup.tar` dir →
  `x_backup.tar`); all seven modifiers work unchanged on them. Numbering spans a mixed
  selection in list order (one combined sequence).
- Invalid regex = no-op (never crashes the live preview). Empty Replace search = no-op
  (`str.replace("", x)` would mangle names on disk).
- The engine is **pure stdlib** (dataclasses, `re`, `os`, `datetime`) — no web deps;
  HTTP concerns live in `backend/api/`.

## 2. The seven modifiers

Each is independently toggleable (✓/✗ indicator); when off its panel **collapses** (hidden) and
its `<fieldset disabled>` root keeps every control in a real disabled state (for assistive
tech) — and its card is drag-reorderable.

| Modifier | What it does | Notes |
|---|---|---|
| **Replace** | search → replace, all occurrences; plain or regex, case option | fixed: applied exactly once (original double-applied) |
| **Case** | UPPER / lower / Title / Sentence + camel, Pascal, snake, kebab, CONSTANT, train | added (not in original); splits on delimiters + camel boundaries; `str.title` apostrophe quirk (`it's` → `It'S`) preserved |
| **If-Then** | condition (CONTAINS / CONTAINS-NOT, plain or regex, case) evaluated on the **original** `base` → consequence as PREFIX / INSERT-at-pos / SUFFIX | consequence applies to the evolving `new_base` (preserved quirk) |
| **Remove** | first-n chars, last-n chars, range start–end (+ "until end") | ranges clamping past a shorter name never go out of bounds |
| **Add** | prefix, suffix, insert-at-position | insert applies first, then `prefix + name + suffix` |
| **Counting** | start number, zero-padding (`001`), as prefix / suffix / insert | no separator (faithful: `name01`); combine with **Add** for a dash |
| **Date** | format DD-MM-YYYY / YYYY-MM-DD / MM-DD-YYYY, date separator, optional **name separator** (default empty = direct concat, faithful), source created/mtime/today/custom (+picker), prefix/suffix/insert | never leaves a dangling separator at an edge or against an empty base |

Sub-option inputs follow one rule: mode-only inputs render conditionally (`{#if}`),
persistent-value inputs (Remove's range) stay visible and use real `disabled` attributes.

## 3. Rename workflow (safety)

`/check` → if any resulting name would clobber an existing on-disk entry, a blocking
**Warning** "Found existing entries for N new name(s)!" (Abort only) and stop. Duplicate
detection is **cross-type** (compares against whatever exists at the target path:
file→dir, dir→file, dir→dir). Else **Confirmation** "Rename N Item(s)?" (Ok/Abort;
dialogs say "Item(s)" / de "Element(e)", not "File(s)") → on Ok rename only entries
whose new name differs → **"Successfully renamed N Item(s)!"**

## 4. Behavior decisions vs the original (keep unless explicitly told otherwise)

- **Fixed:** Replace double-application; preview shows the full name (base + extension);
  dot-files are fully renameable; dialogs say "Item(s)"; disabled modifier panels are a real
  `<fieldset disabled>` and, in the modern UI, collapsed (was a CSS-only grey-out — keyboard
  users could still Tab in and edit).
- **Preserved:** If-Then condition on the original base; list-order numbering; no
  separator around numbers; `str.title` apostrophe quirk.
- **Added (beyond the original):** Case modifier; directory renaming (typed `/api/list` +
  optional `dirs[]` payload); Files/Directories **view toggles** (view state, *not* modifier
  config — deliberately not in `defaultConfig()`/`Config`); date name separator; custom
  pipeline order.

## 5. Repo layout

```
run.py                 # one-command launcher (desktop window / :8000 web)
do                     # release tooling, pure stdlib: bump / tag / changelog / build / test
pyproject.toml         # single source of version truth (PyInstaller spec + CI version-sync);
                       #   also pip-installable (pip install -e . -> `arenamer`)
DESIGN.md              # design system: tokens, two themes (dark default), elevation, state contract
plan.md                # historical planning doc (directory renaming; shipped in 0.3.0 — don't re-execute)
requirements*.txt      # runtime (fastapi, uvicorn, pywebview) / -dev (+pytest) / -build (+pyinstaller, cairosvg, pillow)
changelog.md           # per-tag sections written by `do bump`
backend/
├── main.py            # FastAPI app, static mount, /api/health, pywebview bootstrap; _base_dir() honors sys._MEIPASS when frozen
├── api/               # routes.py (all /api/*) + schemas.py
└── engine/            # PURE engine: models.py (Config, RenameFile + 7 modifier configs, to/from_dict),
                       #   pipeline.py, add remove replace case number ifthen date
frontend/src/
├── index.css          # design tokens (two themes, dark default) + global state contract, per DESIGN.md
├── App.svelte         # 3-pane layout (tree | file list | modifier sidebar), header (language + theme
│                      #   toggle), breadcrumb path bar (+ path input / Open), dismissible error banner,
│                      #   dialog host, debounced preview $effect; page never scrolls (each pane does),
│                      #   stacked below ~980px
├── lib/state/store.svelte.js   # THE single $state store + all actions (see §6)
├── lib/api.js         # fetch client for /api/*
├── lib/config.js      # defaultConfig() + sanitizeConfig()
├── lib/i18n/          # en.js (source of truth), de.js (identical key set), index.svelte.js (language $state, t())
└── components/        # FileList, DirectoryTree(+TreeNode), ModifierCard, RenameButton, Dialog
    └── modifiers/     # seven panels: Replace, Case, IfThen, Remove, Add, Counting, Date
build/                 # build.py (cross-platform orchestrator: frontend → icons → PyInstaller → archive),
                       #   arenamer.spec, _bundle.py, _smoke.py + smoke.spec, icons/, make_icons.py
tests/backend/         # test_engine.py (127 tests), test_api.py (18 tests)
.github/workflows/     # ci.yml, release.yml, build.yml
```

Engine public API (`backend/engine/__init__.py`): `Config`, `RenameFile` (incl. `is_dir`),
the seven `*Config` dataclasses, `CANONICAL_ORDER`, `compute`, `build_files(path, names,
dirs=None)`, `preview`, `find_duplicates` / `check_duplicates`, `perform_rename`.

### API surface (`/api/*`, `backend/api/routes.py`)

- `GET /list?path=` — the directory's entries: files **and** subdirectories, each
  `type: "file"|"dir"` (dirs report `size: 0`, real mtime), sorted. Response field is
  still named `files`; type filtering is client-side (view toggles). Friendly **403** for
  unreadable dirs (e.g. macOS TCC).
- `GET /dirs?path=` — immediate subdirectories (lazy tree); `GET /home` — home directory.
- `POST /preview | /check | /rename` — `{path, files[], dirs[], config}`. `files` = selected
  names **in on-screen list order**; `dirs` = the ones that are directories (optional —
  omitted ⇒ all files, old clients keep working). `/rename` returns **409** if any would clobber.

`config` is a plain JSON object matching `Config.to_dict()`; `Config.from_dict` accepts
partial configs (unknown keys ignored, `null` → field default, so a cleared UI input never 500s).
Workflow: UI calls `/check` (blocking warning) → its own confirm dialog → `/rename`.

## 6. Frontend essentials

- **The store is the single source of truth** — a module-level `$state` object (files,
  selection, `showFiles`/`showDirs`, `treeVersion`, config, previews, `duplicateNames`,
  `error`, `dialog`) plus actions: `loadDir, openHome, goUp, clearError, toggleSelect,
  selectAll, clearSelection, setShowFiles, setShowDirs, reorderModifier, resetModifierOrder,
  refreshPreview, showDialog, checkDuplicates, performRename, bumpTreeVersion`.
  `selectAll` selects the *visible* entries only; hiding a type prunes it from selection,
  previews and duplicate highlights the moment it's toggled off. Components read/write the
  store and call `/api/*` — **never compute rename results in a component**.
- **`$state` rune trap:** Svelte 5 parses `$state` as a *legacy store* auto-subscription
  (`state.subscribe`) when a binding named `state` is in scope — this crashed every
  TreeNode render. Alias the import (`state as appState`) in components; only plain dot
  access (`state.x`) is safe.
- Files using `$state` must use the **`.svelte.js`** extension (runes only compile in
  `.svelte*` files).
- **Live preview:** debounced `$effect` in `App.svelte` re-runs `/api/preview` on any
  config / selection / directory change.
- **Theming:** dark is the default; the header toggle flips `data-theme` on `<html>` and
  persists `"arenamer.theme"` to localStorage — `frontend/index.html` re-applies that key
  in an inline pre-paint script so there is no flash. All colours come from the CSS
  variables in `index.css` (the `DESIGN.md` token set); components use `var(--token)`
  only — no off-system hex, no ad-hoc shadows.
- `sanitizeConfig()` coerces every numeric field to int before each API call (Svelte binds
  a cleared `<input type="number">` to `null`). Keep it in sync with `defaultConfig()`
  and the backend `Config` — the three shapes must mirror each other.
- **i18n:** all UI strings go through `t("key")` (reactive). `en.js` is the source of
  truth; `de.js` has the identical key set (tested); wording is modernized standard German.
  Startup: saved choice (localStorage) wins, else `navigator.language` (`de*` → German).
  Backend error messages stay English (technical, not user-facing copy).
- **DirectoryTree:** lazy under home (`/api/dirs` per expansion); clicking a node re-roots
  the file list; watches `treeVersion` to re-fetch children of loaded nodes (renamed-dir
  labels). **Lesson (fixed bug):** the refresh must run outside the `$effect` body —
  running `refreshLoaded()` inside tracked node state and caused an endless re-fetch loop
  (tree collapsed to its first level).

## 7. Build, run & test

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt          # fastapi, uvicorn, pywebview, pytest
python run.py                                # desktop window (or web fallback :8000)

python -m pytest tests/ -v                   # backend suite, from repo root

cd frontend && npm install
npm run dev                                  # Vite :5173 (proxies /api → :8000)
npm run build                                # → ../backend/static
npm run test                                 # vitest: 7 files, 98 tests
                                             #   (lib/config, lib/api, lib/i18n/languages, lib/state/store,
                                             #    components/DirectoryTree, components smoke, modifiers smoke)
./do test                                    # pytest + vitest in one command
```

Vitest notes (keep when changing test setup): `vitest.config.js` is separate from
`vite.config.js` (production build untouched) and aliases bare `svelte` to its **client
entry** — otherwise the SSR-style transform resolves `index-server.js` and `mount()`
throws `lifecycle_function_unavailable`. The component smoke test opts into **jsdom**
(`// @vitest-environment jsdom`; happy-dom crashes inside Svelte 5 checkbox mounting).
Store/i18n are module-level singletons: tests get fresh state via `vi.resetModules()` +
dynamic import (store) or explicit resets (smoke). Frontend tests stay **co-located under
`frontend/src/`** — Vite refuses test files outside its project root (a shared
`tests/frontend/` folder was tried and abandoned); the Python suite lives in
`tests/backend/`.

### Packaging (distributable desktop app)

`python build/build.py` (or `./do build`): frontend → (re)generate native icons from
`favicon.svg` (best effort via `make_icons.py`; committed icons are the fallback) →
PyInstaller (`build/arenamer.spec`, one-folder bundle, `.app` on macOS; `CONSOLE=False`
always — it's a GUI app, and on macOS console=True would hide the Dock icon) →
versioned archive in `dist/`. `_bundle.py` collects
pywebview's JS bridge, uvicorn's dynamic loop modules, and (macOS) the PyObjC frameworks
behind WKWebView. Because **PyInstaller cannot cross-compile, run it on each target OS**:

| OS | Artifact | pywebview driver | System requirement |
|----|----------|------------------|--------------------|
| macOS | `A-Renamer.app` + `-macOS.zip` | `cocoa` (WKWebView) | none; unsigned → right-click→Open past Gatekeeper |
| Windows | `A-Renamer/` + `-windows.zip` | `edgechromium` (WebView2) | WebView2 Runtime (preinstalled Win10/11) |
| Linux | `A-Renamer/` + `-linux.tar.gz` | `gtk` (WebKit2GTK) | `libwebkit2gtk-4.x` |

Headless frozen-bundle smoke test: `python -m PyInstaller build/smoke.spec &&
dist/arenamer-smoke[.exe]` (imports the full stack, serves `/api/health` + `/`). The frozen
app resolves its bundled SPA via `backend/main.py:_base_dir()`; `run.py` picks a free
localhost port so instances don't clash.

## 8. CI & releases (GitHub Actions)

- **`ci.yml`** (PRs + pushes to `develop`): 4 parallel jobs — backend-tests (pytest,
  Python 3.10/3.12), frontend-tests (vitest, Node 22), frontend-build, version-sync
  (asserts `pyproject.toml` == `frontend/package.json`).
- **`release.yml`** (trigger: `pull_request` **closed** with `merged == true`, base
  `master`, head `release/*` — so it only fires on actual merges; checks out `master`
  with `fetch-depth: 0` because `do bump` needs `git describe`; optional
  `RELEASE_PAT` token): `do bump` (semver from conventional commits since last tag;
  commit version + changelog) → if HEAD moved, `do tag` (`v<version>`), then push
  `master --tags`. Idempotent: nothing new → no commit/tag. Job sets up Python 3.12
  first (`do` imports `tomllib`).
- **`build.yml`** (tag push `v<digit>*`): three parallel OS jobs install runtime +
  PyInstaller deps, `python do build`, then run the headless smoke test (the only CI
  signal that the app actually starts); Linux apt-installs WebKit2GTK + typelibs. Final
  job attaches the artifacts to the GitHub Release, using the matching `changelog.md`
  section as notes.

Release flow: branch `release/vX.Y.Z` off `develop` (conventional commits) → PR to
`master` → auto bump + tag → release with all three OS artifacts. Artifacts are unsigned.

## 9. Conventions & open work

- Keep the engine **pure** and the pipeline order / §4 decisions intact; engine behavior
  changes always **with tests**.
- CI reuses `do` and `build/build.py` — keep `do` stdlib-only and the orchestrator
  self-contained; job display names in the workflows should stay stable.
- New config fields: add them to backend `Config`, `defaultConfig()` **and**
  `sanitizeConfig()` (numeric ones) so all three shapes stay in sync.
- Never import the store as bare `state` + write `$state` in a component (§6 trap).
- **Open:** keyboard shortcuts (only remaining polish item; dark mode shipped with the
  modern UI — `DESIGN.md` token set + header theme toggle, dark default).