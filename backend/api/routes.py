"""API routes for the A-Renamer Tool.

Endpoints (all under ``/api``):
    GET  /list?path=      -> files in a directory (for the file list)
    GET  /dirs?path=      -> subdirectories (for the directory tree, lazy-loaded)
    POST /preview         -> per-file new-name preview for a selection + config
    POST /check           -> duplicate detection (names that would clobber existing)
    POST /rename          -> perform the renames on disk (with a duplicate safety net)

The rename workflow mirrors the original: the UI calls /check first (blocking warning
if any duplicates), shows its own confirmation dialog, then calls /rename. /rename also
re-checks for duplicates as a safety net and refuses (HTTP 409) rather than clobbering.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Query

from ..engine import Config, build_files, find_duplicates, perform_rename, preview
from .schemas import (
    CheckRequest,
    CheckResponse,
    DirEntry,
    DirsResponse,
    FileEntry,
    ListResponse,
    PreviewRequest,
    PreviewResponse,
    RenameError,
    RenameRequest,
    RenameResponse,
)

router = APIRouter(prefix="/api")


def _require_dir(path: str) -> str:
    if not path or not os.path.isdir(path):
        raise HTTPException(status_code=404, detail=f"Not a directory: {path!r}")
    return path


@router.get("/list", response_model=ListResponse)
def list_files(path: str = Query(...)) -> ListResponse:
    """List the files (not subdirectories) in ``path``, sorted by name."""
    _require_dir(path)
    entries: list[FileEntry] = []
    for name in sorted(os.listdir(path), key=str.lower):
        full = os.path.join(path, name)
        if os.path.isfile(full):
            st = os.stat(full)
            entries.append(FileEntry(name=name, size=st.st_size, mtime=st.st_mtime))
    return ListResponse(path=path, files=entries)


@router.get("/dirs", response_model=DirsResponse)
def list_dirs(path: str = Query(...)) -> DirsResponse:
    """List the immediate subdirectories of ``path`` (for tree navigation)."""
    _require_dir(path)
    entries: list[DirEntry] = []
    for name in sorted(os.listdir(path), key=str.lower):
        if name in (".", ".."):
            continue
        full = os.path.join(path, name)
        if os.path.isdir(full):
            entries.append(DirEntry(name=name, path=full))
    return DirsResponse(path=path, dirs=entries)


@router.post("/preview", response_model=PreviewResponse)
def api_preview(req: PreviewRequest) -> PreviewResponse:
    """Compute the new name for each selected file under the given config."""
    cfg = Config.from_dict(req.config)
    files = build_files(req.path, req.files)
    return PreviewResponse(path=req.path, previews=preview(files, cfg))


@router.post("/check", response_model=CheckResponse)
def api_check(req: CheckRequest) -> CheckResponse:
    """Report which selected files would clobber an existing file on rename."""
    cfg = Config.from_dict(req.config)
    files = build_files(req.path, req.files)
    dups = find_duplicates(files, cfg)
    return CheckResponse(duplicates=len(dups), names=dups)


@router.post("/rename", response_model=RenameResponse)
def api_rename(req: RenameRequest) -> RenameResponse:
    """Perform the renames on disk. Refuses (409) if any would clobber an existing file."""
    cfg = Config.from_dict(req.config)
    files = build_files(req.path, req.files)

    # Safety net: even if the client skipped /check, never clobber an existing file.
    dups = find_duplicates(files, cfg)
    if dups:
        raise HTTPException(status_code=409, detail={"duplicates": len(dups), "names": dups})

    result = perform_rename(files, cfg)
    return RenameResponse(renamed=result["renamed"], errors=[RenameError(**e) for e in result["errors"]])
