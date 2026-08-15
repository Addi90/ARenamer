"""Replace modifier (AGENTS.md 5c).

Replaces all occurrences of a search pattern with a replacement, honoring regex and
case-sensitivity.

Note: the original ``ReplaceModifier::modify`` had a bug where an unconditional
plain, case-insensitive ``replace()`` ran *again* after the regex/case branch,
double-applying the replacement. This port applies the replacement exactly once per
the selected mode (see AGENTS.md section 9).

An invalid regular expression is treated as a no-op rather than raising, so a
half-typed pattern never crashes the live preview.
"""

from __future__ import annotations

import re

from .models import ReplaceConfig, RenameFile


def modify(files: list[RenameFile], cfg: ReplaceConfig) -> None:
    for f in files:
        if cfg.regex:
            flags = 0 if cfg.case_sensitive else re.IGNORECASE
            try:
                f.new_base = re.sub(cfg.search, cfg.replace, f.new_base, flags=flags)
            except re.error:
                pass  # invalid pattern -> leave name unchanged
        else:
            if cfg.case_sensitive:
                f.new_base = f.new_base.replace(cfg.search, cfg.replace)
            else:
                # Case-insensitive *literal* replace via an escaped pattern.
                f.new_base = re.sub(re.escape(cfg.search), cfg.replace, f.new_base, flags=re.IGNORECASE)
