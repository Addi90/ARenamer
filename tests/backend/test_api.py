"""Tests for the FastAPI layer (Milestone 3).

Exercises /api/list, /api/dirs, /api/preview, /api/check and /api/rename against a
real temporary directory, confirming the endpoints drive the engine correctly and that
the rename safety workflow (duplicate detection + 409) behaves as specified.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from backend.main import create_app

    return TestClient(create_app())


@pytest.fixture()
def workdir(tmp_path):
    """A temp dir with a couple of files and one subdirectory."""
    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.txt").write_text("B")
    (tmp_path / "subdir").mkdir()
    return str(tmp_path)


# --- browsing -------------------------------------------------------------- #

def test_list_returns_typed_entries(client, workdir):
    # Files *and* subdirectories are listed, each with its type, sorted by name.
    r = client.get("/api/list", params={"path": workdir})
    assert r.status_code == 200
    entries = r.json()["files"]
    assert [(e["name"], e["type"]) for e in entries] == [
        ("a.txt", "file"),
        ("b.txt", "file"),
        ("subdir", "dir"),
    ]
    dir_entry = entries[2]
    assert dir_entry["size"] == 0  # dirs report size 0
    assert dir_entry["mtime"] >= 0


def test_list_missing_dir_404(client):
    r = client.get("/api/list", params={"path": "/no/such/dir/xyz123"})
    assert r.status_code == 404


def test_dirs(client, workdir):
    r = client.get("/api/dirs", params={"path": workdir})
    assert r.status_code == 200
    names = [d["name"] for d in r.json()["dirs"]]
    assert names == ["subdir"]


# --- preview --------------------------------------------------------------- #

def test_preview_add_prefix(client, workdir):
    r = client.post(
        "/api/preview",
        json={"path": workdir, "files": ["a.txt", "b.txt"], "config": {"add": {"enabled": True, "prefix": "x_"}}},
    )
    assert r.status_code == 200
    prev = r.json()["previews"]
    assert prev["a.txt"]["full_new_name"] == "x_a.txt"
    assert prev["b.txt"]["changed"] is True
    # requests without the `dirs` field: everything stays a regular file
    assert prev["a.txt"]["type"] == "file"


def test_preview_dir_is_extension_less(client, tmp_path):
    (tmp_path / "backup.tar").mkdir()  # a dir whose name contains a dot
    r = client.post(
        "/api/preview",
        json={
            "path": str(tmp_path),
            "files": ["backup.tar"],
            "dirs": ["backup.tar"],
            "config": {"add": {"enabled": True, "prefix": "x_"}},
        },
    )
    assert r.status_code == 200
    item = r.json()["previews"]["backup.tar"]
    assert item["type"] == "dir"
    assert item["ext"] == ""
    assert item["full_new_name"] == "x_backup.tar"  # whole name is the base


def test_preview_no_config_unchanged(client, workdir):
    r = client.post("/api/preview", json={"path": workdir, "files": ["a.txt"], "config": {}})
    assert r.json()["previews"]["a.txt"]["changed"] is False


# --- duplicate check ------------------------------------------------------- #

def test_check_detects_existing_target(client, tmp_path):
    (tmp_path / "source.txt").write_text("s")
    (tmp_path / "target.txt").write_text("t")  # exists -> renaming source->target collides
    r = client.post(
        "/api/check",
        json={
            "path": str(tmp_path),
            "files": ["source.txt"],
            "config": {"replace": {"enabled": True, "search": "source", "replace": "target"}},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["duplicates"] == 1
    assert "source.txt" in body["names"]


def test_check_no_collision(client, workdir):
    r = client.post(
        "/api/check",
        json={"path": workdir, "files": ["a.txt"], "config": {"add": {"enabled": True, "prefix": "x_"}}},
    )
    assert r.json()["duplicates"] == 0


def test_check_dir_into_existing_dir(client, tmp_path):
    (tmp_path / "source").mkdir()
    (tmp_path / "target").mkdir()
    r = client.post(
        "/api/check",
        json={
            "path": str(tmp_path),
            "files": ["source"],
            "dirs": ["source"],
            "config": {"replace": {"enabled": True, "search": "source", "replace": "target"}},
        },
    )
    assert r.status_code == 200
    assert r.json()["duplicates"] == 1
    assert "source" in r.json()["names"]


def test_check_dir_into_existing_file(client, tmp_path):
    (tmp_path / "source").mkdir()
    (tmp_path / "target.txt").write_text("t")
    r = client.post(
        "/api/check",
        json={
            "path": str(tmp_path),
            "files": ["source"],
            "dirs": ["source"],
            "config": {"replace": {"enabled": True, "search": "source", "replace": "target.txt"}},
        },
    )
    assert r.json()["duplicates"] == 1  # cross-type collision is caught


def test_check_file_into_existing_dir(client, tmp_path):
    (tmp_path / "target").mkdir()
    (tmp_path / "sourcefile").write_text("s")
    r = client.post(
        "/api/check",
        json={
            "path": str(tmp_path),
            "files": ["sourcefile"],
            "config": {"replace": {"enabled": True, "search": "sourcefile", "replace": "target"}},
        },
    )
    assert r.json()["duplicates"] == 1  # the (extension-less) new name is the dir


# --- rename ---------------------------------------------------------------- #

def test_rename_applies_and_reports(client, workdir):
    r = client.post(
        "/api/rename",
        json={"path": workdir, "files": ["a.txt", "b.txt"], "config": {"add": {"enabled": True, "prefix": "x_"}}},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["renamed"] == 2
    assert body["errors"] == []
    # files actually renamed on disk; originals gone
    assert os.path.exists(os.path.join(workdir, "x_a.txt"))
    assert os.path.exists(os.path.join(workdir, "x_b.txt"))
    assert not os.path.exists(os.path.join(workdir, "a.txt"))


def test_rename_refuses_to_clobber(client, tmp_path):
    (tmp_path / "source.txt").write_text("s")
    (tmp_path / "target.txt").write_text("t")
    r = client.post(
        "/api/rename",
        json={
            "path": str(tmp_path),
            "files": ["source.txt"],
            "config": {"replace": {"enabled": True, "search": "source", "replace": "target"}},
        },
    )
    assert r.status_code == 409  # safety net: would clobber target.txt
    assert r.json()["detail"]["duplicates"] == 1
    # nothing was renamed
    assert os.path.exists(os.path.join(str(tmp_path), "source.txt"))


def test_rename_unchanged_is_noop(client, workdir):
    r = client.post("/api/rename", json={"path": workdir, "files": ["a.txt"], "config": {}})
    assert r.status_code == 200
    assert r.json()["renamed"] == 0  # no config -> nothing changes


# --- renaming directories -------------------------------------------------- #

def test_rename_dir_succeeds_and_preserves_content(client, tmp_path):
    d = tmp_path / "Photos"
    d.mkdir()
    (d / "a.jpg").write_text("x")
    r = client.post(
        "/api/rename",
        json={
            "path": str(tmp_path),
            "files": ["Photos"],
            "dirs": ["Photos"],
            "config": {"add": {"enabled": True, "prefix": "archived_"}},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["renamed"] == 1
    assert body["errors"] == []
    assert (tmp_path / "archived_Photos" / "a.jpg").exists()
    assert not (tmp_path / "Photos").exists()


def test_rename_dir_unchanged_is_noop(client, tmp_path):
    (tmp_path / "Photos").mkdir()
    r = client.post(
        "/api/rename",
        json={"path": str(tmp_path), "files": ["Photos"], "dirs": ["Photos"], "config": {}},
    )
    assert r.status_code == 200
    assert r.json()["renamed"] == 0
    assert (tmp_path / "Photos").exists()


def test_rename_dir_refuses_to_clobber_file(client, tmp_path):
    (tmp_path / "source").mkdir()
    (tmp_path / "target.txt").write_text("t")
    r = client.post(
        "/api/rename",
        json={
            "path": str(tmp_path),
            "files": ["source"],
            "dirs": ["source"],
            "config": {"replace": {"enabled": True, "search": "source", "replace": "target.txt"}},
        },
    )
    assert r.status_code == 409  # safety net: cross-type clobber
    assert r.json()["detail"]["duplicates"] == 1
    assert (tmp_path / "source").is_dir()  # nothing was renamed
    assert (tmp_path / "target.txt").is_file()
