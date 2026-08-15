"""Remove modifier (AGENTS.md 5d).

Removal order matches the original ``RemoveModifier::modify``:
  1. first *n* chars (front)
  2. last *n* chars (back)
  3. a character range, if enabled

Range positions are 1-based inclusive in the UI and converted to 0-based here.
If a range extends past the end of a (possibly shorter) name it is clamped to the
actual end, and "until end" removes from the start position through the final char.
"""

from __future__ import annotations

from .models import RemoveConfig, RenameFile


def modify(files: list[RenameFile], cfg: RemoveConfig) -> None:
    for f in files:
        n = f.new_base

        if cfg.front > 0:
            # QString::mid(n) -> "" when n exceeds length; Python slice matches.
            n = n[cfg.front:]

        if cfg.back > 0:
            # QString::left(negative) -> ""; guard so an over-large count empties it.
            n = n[: max(len(n) - cfg.back, 0)]

        if cfg.range_enabled and cfg.range_start >= 1:
            start = max(cfg.range_start - 1, 0)   # 0-based index of first char to drop
            length = len(n)

            if cfg.until_end:
                n = n[:start]
            elif cfg.range_end >= cfg.range_start:
                if cfg.range_end < length:
                    count = cfg.range_end - start  # == rangeEnd - rangeStart in the original
                    n = n[:start] + n[start + count:]
                else:
                    # Range runs past the end of a shorter name -> clamp to actual end.
                    n = n[:start]

        f.new_base = n
