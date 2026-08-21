"""Case modifier.

Changes the letter case of the base name. Modes:
  - "upper":    all characters uppercase
  - "lower":    all characters lowercase
  - "title":    first character of each word uppercase (``str.title``)
  - "sentence": first character uppercase, rest lowercase (``str.capitalize``)

Note: ``str.title`` capitalizes after apostrophes ("it's" -> "It'S"); that is the
documented, faithful behavior of the mode (see AGENTS.md section 4).
"""

from __future__ import annotations

from .models import CaseConfig, RenameFile

_MODES = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "sentence": str.capitalize,
}


def modify(files: list[RenameFile], cfg: CaseConfig) -> None:
    fn = _MODES.get(cfg.mode, str.upper)
    for f in files:
        f.new_base = fn(f.new_base)
