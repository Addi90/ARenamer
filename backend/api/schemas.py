"""Pydantic request/response models for the A-Renamer API.

The modifier ``config`` is accepted as a plain JSON object (matching
``Config.to_dict()``) and converted via ``Config.from_dict``. This keeps the API
lenient: a UI that sends only the modifiers it has configured (partial config) works,
and unknown keys are ignored. See ``backend/engine/models.py`` for the full shape.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Directory / file browsing --------------------------------------------- #

class FileEntry(BaseModel):
    """One entry in a directory listing.

    ``type`` is ``"file"`` or ``"dir"``; directory entries report ``size: 0``.
    The client decides which types to show (view toggles) and which to select.
    """

    name: str
    type: str = "file"
    size: int = 0
    mtime: float = 0.0


class ListResponse(BaseModel):
    path: str
    files: list[FileEntry] = Field(default_factory=list)


class DirEntry(BaseModel):
    name: str
    path: str


class DirsResponse(BaseModel):
    path: str
    dirs: list[DirEntry] = Field(default_factory=list)


# --- Preview --------------------------------------------------------------- #

class PreviewItem(BaseModel):
    name: str
    type: str = "file"
    new_base: str
    ext: str
    full_new_name: str
    changed: bool


class PreviewRequest(BaseModel):
    path: str = ""
    files: list[str] = Field(default_factory=list)
    # Names in ``files`` that are directories (extension-less rename entries).
    dirs: list[str] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)


class PreviewResponse(BaseModel):
    path: str
    previews: dict[str, PreviewItem] = Field(default_factory=dict)


# --- Duplicate check ------------------------------------------------------- #

class CheckRequest(BaseModel):
    path: str = ""
    files: list[str] = Field(default_factory=list)
    dirs: list[str] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)


class CheckResponse(BaseModel):
    duplicates: int
    names: list[str] = Field(default_factory=list)


# --- Rename ---------------------------------------------------------------- #

class RenameRequest(BaseModel):
    path: str = ""
    files: list[str] = Field(default_factory=list)
    dirs: list[str] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)


class RenameError(BaseModel):
    name: str
    error: str


class RenameResponse(BaseModel):
    renamed: int
    errors: list[RenameError] = Field(default_factory=list)
