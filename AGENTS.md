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
- **Preview shows the base name** (extension hidden) in the preview column — PRESERVED.
- **No separator between a name and an appended number/date — PRESERVED (faithful).** The
  original appends/prepends the value directly, so `name` + number-suffix `01` + date-suffix
  yields e.g. `name012024-05-01`. If a nicer result is wanted, the user combines with **Add**
  (e.g. an `-` suffix). *Candidate enhancement for the modern UI: an optional separator.*
- **Invalid regex is a no-op** (does not crash the live preview) — a deliberate safety choice.

---

## 5. Repository layout

```
arenamer/
├── run.py                     # one-command launcher (desktop window, or web fallback)
├── requirements.txt           # runtime deps: fastapi, uvicorn, pywebview
├── requirements-dev.txt       # + pytest
├── backend/
│   ├── main.py                # FastAPI app: static mount, /api/health, pywebview bootstrap
│   ├── api/                   # API route modules (Milestone 3: list / preview / rename)
│   ├── engine/                # PURE rename engine (no web deps) — the correctness core
│   │   ├── models.py          # RenameFile + Config dataclasses (+ JSON (de)serialization)
│   │   ├── pipeline.py        # compute() + preview() + check_duplicates() + build_files()
│   │   ├── add.py remove.py replace.py number.py ifthen.py date.py
│   └── static/                # built SPA (gitignored; `npm run build` output)
├── frontend/                  # Svelte SPA (Vite)
│   ├── package.json  vite.config.js  index.html
│   └── src/
│       ├── main.js            # mounts the Svelte app
│       ├── App.svelte         # root component (scaffold for now)
│       ├── lib/state/         # central store: files, selection, config (Milestone 4)
│       ├── components/        # FileList, DirectoryTree, RenameButton, … (Milestone 5)
│       └── components/modifiers/  # one component per modifier (Milestone 6)
└── tests/test_engine.py       # engine test suite (59 tests, all green)
```

### Engine public API (`backend/engine/__init__.py`)
- `Config` / `RenameFile` and the six modifier config dataclasses — from `models.py`.
- `compute(files, config)` — run the full pipeline (mutates each file's `new_base`).
- `build_files(path, names)` — build `RenameFile` objects (row = list position).
- `preview(files, config)` — per-file new-name info keyed by original name.
- `check_duplicates(files, config)` — count results that would clobber an existing file.

The engine is **pure stdlib** (dataclasses, `re`, `os`, `datetime`) — no web deps — so it
is trivially unit-testable and reusable.

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
| 3 | API: `GET /api/list`, `POST /api/preview`, `POST /api/rename` (duplicate check + confirm) | ⬜ next |
| 4 | Frontend core: central store (files, selection, config), live preview column | ⬜ |
| 5 | UI: file list (multi-select), directory tree, select-all/clear, path bar, Rename button + dialogs | ⬜ |
| 6 | Modifier panels: all six with live preview + active indicators (✓/✗) | ⬜ |
| 7 | i18n: German + English, runtime switcher, system-locale auto-detect | ⬜ |
| 8 | Polish: dark mode, keyboard shortcuts, drag-and-drop, empty states, error handling | ⬜ |

### Conventions for future work
- Keep the engine **pure** (no web/fs-side-effect deps beyond what a rename needs); put
  HTTP concerns in `backend/api/`. Add engine behavior changes **with tests**.
- The frontend is a single source of truth in `src/lib/state/`; components read/write the
  store and call `/api/*`. Never let a component compute rename results locally.
- Preserve the pipeline order (§2) and the behavior decisions in §4 unless explicitly told otherwise.
