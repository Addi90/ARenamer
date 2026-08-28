"""API routes for the A-Renamer Tool.

Endpoints (all under ``/api``):
    GET  /list?path=      -> files and directories in a directory (for the file list)
    GET  /dirs?path=      -> subdirectories (for the directory tree, lazy-loaded)
    POST /preview         -> per-entry new-name preview for a selection + config
    POST /check           -> duplicate detection (names that would clobber existing)
    POST /rename          -> perform the renames on disk (with a duplicate safety net)

The rename workflow mirrors the original: the UI calls /check first (blocking warning
if any duplicates), shows its own confirmation dialog, then calls /rename. /rename also
re-checks for duplicates as a safety net and refuses (HTTP 409) rather than clobbering.
"""

from __future__ import annotations

import os
import sys

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


def _list_dir(path: str) -> list[str]:
    """The entry names of ``path`` (lowercase-sorted), with a friendly error if unreadable.

    A directory can exist yet be unreadable — macOS TCC blocks apps without the
    right permission (e.g. an external volume), which used to surface as a raw
    ``PermissionError`` traceback + opaque 500. Translate it into a 403 with an
    actionable message the UI can show in its error banner.
    """
    try:
        return sorted(os.listdir(path), key=str.lower)
    except PermissionError:
        hint = (
            " On macOS, grant the app access to this disk "
            "(System Settings → Privacy & Security → Full Disk Access)."
            if sys.platform == "darwin"
            else " Check the folder's permissions."
        )
        raise HTTPException(status_code=403, detail=f"Cannot read {path!r}: permission denied.{hint}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Cannot read {path!r}: {e}")


@router.get("/list", response_model=ListResponse)
def list_files(path: str = Query(...)) -> ListResponse:
    """List the entries (files *and* subdirectories) in ``path``, sorted by name.

    Every entry carries ``type`` (``"file"`` / ``"dir"``); the UI filters the
    two types with its view toggles (default: files shown, directories hidden).
    """
    _require_dir(path)
    entries: list[FileEntry] = []
    for name in _list_dir(path):
        full = os.path.join(path, name)
        try:
            st = os.stat(full)
        except OSError:
            continue  # vanished/broken entry; skip rather than fail the listing
        if os.path.isdir(full):
            entries.append(FileEntry(name=name, type="dir", size=0, mtime=st.st_mtime))
        elif os.path.isfile(full):
            entries.append(FileEntry(name=name, type="file", size=st.st_size, mtime=st.st_mtime))
    return ListResponse(path=path, files=entries)


@router.get("/dirs", response_model=DirsResponse)
def list_dirs(path: str = Query(...)) -> DirsResponse:
    """List the immediate subdirectories of ``path`` (for tree navigation)."""
    _require_dir(path)
    entries: list[DirEntry] = []
    for name in _list_dir(path):
        if name in (".", ".."):
            continue
        full = os.path.join(path, name)
        if os.path.isdir(full):
            entries.append(DirEntry(name=name, path=full))
    return DirsResponse(path=path, dirs=entries)


@router.get("/home")
def home() -> dict:
    """The user's home directory — a sensible default starting point for the UI."""
    return {"path": os.path.expanduser("~")}


@router.post("/preview", response_model=PreviewResponse)
def api_preview(req: PreviewRequest) -> PreviewResponse:
    """Compute the new name for each selected entry (files and dirs) under the config."""
    cfg = Config.from_dict(req.config)
    files = build_files(req.path, req.files, req.dirs)
    return PreviewResponse(path=req.path, previews=preview(files, cfg))


@router.post("/check", response_model=CheckResponse)
def api_check(req: CheckRequest) -> CheckResponse:
    """Report which selected entries would clobber an existing file or dir on rename.

    The existence check is cross-type: a directory target clobbers an existing
    file just as a file target clobbers an existing directory.
    """
    cfg = Config.from_dict(req.config)
    files = build_files(req.path, req.files, req.dirs)
    dups = find_duplicates(files, cfg)
    return CheckResponse(duplicates=len(dups), names=dups)


@router.post("/rename", response_model=RenameResponse)
def api_rename(req: RenameRequest) -> RenameResponse:
    """Perform the renames on disk (files and directories).

    Refuses (409) if any would clobber an existing entry.
    """
    cfg = Config.from_dict(req.config)
    files = build_files(req.path, req.files, req.dirs)

    # Safety net: even if the client skipped /check, never clobber an existing entry.
    dups = find_duplicates(files, cfg)
    if dups:
        raise HTTPException(status_code=409, detail={"duplicates": len(dups), "names": dups})

    result = perform_rename(files, cfg)
    return RenameResponse(renamed=result["renamed"], errors=[RenameError(**e) for e in result["errors"]])
