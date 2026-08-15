"""The rename engine — pure Python, framework-agnostic.

This is the single source of truth for computing new filenames. Both the live
preview and the actual rename go through :func:`compute`, guaranteeing they agree.

Public API:
    Config, RenameFile          -- data models (see :mod:`backend.engine.models`)
    compute(files, config)      -- run the full modifier pipeline (see :mod:`pipeline`)
    build_files(path, names)    -- construct RenameFile objects from a dir + filenames
    preview(files, config)      -- per-file new-name info (for the UI column)
    check_duplicates(files, cfg)-- count results that would clobber an existing file
"""

from .models import (
    AddConfig,
    Config,
    CountingConfig,
    DateConfig,
    IfThenConfig,
    RemoveConfig,
    RenameFile,
    ReplaceConfig,
    split_name,
)
from .pipeline import build_files, check_duplicates, compute, preview

__all__ = [
    "Config",
    "RenameFile",
    "AddConfig",
    "IfThenConfig",
    "ReplaceConfig",
    "RemoveConfig",
    "CountingConfig",
    "DateConfig",
    "split_name",
    "compute",
    "build_files",
    "preview",
    "check_duplicates",
]
