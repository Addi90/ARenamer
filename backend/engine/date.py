"""Date modifier (AGENTS.md 5f).

Appends / inserts / prepends a formatted date. The date is taken from the chosen
source (file birth time, last-modified time, today, or a user-picked custom date),
formatted in the selected order using ``separator`` (e.g. ``2024-05-01``), then
placed as prefix, suffix (default), or inserted at ``insert_pos``.

An optional ``name_separator`` is placed between the date and the rest of the name
(e.g. ``photo-2024-05-01``). It is only emitted where name text actually exists on
that side, so an empty base (e.g. after Remove) never yields a dangling separator.
The default is ``""`` — direct concatenation, faithful to the original app.

Filesystem note: a true "created"/birth time is only available on macOS/Windows
(``st_birthtime``). On Linux it falls back to the last-modified time.
"""

from __future__ import annotations

import os
from datetime import date, datetime

from .models import DateConfig, RenameFile


def _clamp(pos: int, length: int) -> int:
    return max(0, min(pos, length))


def _source_date(f: RenameFile, cfg: DateConfig) -> date:
    if cfg.source == "today":
        return date.today()
    if cfg.source == "custom" and cfg.custom_date is not None:
        return cfg.custom_date

    try:
        st = os.stat(f.full_path)
    except OSError:
        return date.today()

    if cfg.source == "created":
        ts = getattr(st, "st_birthtime", None)
        if ts is None:  # Linux has no birth time -> fall back to mtime.
            ts = st.st_mtime
    else:  # "modified" (and any unknown source)
        ts = st.st_mtime

    return datetime.fromtimestamp(ts).date()


def _format(d: date, cfg: DateConfig) -> str:
    y = str(d.year)
    m = f"{d.month:02d}"
    dd = f"{d.day:02d}"
    sep = cfg.separator

    if cfg.format == "dmy":
        return f"{dd}{sep}{m}{sep}{y}"
    if cfg.format == "mdy":
        return f"{m}{sep}{dd}{sep}{y}"
    return f"{y}{sep}{m}{sep}{dd}"  # "ymd" (default)


def _name_sep(side: str, name_separator: str) -> str:
    """The separator between the date and one side of the name.

    Emitted only when that side actually has text, so a date placed at an edge
    (or against an empty base) never produces a dangling separator.
    """
    return name_separator if side and name_separator else ""


def modify(files: list[RenameFile], cfg: DateConfig) -> None:
    for f in files:
        s = _format(_source_date(f, cfg), cfg)

        if cfg.position == "prefix":
            f.new_base = s + _name_sep(f.new_base, cfg.name_separator) + f.new_base
        elif cfg.position == "insert":
            pos = _clamp(cfg.insert_pos, len(f.new_base))
            left, right = f.new_base[:pos], f.new_base[pos:]
            f.new_base = left + _name_sep(left, cfg.name_separator) + s + _name_sep(right, cfg.name_separator) + right
        else:  # suffix (default)
            f.new_base = f.new_base + _name_sep(f.new_base, cfg.name_separator) + s
