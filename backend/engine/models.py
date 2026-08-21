"""Data models for the rename engine.

These are plain, framework-agnostic dataclasses so the engine can be unit-tested
without any web dependency. The API layer (later milestone) serializes them to/from
JSON via :meth:`Config.from_dict` / :meth:`Config.to_dict`.

Naming mirrors the original Qt implementation (see AGENTS.md) so behavior is easy
to cross-check against the reference.
"""

from __future__ import annotations

import os
from dataclasses import MISSING, dataclass, field, asdict
from datetime import date
from typing import Optional


def split_name(name: str) -> tuple[str, str]:
    """Split a filename into (base, ext) at the *last* dot.

    Mirrors ``RenameFile`` in renamefile.cpp:
      - if there is a dot, base = everything before it, ext = from the dot onward
        (the extension *includes* its leading dot, e.g. ``".txt"``).
      - a file like ``".bashrc"`` yields base="" and ext=".bashrc" (dot at index 0).
      - a file with no dot yields base=name and ext="".
    """
    dot = name.rfind(".")
    if dot > -1:
        return name[:dot], name[dot:]
    return name, ""


@dataclass
class RenameFile:
    """One file participating in a rename batch."""

    name: str                 # original full filename, e.g. "photo.txt"
    path: str = ""            # directory the file lives in (no trailing slash)
    row: int = 0              # list order index; drives deterministic numbering

    base: str = field(default="", init=False)
    ext: str = field(default="", init=False)
    new_base: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.base, self.ext = split_name(self.name)
        self.new_base = self.base

    @property
    def full_path(self) -> str:
        return os.path.join(self.path, self.name) if self.path else self.name

    @property
    def new_full_name(self) -> str:
        """New filename including the (always preserved) extension."""
        return self.new_base + self.ext

    @property
    def changed(self) -> bool:
        return self.new_base != self.base

    def set_name(self, newname: str) -> None:
        """Adopt a new on-disk name and re-derive base/ext/new_base from it.

        Called after a successful rename so the in-memory object matches reality
        (a subsequent preview of an already-renamed file correctly shows no change).
        """
        self.name = newname
        self.base, self.ext = split_name(newname)
        self.new_base = self.base


# --------------------------------------------------------------------------- #
# Modifier configuration objects. Each has an `enabled` flag + its parameters,
# matching the seven modifiers documented in AGENTS.md section 5.
# --------------------------------------------------------------------------- #


@dataclass
class AddConfig:
    """Add / Insert modifier (AGENTS.md 5a)."""

    enabled: bool = False
    prefix: str = ""
    suffix: str = ""
    insert: str = ""
    insert_pos: int = 0


@dataclass
class IfThenConfig:
    """If-Then conditional modifier (AGENTS.md 5b).

    `expression` is the single source for both plain and regex modes. The
    condition is evaluated against each file's *original* base name.
    """

    enabled: bool = False
    contains_not: bool = False        # condition mode: CONTAINS (False) / CONTAINS NOT (True)
    expression: str = ""
    regex: bool = False
    case_sensitive: bool = False
    action: str = "prefix"            # "prefix" | "insert" | "suffix"
    string: str = ""
    insert_pos: int = 0


@dataclass
class ReplaceConfig:
    """Replace modifier (AGENTS.md 5c)."""

    enabled: bool = False
    search: str = ""
    replace: str = ""
    regex: bool = False
    case_sensitive: bool = False


@dataclass
class CaseConfig:
    """Case modifier: letter case of the base name (upper/lower/title/sentence)."""

    enabled: bool = False
    mode: str = "upper"               # "upper" | "lower" | "title" | "sentence"


@dataclass
class RemoveConfig:
    """Remove modifier (AGENTS.md 5d). Range positions are 1-based inclusive."""

    enabled: bool = False
    front: int = 0                    # remove first n chars
    back: int = 0                     # remove last n chars
    range_enabled: bool = False
    range_start: int = 1              # 1-based inclusive start
    range_end: int = 1                # 1-based inclusive end
    until_end: bool = False           # remove from range_start to end of name


@dataclass
class CountingConfig:
    """Counting / Number modifier (AGENTS.md 5e)."""

    enabled: bool = False
    position: str = "prefix"          # "prefix" | "suffix" | "insert"
    start: int = 1                    # first number in the sequence
    padding: int = 0                  # zero-pad width (e.g. 3 -> "001")
    insert_pos: int = 0               # used only when position == "insert"


@dataclass
class DateConfig:
    """Date modifier (AGENTS.md 5f)."""

    enabled: bool = False
    format: str = "ymd"               # "dmy" | "ymd" | "mdy"
    separator: str = "-"              # between day/month/year inside the date
    name_separator: str = ""          # between the date and the rest of the name ("" = none, faithful to original)
    source: str = "today"             # "created" | "modified" | "today" | "custom"
    custom_date: Optional[date] = None  # used only when source == "custom"
    position: str = "suffix"          # "prefix" | "suffix" | "insert"
    insert_pos: int = 0               # used only when position == "insert"


@dataclass
class Config:
    """The full rename recipe: which modifiers are active and how they're set."""

    add: AddConfig = field(default_factory=AddConfig)
    ifthen: IfThenConfig = field(default_factory=IfThenConfig)
    replace: ReplaceConfig = field(default_factory=ReplaceConfig)
    case: CaseConfig = field(default_factory=CaseConfig)
    remove: RemoveConfig = field(default_factory=RemoveConfig)
    counting: CountingConfig = field(default_factory=CountingConfig)
    date: DateConfig = field(default_factory=DateConfig)

    # -- (de)serialization for the JSON API ---------------------------------- #
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Build a Config from a plain dict (e.g. parsed JSON).

        Missing keys fall back to each dataclass's defaults, so partial configs
        from the UI are safe. Unknown keys are ignored. ``null`` values fall back
        to the field's default too (a cleared UI input must not 500 the API).
        """
        data = data or {}

        def _build(dc_type, key):
            raw = data.get(key) or {}
            spec = dc_type.__dataclass_fields__  # type: ignore[attr-defined]
            out = {}
            for k, v in raw.items():
                if k not in spec:
                    continue  # unknown keys are ignored
                if v is None:  # null -> field default (a cleared UI input must not crash)
                    f = spec[k]
                    if f.default is not MISSING:
                        v = f.default
                    elif f.default_factory is not None:
                        v = f.default_factory()
                out[k] = v
            return dc_type(**out)

        date_cfg = _build(DateConfig, "date")
        # JSON carries the custom date as an ISO string ("2024-05-01"); normalize it.
        if isinstance(date_cfg.custom_date, str):
            try:
                date_cfg.custom_date = date.fromisoformat(date_cfg.custom_date)
            except ValueError:
                date_cfg.custom_date = None

        return cls(
            add=_build(AddConfig, "add"),
            ifthen=_build(IfThenConfig, "ifthen"),
            replace=_build(ReplaceConfig, "replace"),
            case=_build(CaseConfig, "case"),
            remove=_build(RemoveConfig, "remove"),
            counting=_build(CountingConfig, "counting"),
            date=date_cfg,
        )

    def to_dict(self) -> dict:
        return asdict(self)
