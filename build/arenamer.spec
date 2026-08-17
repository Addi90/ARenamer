# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the A-Renamer Tool desktop app.

Build from the repo root (so relative paths resolve):
    python -m PyInstaller build/arenamer.spec

Produces a one-folder bundle (``dist/A-Renamer/``) and, on macOS, an
``A-Renamer.app`` bundle. The built Svelte SPA (``backend/static``) is bundled
as data and served by the in-process FastAPI server that pywebview loads.

Cross-platform: PyObjC (the macOS WKWebView driver) is collected only on Darwin;
all pywebview platform drivers are listed so each OS bundles the one it needs.
"""

import os
import sys

# Make the shared collection helper (build/_bundle.py) importable from this spec.
sys.path.insert(0, os.path.dirname(os.path.abspath(SPEC)))  # noqa: F821
from _bundle import collect_bundle_deps  # noqa: E402

# Flip to False for release builds (no console window on Windows).
CONSOLE = True

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))  # noqa: F821

# Read the canonical app name/version from pyproject.toml (single source of truth),
# falling back to sensible defaults if it can't be read.
APP_NAME, APP_VERSION = "A-Renamer", "0.1.0"
try:
    import tomllib

    with open(os.path.join(REPO_ROOT, "pyproject.toml"), "rb") as _f:
        _proj = tomllib.load(_f)["project"]
    APP_NAME = "A-Renamer"  # display name (keeps spaces); package name differs
    APP_VERSION = _proj.get("version", APP_VERSION)
except Exception as exc:  # pragma: no cover - metadata is optional
    print(f"[spec] warn: could not read pyproject.toml ({exc}); using defaults")

# The built SPA. Must exist before building (run `npm run build` in frontend/).
STATIC_SRC = os.path.join(REPO_ROOT, "backend", "static")

datas, binaries, hiddenimports = collect_bundle_deps()

# Bundle the built SPA so the frozen app can serve it. backend/main.py's
# _base_dir() resolves to sys._MEIPASS (the bundle root) when frozen, so the
# static dir must sit directly under it - i.e. destpath "static", matching the
# source layout where it lives at <backend>/static under _base_dir().
if os.path.isdir(STATIC_SRC):
    datas.append((STATIC_SRC, "static"))
else:
    print(f"[spec] WARNING: {STATIC_SRC} not found - run `npm run build` first.")

a = Analysis(
    [os.path.join(REPO_ROOT, "run.py")],
    pathex=[REPO_ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib"],  # not used; keep the bundle lean
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],  # onedir: binaries/datas are gathered by COLLECT below
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=CONSOLE,
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)

# On macOS, wrap the one-folder bundle in a proper .app so it behaves like a
# native app (Dock icon, no terminal). Unsigned for now (see plan Phase 3).
if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        coll,
        name=f"{APP_NAME}.app",
        icon=None,  # placeholder; drop in a real .icns later (Phase 3)
        bundle_identifier="com.arenamer.tool",
    )
