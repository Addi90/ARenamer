"""Frozen-bundle smoke test (no GUI).

Imports the full runtime stack, verifies the bundled SPA path resolves under
``sys._MEIPASS``, starts the in-process server, and hits ``/api/health`` + ``/``
over HTTP. Exits 0 on success, non-zero otherwise. Used to validate the PyInstaller
bundle without needing a window/WindowServer.
"""

from __future__ import annotations

import os
import sys
import threading
import time
import urllib.request


def main() -> int:
    print("SMOKE start; frozen =", getattr(sys, "frozen", False), flush=True)

    # 1. Import the whole stack - proves every module + native lib is bundled.
    import webview  # noqa: F401  (pulls the platform driver + PyObjC on macOS)
    import uvicorn  # noqa: F401

    from backend.main import STATIC_DIR, app

    print("SMOKE imported webview + uvicorn + backend.main", flush=True)
    print(f"SMOKE STATIC_DIR={STATIC_DIR} exists={os.path.isdir(STATIC_DIR)}", flush=True)
    if not os.path.isdir(STATIC_DIR):
        print("SMOKE FAIL: bundled static dir missing", flush=True)
        return 2

    # 2. Start the server on a free port in a background thread.
    import socket

    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    cfg = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()

    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)
    if not server.started:
        print("SMOKE FAIL: server did not start", flush=True)
        return 3

    base = f"http://127.0.0.1:{port}"
    ok = True
    for path in ("/api/health", "/"):
        try:
            with urllib.request.urlopen(base + path, timeout=5) as r:
                body = r.read()
            print(f"SMOKE GET {path} -> {r.status}, {len(body)} bytes", flush=True)
            if r.status != 200:
                ok = False
        except Exception as exc:  # noqa: BLE001
            print(f"SMOKE GET {path} -> ERROR {exc!r}", flush=True)
            ok = False

    server.should_exit = True
    print("SMOKE " + ("PASS" if ok else "FAIL"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
