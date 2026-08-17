#!/usr/bin/env python3
"""Build the A-Renamer desktop app for the current operating system.

A single, cross-platform orchestrator (no shell differences to maintain). It:
  1. builds the Svelte frontend into ``backend/static`` (via npm), and
  2. runs PyInstaller with ``build/arenamer.spec``, then
  3. packages the result into a versioned archive under ``dist/``.

Run it with the project's virtualenv active (so PyInstaller + deps are available):
    python build/build.py                 # frontend + bundle + archive
    python build/build.py --no-frontend   # reuse an existing backend/static

Because PyInstaller cannot cross-compile, run this on each target OS to produce
that OS's artifact (macOS -> .app/zip, Windows -> zip, Linux -> tar.gz).
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BUILD_DIR)
FRONTEND_DIR = os.path.join(REPO_ROOT, "frontend")
STATIC_DIR = os.path.join(REPO_ROOT, "backend", "static")
DIST_DIR = os.path.join(REPO_ROOT, "dist")
SPEC = os.path.join(BUILD_DIR, "arenamer.spec")


def _version() -> str:
    try:
        import tomllib

        with open(os.path.join(REPO_ROOT, "pyproject.toml"), "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:  # pragma: no cover - metadata is optional
        return "0.0.0"


def _run(cmd: list[str], cwd: str) -> None:
    print(f"\n$ {' '.join(cmd)}  (in {cwd})", flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def build_frontend() -> None:
    npm = shutil.which("npm")
    if not npm:
        sys.exit("error: npm not found on PATH - install Node.js to build the frontend.")
    if not os.path.isdir(os.path.join(FRONTEND_DIR, "node_modules")):
        _run([npm, "install"], FRONTEND_DIR)
    _run([npm, "run", "build"], FRONTEND_DIR)
    if not os.path.isfile(os.path.join(STATIC_DIR, "index.html")):
        sys.exit(f"error: frontend build did not produce {STATIC_DIR}/index.html")


def pyinstaller_build() -> None:
    _run([sys.executable, "-m", "PyInstaller", SPEC, "--noconfirm"], REPO_ROOT)


def _archive_macos(version: str) -> str | None:
    app = os.path.join(DIST_DIR, "A-Renamer.app")
    if not os.path.isdir(app):
        return None
    out = os.path.join(DIST_DIR, f"A-Renamer-{version}-macOS.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(app):
            for name in files:
                full = os.path.join(root, name)
                zf.write(full, os.path.relpath(full, DIST_DIR))
    return out


def _archive_folder(version: str, ext: str) -> str | None:
    folder = os.path.join(DIST_DIR, "A-Renamer")
    if not os.path.isdir(folder):
        return None
    system = platform.system().lower()  # 'windows' | 'linux'
    out = os.path.join(DIST_DIR, f"A-Renamer-{version}-{system}{ext}")
    if ext == ".zip":
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(folder):
                for name in files:
                    full = os.path.join(root, name)
                    zf.write(full, os.path.relpath(full, DIST_DIR))
    else:  # .tar.gz
        with tarfile.open(out, "w:gz") as tf:
            tf.add(folder, arcname="A-Renamer")
    return out


def package(version: str) -> None:
    system = platform.system()
    if system == "Darwin":
        out = _archive_macos(version)
    elif system == "Windows":
        out = _archive_folder(version, ".zip")
    else:  # Linux / others
        out = _archive_folder(version, ".tar.gz")
    if out:
        size_mb = os.path.getsize(out) / (1024 * 1024)
        print(f"\nPackaged: {out} ({size_mb:.1f} MB)")


def _notes() -> None:
    system = platform.system()
    print("\nDistribution notes for this OS:")
    if system == "Darwin":
        print("  - Unsigned build: first launch, right-click the .app -> Open to")
        print("    clear the Gatekeeper warning (or add signing/notarization later).")
    elif system == "Windows":
        print("  - Requires the Microsoft Edge WebView2 Runtime (preinstalled on")
        print("    Windows 10/11). Unsigned exe may show a SmartScreen warning.")
    else:
        print("  - Requires the GTK WebKit system libs, e.g.:")
        print("      sudo apt install libwebkit2gtk-4.1-0   (or 4.0 on older distros)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-frontend", action="store_true", help="skip the npm build step")
    args = parser.parse_args()

    version = _version()
    print(f"Building A-Renamer v{version} for {platform.system()} ({platform.machine()})")

    if not args.no_frontend:
        build_frontend()
    pyinstaller_build()
    package(version)
    _notes()

    print(f"\nDone. Artifacts are in: {DIST_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
