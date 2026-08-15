"""Add / Insert modifier (AGENTS.md 5a).

For each file the *insert* string is applied first (at ``insert_pos``), then the
result is wrapped as ``prefix + name + suffix``. Empty strings are no-ops, exactly
like the original ``AddModifier::modify``.
"""

from __future__ import annotations

from .models import AddConfig, RenameFile


def _clamp(pos: int, length: int) -> int:
    """Clamp an insert position into [0, length] (QString::insert clamps to end)."""
    return max(0, min(pos, length))


def modify(files: list[RenameFile], cfg: AddConfig) -> None:
    for f in files:
        if cfg.insert:
            pos = _clamp(cfg.insert_pos, len(f.new_base))
            f.new_base = f.new_base[:pos] + cfg.insert + f.new_base[pos:]
        f.new_base = cfg.prefix + f.new_base + cfg.suffix
