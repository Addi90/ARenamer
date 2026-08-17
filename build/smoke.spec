# -*- mode: python ; coding: utf-8 -*-
"""Throwaway spec to build the frozen smoke test (build/_smoke.py).

Validates that every module + native lib is bundled and the in-process server
serves the SPA - without opening a GUI window. Not part of the shipped app.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(SPEC)))  # noqa: F821
from _bundle import collect_bundle_deps  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))  # noqa: F821
STATIC_SRC = os.path.join(REPO_ROOT, "backend", "static")

datas, binaries, hiddenimports = collect_bundle_deps()
if os.path.isdir(STATIC_SRC):
    datas.append((STATIC_SRC, "static"))  # must match backend/main.py _base_dir()

a = Analysis(
    [os.path.join(REPO_ROOT, "build", "_smoke.py")],
    pathex=[REPO_ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="arenamer-smoke",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
)
