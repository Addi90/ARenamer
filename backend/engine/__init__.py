"""The rename engine — pure Python, framework-agnostic.

This is the single source of truth for computing new filenames. Both the live
preview and the actual rename go through :func:`compute`, guaranteeing they agree.

Public API:
    Config, RenameFile          -- data models (see :mod:`backend.engine.models`)
    compute(files, config)      -- run the full modifier pipeline (see :mod:`pipeline`)
    build_files(path, names, dirs=None) -- construct RenameFile objects; ``dirs`` marks
                                            directory entries (extension-less: whole name is base)
    preview(files, config)      -- per-file new-name info (for the UI column)
    check_duplicates(files, cfg)-- count results that would clobber an existing entry
"""

from .models import (
    AddConfig,
    CaseConfig,
    Config,
    CountingConfig,
    DateConfig,
    IfThenConfig,
    RemoveConfig,
    RenameFile,
    ReplaceConfig,
    split_name,
)
from .pipeline import (
    CANONICAL_ORDER,
    build_files,
    check_duplicates,
    compute,
    find_duplicates,
    perform_rename,
    preview,
)

__all__ = [
    "Config",
    "CANONICAL_ORDER",
    "RenameFile",
    "AddConfig",
    "CaseConfig",
    "IfThenConfig",
    "ReplaceConfig",
    "RemoveConfig",
    "CountingConfig",
    "DateConfig",
    "split_name",
    "compute",
    "build_files",
    "preview",
    "find_duplicates",
    "check_duplicates",
    "perform_rename",
]
