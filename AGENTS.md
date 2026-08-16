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

A desktop GUI for **bulk-renaming files**. The user:

1. Selects a directory (folder browser or built-in directory tree).
2. Selects one or more files in it (multi-select).
3. Configures zero or more **modifiers** (text operations) that transform each filename.
4. Sees a **live preview** of every selected file's new name as they tweak modifiers.
5. Clicks **Rename** to apply all transformations on disk (with duplicate + confirmation safeguards).

Core value: batch rename with a composable set of text operations, instant per-file
preview, and safe renaming. The UI is internationalized (German + English) with a
runtime language switcher.

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
3. Apply each **active** modifier in this fixed order:

   `Replace → If-Then → Remove → Add → Counting → Date`

Each modifier transforms `new_base` in place, feeding the next. **This order is part
of the contract** and must be preserved (it's locked in by `tests/test_engine.py`).

Only the **base name** is ever modified. The extension (everything from the last `.`
onward, dot included) is preserved and re-appended on rename. Files with no dot have
an empty extension; a leading-dot name like `.bashrc` yields an empty base.

---

## 3. Features / abilities (the full checklist)

Every item below must work in the rebuilt UI. The engine side of most of these is
already implemented and tested (Milestone 2); the UI wiring lands in later milestones.

### Navigation & selection
- Browse/select a directory (native folder dialog and/or a directory tree).
- Directory tree navigation that re-roots the file list (and clears selection).
- File list with **multi-selection**.
- "Select all" and "Clear selection" actions.
- Current-path display.

### Live preview
- Per-file "new name" preview column, updated instantly on any control change.
- Preview reflects the full modifier pipeline in the correct order (§2).

### Modifiers (all six, each independently toggleable; disabled controls greyed out)
- **Add / Insert** — prefix, suffix, and insert-at-position. (Insert applies first, then the name is wrapped `prefix + name + suffix`.)
- **If-Then** — condition (CONTAINS / CONTAINS-NOT, plain or regex, case option) evaluated against the file's *original* base name → consequence (add as PREFIX / INSERT-at-pos / SUFFIX).
- **Replace** — search (plain or regex, case option) → replacement; replaces all occurrences.
- **Remove** — first-n chars, last-n chars, and a character range (start–end) with an "until end" option. Ranges that run past a shorter name clamp to the actual end (no out-of-bounds).
- **Counting / Number** — start number, zero-padding (e.g. `001`), placed as prefix / suffix / insert-at-pos. Numbers follow on-screen list order, not alphabetical.
- **Date** — format (DD-MM-YYYY / YYYY-MM-DD / MM-DD-YYYY), separator, source (created / last-modified / today / custom + date picker), placed as prefix / suffix / insert-at-pos.

### Safety & workflow (the Rename button)
1. **Duplicate check** — re-run the pipeline; if any resulting name already exists on disk (skipping unchanged files), show a blocking **Warning** ("Found existing duplicate files for N new filename(s)!") with only an Abort button, and stop.
2. **Confirmation** — "Rename N File(s)?" with Ok / Abort (N = selected count).
3. On Ok → perform the renames; only rename files whose new name differs from the current one.
4. **Success** — "Successfully renamed N File(s)!"

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
- **Preview shows the full name** (`base + extension`) in the preview column — FIXED (the
  original showed the base name only). More useful and unambiguous; a display choice only.
- **No separator between a name and an appended number/date — PRESERVED (faithful).** The
  original appends/prepends the value directly, so `name` + number-suffix `01` + date-suffix
  yields e.g. `name012024-05-01`. If a nicer result is wanted, the user combines with **Add**
  (e.g. an `-` suffix). *Candidate enhancement for the modern UI: an optional separator.*
- **Invalid regex is a no-op** (does not crash the live preview) — a deliberate safety choice.
- **Empty Replace search is a no-op** (a deliberate safety choice). `str.replace("", x)` would
  otherwise insert the replacement between every character and mangle names on disk.

---

## 5. Repository layout

```
arenamer/
├── run.py                     # one-command launcher (desktop window, or web fallback)
├── requirements.txt           # runtime deps: fastapi, uvicorn, pywebview
├── requirements-dev.txt       # + pytest
├── backend/
│   ├── main.py                # FastAPI app: static mount, /api/health, pywebview bootstrap
│   ├── api/                   # API routes + Pydantic schemas (list/dirs/preview/check/rename)
│   ├── engine/                # PURE rename engine (no web deps) — the correctness core
│   │   ├── models.py          # RenameFile + Config dataclasses (+ JSON (de)serialization)
│   │   ├── pipeline.py        # compute/preview/find_duplicates/check_duplicates/perform_rename/build_files
│   │   ├── add.py remove.py replace.py number.py ifthen.py date.py
│   └── static/                # built SPA (gitignored; `npm run build` output)
├── frontend/                  # Svelte SPA (Vite)
│   ├── package.json  vite.config.js  index.html
│   └── src/
│       ├── main.js            # mounts the Svelte app
│       ├── App.svelte         # root: path bar + tree | file list layout + modifier panels + live-preview effect
│       ├── lib/api.js         # fetch client for /api/*
│       ├── lib/config.js      # defaultConfig() + sanitizeConfig() (plain JS, no runes)
│       ├── lib/i18n/          # en.js + de.js (string tables) and index.svelte.js (language $state, t())
│       ├── lib/state/         # store.svelte.js — central $state (files, selection, config, previews, dialog)
│       ├── components/        # FileList, DirectoryTree (+TreeNode), RenameButton, Dialog (done)
│       └── components/modifiers/  # all six panels: Replace, IfThen, Remove, Add, Counting, Date
└── tests/
    ├── test_engine.py         # engine suite (61 tests) — modifiers, pipeline order, edge cases
    └── test_api.py            # API suite (10 tests) — list/dirs/preview/check/rename over HTTP
```

### Engine public API (`backend/engine/__init__.py`)
- `Config` / `RenameFile` and the six modifier config dataclasses — from `models.py`.
- `compute(files, config)` — run the full pipeline (mutates each file's `new_base`).
- `build_files(path, names)` — build `RenameFile` objects (row = list position).
- `preview(files, config)` — per-file new-name info keyed by original name.
- `find_duplicates(files, config)` / `check_duplicates(...)` — names/count that would clobber an existing file.
- `perform_rename(files, config)` — rename on disk; returns `{renamed, errors}`.

The engine is **pure stdlib** (dataclasses, `re`, `os`, `datetime`) — no web deps — so it
is trivially unit-testable and reusable.

### API surface (`backend/api/routes.py`, all under `/api`)
- `GET  /list?path=` — files in a directory (name, size, mtime), sorted; subdirs excluded.
- `GET  /dirs?path=` — immediate subdirectories (for lazy tree navigation).
- `GET  /home`       — the user's home directory (default starting point for the UI).
- `POST /preview`  `{path, files[], config}` → per-file new-name preview.
- `POST /check`    `{path, files[], config}` → duplicate names that would clobber existing.
- `POST /rename`   `{path, files[], config}` → renames on disk; **409** if any would clobber.

`config` is a plain JSON object matching `Config.to_dict()` (see §3); the backend converts
it via `Config.from_dict`, so partial configs from the UI are fine. Unknown keys are ignored
and `null` values fall back to each field's default, so a cleared UI input never 500s. The
rename workflow is: UI calls `/check` (blocking warning if duplicates) → its own confirm
dialog → `/rename`.

### Frontend architecture (`frontend/src`)
- **`lib/state/store.svelte.js`** — the single source of truth. A module-level Svelte 5
  `$state` object (files, selection, config, previews, duplicateNames, dialog) plus action
  functions (`loadDir`, `openHome`, `goUp`, `toggleSelect`, `selectAll`, `clearSelection`,
  `refreshPreview`, `showDialog`, `checkDuplicates`, `performRename`). It uses the
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
- **`components/FileList.svelte`** — Name + New Name preview table, multi-select (row/checkbox
  click toggles; header checkbox selects all), a Select-all/Clear toolbar, and red highlighting
  of rows that would clobber an existing file. **`components/modifiers/`** — all six panels
  (Replace, If-Then, Remove, Add, Counting/Number, Date), each a self-contained section with
  an enable toggle + ✓/✗ indicator and controls greyed out when disabled; panels are rendered
  in `App.svelte` in pipeline order (§2) on a responsive grid.
- **`components/DirectoryTree.svelte`** (+ recursive `TreeNode.svelte`) — lazy directory tree
  rooted at home (`/api/dirs` per expansion); clicking a node re-roots the file list.
- **`components/RenameButton.svelte`** — drives the rename workflow: `/api/check` (blocking
  duplicate warning) → confirm dialog → `/api/rename` → success dialog, then re-lists the dir.
- **`components/Dialog.svelte`** — reusable modal (warning / confirm / info variants; Esc or
  backdrop click dismisses). Rendered once in `App.svelte`; driven by the store's `dialog` state.
- **`App.svelte`** — composes the header (title + language switcher), the path bar
  (Home / Up / Open), a two-column layout (directory tree | file list) and the modifier
  panels; a debounced `$effect` re-runs `/api/preview` whenever config, selection or
  directory changes (live preview).

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
python3 -m pytest tests/ -v             # from repo root
```

### Frontend (Svelte)
```sh
cd frontend && npm install
npm run dev                             # Vite dev server on :5173 (proxies /api -> :8000)
npm run build                           # emits to ../backend/static for the desktop app
```

For a full desktop run: start the backend (`python run.py` or `uvicorn backend.main:app`)
and either open http://127.0.0.1:8000 (after `npm run build`) or use the Vite dev server.

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

### Conventions for future work
- Keep the engine **pure** (no web/fs-side-effect deps beyond what a rename needs); put
  HTTP concerns in `backend/api/`. Add engine behavior changes **with tests**.
- The frontend is a single source of truth in `src/lib/state/`; components read/write the
  store and call `/api/*`. Never let a component compute rename results locally.
- Preserve the pipeline order (§2) and the behavior decisions in §4 unless explicitly told otherwise.
