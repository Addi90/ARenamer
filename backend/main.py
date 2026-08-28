"""FastAPI application for the A-Renamer Tool Python port.

Creates the app, mounts the rename API (``/api/*``, see :mod:`backend.api`), and
serves the built Svelte frontend from ``backend/static`` (when present).

Run for development (serves API + static on http://127.0.0.1:8000):
    uvicorn backend.main:app --reload

Run as a desktop window (opens pywebview):
    python run.py
"""

from __future__ import annotations

import os
import sys
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import api_router

def _base_dir() -> str:
    """Directory that holds the app's bundled data files.

    When frozen by PyInstaller, bundled data lives under ``sys._MEIPASS``; in a
    normal source checkout it is this file's own directory.
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


# Directory that holds the built Svelte assets (frontend `npm run build` output).
BACKEND_DIR = _base_dir()
STATIC_DIR = os.path.join(BACKEND_DIR, "static")


def _window_icon() -> str | None:
    """Path to the app's PNG icon, or None (window created without one).

    Frozen bundles carry the icons under ``<bundle>/icons`` (see
    ``build/arenamer.spec``); from a source checkout they live in ``build/icons``.
    """
    candidates = [os.path.join(BACKEND_DIR, "icons", "arenamer.png")]
    if not getattr(sys, "frozen", False):
        candidates.append(os.path.join(os.path.dirname(BACKEND_DIR), "build", "icons", "arenamer.png"))
    return next((c for c in candidates if os.path.isfile(c)), None)


def create_app() -> FastAPI:
    app = FastAPI(title="A-Renamer Tool", version="0.1.0")

    # Permissive CORS for local development (Vite dev server on another port).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "app": "A-Renamer Tool"}

    # Serve the built SPA if it exists (so `python run.py` works after a build).
    # Mounted last so the /api routes above take precedence.
    if os.path.isdir(STATIC_DIR):
        app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()


def start_desktop(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the local server in a background thread and open a desktop window.

    The pywebview import is deferred so that importing this module (e.g. for
    ``uvicorn backend.main:app`` or tests) never requires pywebview to be present.
    """
    import uvicorn

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait until the server is accepting connections.
    url = f"http://{host}:{port}"
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)

    import webview

    # Sized so all three panes (tree | file list | modifiers) are visible at once;
    # each pane scrolls internally, so smaller screens still work.
    icon = _window_icon()
    window = webview.create_window("A-Renamer Tool", url, width=1360, height=900)
    # pywebview 6.x: icon is a start() parameter (applied on GTK/QT; on macOS/
    # Windows the window icon comes from the .app/exe icon set in the spec).
    webview.start(**({"icon": icon} if icon else {}))

    # Clean shutdown: stop the server when the window closes.
    server.should_exit = True
