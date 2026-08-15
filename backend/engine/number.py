"""Counting / Number modifier (AGENTS.md 5e).

Files are numbered in list order: file *i* gets ``start + i``, zero-padded to
``padding`` width when shorter (e.g. padding 3 -> "001"), then placed as prefix,
suffix, or inserted at ``insert_pos``.

The pipeline sorts files by row before calling this (matching the original, which
re-sorted here), so numbering follows on-screen list order, not alphabetical.
"""

from __future__ import annotations

from .models import CountingConfig, RenameFile


def _clamp(pos: int, length: int) -> int:
    return max(0, min(pos, length))


def modify(files: list[RenameFile], cfg: CountingConfig) -> None:
    for i, f in enumerate(files):
        num = str(cfg.start + i)
        if cfg.padding > 0 and len(num) < cfg.padding:
            num = num.zfill(cfg.padding)

        if cfg.position == "prefix":
            f.new_base = num + f.new_base
        elif cfg.position == "suffix":
            f.new_base = f.new_base + num
        elif cfg.position == "insert":
            pos = _clamp(cfg.insert_pos, len(f.new_base))
            f.new_base = f.new_base[:pos] + num + f.new_base[pos:]
