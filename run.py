#!/usr/bin/env python3
"""One-command launcher for the A-Renamer Tool Python port.

Tries to open a native desktop window (pywebview). If pywebview isn't available
(e.g. headless environment), it falls back to running the local web server and
printing the URL so you can open it in a browser.

Usage:
    python run.py            # desktop window (or web fallback)
"""

from __future__ import annotations

import socket
import sys


def _free_port() -> int:
    """Ask the OS for a free TCP port on localhost (avoids clashing with :8000)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def main() -> int:
    host, port = "127.0.0.1", _free_port()

    try:
        import webview  # noqa: F401  (availability check)

        from backend.main import start_desktop

        print(f"Starting A-Renamer Tool desktop window on http://{host}:{port} ...")
        start_desktop(host=host, port=port)
    except ImportError:
        import uvicorn

        from backend.main import app

        print(f"pywebview not available; serving web UI at http://{host}:{port} (Ctrl+C to stop)")
        uvicorn.run(app, host=host, port=port)

    return 0


if __name__ == "__main__":
    sys.exit(main())
