"""Rename pipeline (AGENTS.md section 3).

``compute`` is the single source of truth for both preview and rename. It is pure
and deterministic: every call starts from the original base names, so repeated calls
with the same inputs yield identical results (the original re-ran the whole pipeline
for preview, duplicate-check, and save).

Modifier application order is fixed and part of the contract:
    Replace -> If-Then -> Remove -> Add -> Counting -> Date

Only *active* (enabled) modifiers run.
"""

from __future__ import annotations

import os

from . import add, date, ifthen, number, remove, replace
from .models import Config, RenameFile


def compute(files: list[RenameFile], config: Config) -> list[RenameFile]:
    """Run the full modifier pipeline over ``files`` (mutates their ``new_base``)."""
    # 1. reset every file to its original base name (resetNewBaseName)
    for f in files:
        f.new_base = f.base

    # 2. sort by row for deterministic, in-list-order numbering (sortList)
    files.sort(key=lambda f: f.row)

    # 3. apply each active modifier in the fixed order
    if config.replace.enabled:
        replace.modify(files, config.replace)
    if config.ifthen.enabled:
        ifthen.modify(files, config.ifthen)
    if config.remove.enabled:
        remove.modify(files, config.remove)
    if config.add.enabled:
        add.modify(files, config.add)
    if config.counting.enabled:
        number.modify(files, config.counting)
    if config.date.enabled:
        date.modify(files, config.date)

    return files


def build_files(path: str, names: list[str]) -> list[RenameFile]:
    """Build RenameFile objects from a directory path + filenames.

    ``row`` is the position in the provided list, so numbering/preview follow the
    order the UI sent (on-screen list order).
    """
    return [RenameFile(name=n, path=path, row=i) for i, n in enumerate(names)]


def preview(files: list[RenameFile], config: Config) -> dict[str, dict]:
    """Return per-file preview info keyed by the *original* filename.

    Mirrors ``Renamer::preview`` (which showed the new base name, extension hidden)
    but also exposes the extension and full new name so the UI can render however it
    likes. The pipeline is run first, so previews always match what rename does.
    """
    compute(files, config)
    result: dict[str, dict] = {}
    for f in files:
        result[f.name] = {
            "name": f.name,
            "new_base": f.new_base,
            "ext": f.ext,
            "full_new_name": f.new_full_name,
            "changed": f.changed,
        }
    return result


def check_duplicates(files: list[RenameFile], config: Config) -> int:
    """Count files whose resulting name already exists on disk.

    Mirrors ``Renamer::checkForDuplicates``: re-run the pipeline, then count any file
    whose new name (path/new_base+ext) exists on disk, skipping files whose base name
    is unchanged. Used to block a rename that would clobber an existing file.
    """
    compute(files, config)
    count = 0
    for f in files:
        if not f.changed:
            continue
        target = os.path.join(f.path, f.new_full_name) if f.path else f.new_full_name
        if os.path.exists(target):
            count += 1
    return count
