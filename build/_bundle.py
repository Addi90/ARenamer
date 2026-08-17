"""Shared PyInstaller dependency-collection logic for A-Renamer build specs.

Imported by the ``.spec`` files (and reusable from a build script). Returns the
extra ``datas`` / ``binaries`` / ``hiddenimports`` needed so the frozen app bundles:

* pywebview's JS bridge + (Windows) loader libs,
* uvicorn's dynamically-imported loop/protocol modules, and
* (macOS only) the PyObjC frameworks behind the WKWebView driver.

Kept free of any ``SPEC`` reference so it can be imported from a plain script too.
"""

from __future__ import annotations

import sys

from PyInstaller.utils.hooks import collect_all


def collect_bundle_deps() -> tuple[list, list, list]:
    datas: list = []
    binaries: list = []
    hiddenimports: list = [
        # pywebview selects its GUI driver dynamically per platform; list them all
        # so the frozen app bundles whichever one the target OS picks.
        "webview.platforms.cocoa",         # macOS (PyObjC / WKWebView)
        "webview.platforms.gtk",           # Linux (WebKit2GTK via PyGObject)
        "webview.platforms.edgechromium",  # Windows (Edge WebView2)
        "webview.platforms.winforms",      # Windows fallback
        "webview.platforms.qt",            # optional Qt driver (all platforms)
        "webview.platforms.mshtml",        # legacy Windows fallback
        "webview.platforms.cef",           # optional CEF driver
    ]

    def _add(module: str) -> None:
        try:
            d, b, h = collect_all(module)
            datas.extend(d)
            binaries.extend(b)
            hiddenimports.extend(h)
        except Exception as exc:  # pragma: no cover - optional dependency
            print(f"[bundle] warn: collect_all({module!r}) failed: {exc}")

    _add("webview")
    _add("uvicorn")

    # macOS WKWebView driver depends on PyObjC; its compiled frameworks must be
    # bundled explicitly (no auto-hook exists for it). Darwin-only.
    if sys.platform == "darwin":
        for mod in (
            "objc",
            "PyObjCTools",
            "AppKit",
            "Foundation",
            "WebKit",
            "Quartz",
            "Security",
            "UniformTypeIdentifiers",
        ):
            _add(mod)

    return datas, binaries, hiddenimports
