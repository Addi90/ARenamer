<p align="center"><img src="build/icons/arenamer.png" width="144" alt="A-Renamer Tool logo"></p>

# A-Renamer Tool

The A (or Adrian's) – Renamer is a tool for bulk renaming files **and directories** in various ways. Its graphical user interface lets the user easily select a file directory and then select the entries (files and/or folders) to bulk rename. In the file selection view it also provides a live preview of the new name for each selected entry, and Files/Directories toggles control which entry types are shown (default: files only, the historical view).

This is a modern rebuild of the original Qt/C++ tool (see [`../ARenamerTool`](../ARenamerTool)): the rename engine is now pure Python, served by a small FastAPI backend and wrapped in a native desktop window via `pywebview`, with a Svelte single-page frontend.

The user has various ways of adding, removing and replacing content in a filename with the help of different modifiers that can also be used at the same time:

- **Add / Insert** — prefix, suffix, and insert-at-position
- **If-Then** — condition (contains / contains-not, plain or regex) → append / prepend / insert
- **Replace** — a sequence of characters or a regular expression (all occurrences)
- **Case** — change letter case (UPPERCASE, lowercase, Title Case, Sentence case, camelCase, PascalCase, snake_case, kebab-case, CONSTANT_CASE, train case)
- **Remove** — any number of characters from the front, back, or a given position range
- **Date** — add a date (created, last modified, today, or custom) in several formats
- **Counting** — add a running number (start value, zero-padding) in list order

Modifiers are applied in a pipeline (`Replace → Case → If-Then → Remove → Add → Counting → Date`) whose order you can also customize by dragging the modifier cards, each modifier independently toggleable, with an instant per-entry preview. Renaming is safe: a duplicate check runs first (blocking warning if any new name would clobber an existing entry — cross-type, so renaming a folder onto a file or vice versa is caught too), followed by a confirmation dialog. Directories are treated as *extension-less* entries: a folder named `backup.tar` renames to `x_backup.tar` (nothing is stripped). The UI is internationalized (German + English) with a runtime language switcher.

## Quick start

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # fastapi, uvicorn, pywebview, pytest (+httpx2 for the API tests)
python run.py                         # opens a desktop window (or web fallback)
```

(Or `pip install -e .` instead of the requirements files — `pyproject.toml` makes the
project pip-installable and provides the `arenamer` command.)

`run.py` starts the backend and tries to open a native desktop window; in headless environments it falls back to serving the web UI at `http://127.0.0.1:<port>`.

## Development

```sh
# Both test suites in one command (pytest engine + API, then vitest frontend)
./do test

# Or individually:
python3 -m pytest tests/ -v          # backend / engine (the verified core)
cd frontend && npm install
npm run dev        # dev server on :5173, proxies /api -> :8000
npm run build      # emits to ../backend/static for the desktop app
npm run test       # frontend vitest suite
```

`do` is a small stdlib-only release tool (`do bump` / `do tag` / `do changelog` / `do build` / `do test`), also used by the CI workflows.

## Packaging (distributable desktop app)

The app is bundled with PyInstaller into a self-contained desktop application (no Python required by end users):

```sh
pip install -r requirements-build.txt   # pyinstaller (+ cairosvg/pillow for optional icon regen)
python build/build.py                   # frontend -> icons -> PyInstaller -> versioned archive in dist/
```

| OS | Artifact in `dist/` | Web engine | End-user requirement |
|----|---------------------|------------|----------------------|
| macOS | `A-Renamer.app` + `-macOS.zip` | WKWebView (cocoa) | none; unsigned → right-click → Open past Gatekeeper |
| Windows | `A-Renamer/` + `-windows.zip` | WebView2 (edgechromium) | Edge WebView2 Runtime (preinstalled on Win 10/11) |
| Linux | `A-Renamer/` + `-linux.tar.gz` | WebKit2GTK (gtk) | `libwebkit2gtk-4.x` system libraries |

PyInstaller cannot cross-compile, so run the build on each target OS to get that OS's artifact.

## CI & Releases (GitHub Actions)

- **Development** (`ci.yml`): every pull request (and push to `develop`) runs, in parallel, the Python test suite (engine + API on Python 3.10 and 3.12), the Svelte/vitest frontend tests, the production frontend build, and a version-sync check (`pyproject.toml` vs `frontend/package.json`).
- **Release** (`release.yml`): when a `release/*` branch is merged into `master`, the version is bumped automatically from the conventional commits since the last tag (`do bump`), `changelog.md` is updated and committed, and the commit is tagged `v<version>` (`do tag`).
- **Builds** (`build.yml`): on each release tag, the desktop app is built on macOS, Windows and Linux (PyInstaller cannot cross-compile), validated with a headless smoke test of the frozen bundle, and published as a GitHub Release with the matching changelog section as the release notes.

So a release is simply: branch `release/vX.Y.Z` off `develop` → pull request to `master` → the tag and all three artifacts appear automatically.

## Repository layout

```
arenamer/
├── run.py                     # one-command launcher (desktop window, or web fallback)
├── do                         # stdlib-only release tooling (bump/tag/changelog/build/test)
├── pyproject.toml             # single source of truth for name + version
├── changelog.md               # per-version sections (written by `do bump`)
├── backend/
│   ├── main.py                # FastAPI app: static mount, /api/* routes, pywebview bootstrap
│   ├── api/                   # API routes + Pydantic schemas (list/dirs/preview/check/rename)
│   ├── engine/                # PURE rename engine (no web deps) — the correctness core
│   └── static/                # built SPA (gitignored; `npm run build` output)
├── frontend/                  # Svelte SPA (Vite): file list, directory tree, modifier panels
├── build/                     # PyInstaller packaging (spec, orchestrator, icons)
├── tests/                     # pytest suites for engine and API
└── .github/workflows/         # ci.yml, release.yml, build.yml
```

See [AGENTS.md](AGENTS.md) for the full feature checklist, behavior decisions vs. the original, and architecture details.

## License

Copyright (C) 2026 Adrian Crombach

This project is licensed under the [GNU General Public License v3](LICENSE) — improvements and redistributed versions must stay open source under the same license.

---

*This project (v0.1.0) was entirely ported from Qt/C++ by Qwen 3.8 27B running locally, development continues exclusively with the use of local LLMs.*
*Setup: Apple MacBook Pro M5 Pro 48GB with Opencode, LMStudio or oMLX*
