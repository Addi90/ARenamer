"""If-Then conditional modifier (AGENTS.md 5b).

"If the name matches a condition, then add a string." The condition is evaluated
against each file's *original* base name (``base``), while the consequence is applied
to the evolving ``new_base`` — matching the original behavior (AGENTS.md section 9).

The condition expression is a single field used for both plain and regex modes.
(The original kept separate ``conditionStr``/``conditionRegex`` members and guarded on
the plain one, which silently disabled regex-only conditions; this port guards on the
expression itself so both modes behave as intended.)

An invalid regular expression is treated as "no match" rather than raising.
"""

from __future__ import annotations

import re

from .models import IfThenConfig, RenameFile


def _matches(base: str, cfg: "IfThenConfig") -> bool:
    if not cfg.expression:
        return False

    if cfg.regex:
        flags = 0 if cfg.case_sensitive else re.IGNORECASE
        try:
            found = re.search(cfg.expression, base, flags=flags) is not None
        except re.error:
            return False
    else:
        if cfg.case_sensitive:
            found = cfg.expression in base
        else:
            found = cfg.expression.lower() in base.lower()

    return (not found) if cfg.contains_not else found


def modify(files: list[RenameFile], cfg: "IfThenConfig") -> None:
    for f in files:
        if not _matches(f.base, cfg):
            continue

        if cfg.action == "prefix":
            f.new_base = cfg.string + f.new_base
        elif cfg.action == "suffix":
            f.new_base = f.new_base + cfg.string
        elif cfg.action == "insert":
            pos = max(0, min(cfg.insert_pos, len(f.new_base)))
            f.new_base = f.new_base[:pos] + cfg.string + f.new_base[pos:]
