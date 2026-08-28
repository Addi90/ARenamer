#!/usr/bin/env python3
"""Generate the native app icons from the logo (``frontend/public/favicon.svg``).

Outputs (all committed to ``build/icons/`` so builds on any OS can use them
without a rasterizer installed):

  arenamer.png   512px - runtime window icon (pywebview ``icon`` arg)
  arenamer.ico   16-256px multi-size - Windows exe icon (PyInstaller)
  arenamer.icns  macOS .app bundle icon (macOS only, via ``iconutil``)

Best effort by design: if cairosvg/Pillow are missing it prints a warning and
keeps the committed icons as-is, never failing the build.

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


def _rasterize(size: int, dest: str) -> None:
    import cairosvg

    cairosvg.svg2png(url=SVG_SRC, write_to=dest, output_width=size, output_height=size)


def main() -> int:
    if not os.path.isfile(SVG_SRC):
        sys.exit(f"error: logo not found: {SVG_SRC}")
    os.makedirs(ICONS_DIR, exist_ok=True)

    try:
        import cairosvg  # noqa: F401
        from PIL import Image
    except ImportError as exc:
        print(
            f"warning: {exc.name} not available - skipping icon regeneration "
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