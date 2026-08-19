# A-Renamer Tool

The A (or Adrian's) – Renamer is a tool for bulk renaming files in various ways. Its graphical user interface lets the user easily select a file directory and then select the files to bulk rename. In the file selection view it also provides a live preview of the new filename for each selected file.

This is a modern rebuild of the original Qt/C++ tool (see [`../ARenamerTool`](../ARenamerTool)): the rename engine is now pure Python, served by a small FastAPI backend and wrapped in a native desktop window via `pywebview`, with a Svelte single-page frontend.

The user has various ways of adding, removing and replacing content in a filename with the help of different modifiers that can also be used at the same time:

- **Add / Insert** — prefix, suffix, and insert-at-position
- **If-Then** — condition (contains / contains-not, plain or regex) → append / prepend / insert
- **Replace** — a sequence of characters or a regular expression (all occurrences)
- **Remove** — any number of characters from the front, back, or a given position range
- **Date** — add a date (created, last modified, today, or custom) in several formats
- **Counting** — add a running number (start value, zero-padding) in list order

Modifiers are applied in a fixed pipeline order (`Replace → If-Then → Remove → Add → Counting → Date`), each independently toggleable, with an instant per-file preview. Renaming is safe: a duplicate check runs first (blocking warning if any new name would clobber an existing file), followed by a confirmation dialog. The UI is internationalized (German + English) with a runtime language switcher.

## Quick start

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # fastapi, uvicorn, pywebview, pytest
python run.py                         # opens a desktop window (or web fallback)
```

`run.py` starts the backend and tries to open a native desktop window; in headless environments it falls back to serving the web UI at `http://127.0.0.1:<port>`.

## Development

```sh
# Backend / engine tests (the rename engine is the verified core)
python3 -m pytest tests/ -v

# Frontend (Svelte + Vite)
cd frontend && npm install
npm run dev        # dev server on :5173, proxies /api -> :8000
npm run build      # emits to ../backend/static for the desktop app
```

## Packaging (distributable desktop app)

The app is bundled with PyInstaller into a self-contained desktop application (no Python required by end users):

```sh
pip install -r requirements-build.txt   # pyinstaller
python build/build.py                   # frontend -> PyInstaller -> versioned archive in dist/
```

| OS | Artifact in `dist/` | Web engine | End-user requirement |
|----|---------------------|------------|----------------------|
| macOS | `A-Renamer.app` + `-macOS.zip` | WKWebView (cocoa) | none; unsigned → right-click → Open past Gatekeeper |
| Windows | `A-Renamer/` + `-win64.zip` | WebView2 (edgechromium) | Edge WebView2 Runtime (preinstalled on Win 10/11) |
| Linux | `A-Renamer/` + `-linux.tar.gz` | WebKit2GTK (gtk) | `libwebkit2gtk-4.x` system libraries |

PyInstaller cannot cross-compile, so run the build on each target OS to get that OS's artifact.

## Repository layout

```
arenamer/
├── run.py                     # one-command launcher (desktop window, or web fallback)
├── backend/
│   ├── main.py                # FastAPI app: static mount, /api/* routes, pywebview bootstrap
│   ├── api/                   # API routes + Pydantic schemas (list/dirs/preview/check/rename)
│   ├── engine/                # PURE rename engine (no web deps) — the correctness core
│   └── static/                # built SPA (gitignored; `npm run build` output)
├── frontend/                  # Svelte SPA (Vite): file list, directory tree, modifier panels
├── build/                     # PyInstaller packaging (spec + orchestrator)
└── tests/                     # pytest suites for engine and API
```

See [AGENTS.md](AGENTS.md) for the full feature checklist, behavior decisions vs. the original, and architecture details.

---

*This project was entirely ported from Qt/C++ by Qwen 3.8 27B running locally.*
