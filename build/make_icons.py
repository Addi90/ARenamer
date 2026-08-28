#!/usr/bin/env python3
"""Generate the native app icons from the logo (``frontend/public/favicon.svg``).

Outputs (all committed to ``build/icons/`` so builds on any OS can use them
without a rasterizer installed):

  arenamer.png   512px - runtime window icon (pywebview ``icon`` arg)
  arenamer.ico   16-256px multi-size - Windows exe icon (PyInstaller)
  arenamer.icns  macOS .app bundle icon (macOS only, via ``iconutil``)

Best effort by design: if cairosvg/Pillow are missing (or the native cairo
library cannot be loaded - it then re-runs itself once with the library's
directory on the linker search path) it prints a warning and keeps the
committed icons as-is, never failing the build.

    python build/make_icons.py
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BUILD_DIR)
SVG_SRC = os.path.join(REPO_ROOT, "frontend", "public", "favicon.svg")
ICONS_DIR = os.path.join(BUILD_DIR, "icons")

ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
# iconset file -> pixel size (covers @2x variants up to 1024)
ICONSET = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def _import_cairosvg():
    """Import cairosvg.

    Raises ``ImportError`` if the pip package is missing, ``OSError`` if the
    native cairo library exists but is not on the dynamic linker's default
    search paths (cairocffi dlopens the bare name ``libcairo.2.dylib`` /
    ``libcairo.so.2``, so a Homebrew/apt install is invisible to it). In that
    case the caller can :func:`_relaunch_with_cairo`.
    """
    import cairosvg

    return cairosvg


def _cairo_lib_dir() -> str | None:
    """Return a directory containing the native cairo library, if any."""
    import ctypes.util

    soname = "libcairo.2.dylib" if sys.platform == "darwin" else "libcairo.so.2"
    candidates = [
        ctypes.util.find_library("cairo"),
        "/opt/homebrew/lib",            # Homebrew (Apple Silicon)
        "/usr/local/lib",               # Homebrew (Intel) / manual installs
        "/usr/lib",
        "/usr/lib/x86_64-linux-gnu",
        "/usr/lib/aarch64-linux-gnu",
    ]
    for base in candidates:
        if not base:
            continue
        path = base if base.endswith(soname) else os.path.join(base, soname)
        if os.path.isfile(path):
            return os.path.dirname(path)
    return None


def _relaunch_with_cairo(lib_dir: str) -> bool:
    """Re-exec this script with the cairo dir on the dyld/LD search path.

    ``DYLD_FALLBACK_LIBRARY_PATH``/``LD_LIBRARY_PATH`` are read by the dynamic
    linker at process start, so the only way to reach a cairo install that is
    off the default paths is a one-shot re-exec. Returns ``False`` if this is
    already the re-exec (no loop) or the exec failed; on success it never
    returns.
    """
    if os.environ.get("_ARENAMER_ICONS_RELAUNCHED"):
        return False
    env = dict(os.environ)
    var = "DYLD_FALLBACK_LIBRARY_PATH" if sys.platform == "darwin" else "LD_LIBRARY_PATH"
    env[var] = lib_dir + os.pathsep + env.get(var, "")
    env["_ARENAMER_ICONS_RELAUNCHED"] = "1"
    print(f"cairo not on the default linker path - re-running with {var}={lib_dir}", flush=True)  # flush: execve discards unflushed buffers
    try:
        os.execve(sys.executable, [sys.executable, os.path.abspath(__file__)] + list(sys.argv[1:]), env)
    except OSError as exc:
        print(f"warning: re-exec failed ({exc}); keeping the committed icons")
    return False


def _rasterize(size: int, dest: str) -> None:
    import cairosvg

    cairosvg.svg2png(url=SVG_SRC, write_to=dest, output_width=size, output_height=size)


def main() -> int:
    if not os.path.isfile(SVG_SRC):
        sys.exit(f"error: logo not found: {SVG_SRC}")
    os.makedirs(ICONS_DIR, exist_ok=True)

    try:
        _import_cairosvg()
    except ImportError:
        print(
            "warning: cairosvg not available - skipping icon regeneration "
            "(using the committed build/icons/*.png|.ico|.icns)."
        )
        return 0
    except OSError:
        lib_dir = _cairo_lib_dir()
        if lib_dir and _relaunch_with_cairo(lib_dir):
            pass  # re-exec in progress / failed; fall through and give up below
        print(
            "warning: native cairo library could not be loaded - skipping icon "
            "regeneration (using the committed build/icons/*.png|.ico|.icns)."
        )
        return 0
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print(
            "warning: Pillow not available - skipping icon regeneration "
            "(using the committed build/icons/*.png|.ico|.icns)."
        )
        return 0

    all_sizes = sorted(set(ICO_SIZES) | {512} | set(ICONSET.values()))

    # --- PNG (window icon, 512) ---------------------------------------------
    png = os.path.join(ICONS_DIR, "arenamer.png")
    _rasterize(512, png)
    print(f"wrote {png}")

    # --- ICO (Windows exe) ----------------------------------------------------
    master = Image.open(png)  # 512px; Pillow derives every smaller size from it
    ico = os.path.join(ICONS_DIR, "arenamer.ico")
    master.save(ico, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"wrote {ico} ({', '.join(map(str, ICO_SIZES))}px)")

    # --- ICNS (macOS .app, needs the iconutil CLI) ----------------------------
    if sys.platform != "darwin":
        print("skipping .icns (macOS only; the committed file is reused)")
        return 0
    iconutil = shutil.which("iconutil")
    if iconutil is None:
        print("warning: iconutil not found - skipping .icns regeneration")
        return 0
    icns = os.path.join(ICONS_DIR, "arenamer.icns")
    with tempfile.TemporaryDirectory(prefix="arenamer-iconset-") as tmp:
        iconset = os.path.join(tmp, "arenamer.iconset")
        os.makedirs(iconset)
        for name, size in ICONSET.items():
            _rasterize(size, os.path.join(iconset, name))
        shutil.rmtree(icns, ignore_errors=True)
        result = os.system(f'{iconutil} -c icns "{iconset}" -o "{icns}"')
        if result != 0:
            print(f"warning: iconutil failed (exit {result}); keeping previous .icns if any")
            return 0
    print(f"wrote {icns}")
    return 0


if __name__ == "__main__":
    sys.exit(main())