"""Rename pipeline (AGENTS.md section 3).

``compute`` is the single source of truth for both preview and rename. It is pure
and deterministic: every call starts from the original base names, so repeated calls
with the same inputs yield identical results (the original re-ran the whole pipeline
for preview, duplicate-check, and save).

Modifier application order is fixed and part of the contract:
    Replace -> Case -> If-Then -> Remove -> Add -> Counting -> Date

Only *active* (enabled) modifiers run.
"""

from __future__ import annotations

import os

from . import add, case, date, ifthen, number, remove, replace
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
    if config.case.enabled:
        case.modify(files, config.case)
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


def find_duplicates(files: list[RenameFile], config: Config) -> list[str]:
    """Return the original names of files whose resulting name already exists on disk.

    Mirrors ``Renamer::checkForDuplicates``: re-run the pipeline, then collect any file
    whose new name (path/new_base+ext) exists on disk, skipping files whose base name is
    unchanged. The API uses this to (a) show a blocking warning and (b) highlight the
    offending rows before a rename.
    """
    compute(files, config)
    dups: list[str] = []
    for f in files:
        if not f.changed:
            continue
        target = os.path.join(f.path, f.new_full_name) if f.path else f.new_full_name
        if os.path.exists(target):
            dups.append(f.name)
    return dups


def check_duplicates(files: list[RenameFile], config: Config) -> int:
    """Count of files that would clobber an existing file (see ``find_duplicates``)."""
    return len(find_duplicates(files, config))


def perform_rename(files: list[RenameFile], config: Config) -> dict:
    """Run the pipeline and rename files on disk. Returns a summary.

    Mirrors ``Renamer::save`` + ``RenameFile::renameFile``: only files whose new name
    differs from the current one and that still exist are renamed. Per-file OS errors are
    collected rather than raised, so one bad file doesn't abort the rest.

    Returns ``{"renamed": int, "errors": [{"name", "error"}, ...]}``.
    """
    compute(files, config)
    renamed = 0
    errors: list[dict] = []
    for f in files:
        if not f.changed:
            continue
        src = os.path.join(f.path, f.name) if f.path else f.name
        dst = os.path.join(f.path, f.new_full_name) if f.path else f.new_full_name
        try:
            if not os.path.exists(src):
                continue  # source gone; skip silently (matches the original)
            os.rename(src, dst)
            f.set_name(f.new_full_name)  # keep in-memory state consistent
            renamed += 1
        except OSError as e:
            errors.append({"name": f.name, "error": str(e)})
    return {"renamed": renamed, "errors": errors}
