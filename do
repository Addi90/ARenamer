#!/usr/bin/env python3
"""Release tooling for the A-Renamer Tool.

Commands:
    do bump [major|minor|patch] [--dry-run] [--no-tag]
        Decide the semver bump from the commits since the last version tag
        (conventional-commit style: feat -> minor, fix/perf -> patch,
        '!' or BREAKING CHANGE -> major; docs/chore-only still releases a
        patch), update the version in pyproject.toml (and
        frontend/package.json), prepend a new section to changelog.md,
        commit both and tag the release as v<version>.

    do changelog
        (Re)write changelog.md sections for all existing version tags that
        do not have a section yet. Does not change the version or tag.

    do build [--no-frontend]
        Build the desktop app for the current OS (frontend -> PyInstaller ->
        versioned archive in dist/), using the project virtualenv.

    do test
        Run the pytest suite (engine + API) with the project virtualenv.

The version in pyproject.toml is the single source of truth (build/build.py
reads it); tags are named v<version>. Run with the repo's virtualenv active
is not required - this script only uses the Python standard library.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PYPROJECT = os.path.join(REPO_ROOT, "pyproject.toml")
PACKAGE_JSON = os.path.join(REPO_ROOT, "frontend", "package.json")
CHANGELOG = os.path.join(REPO_ROOT, "changelog.md")

HEADER = (
    "# Changelog\n"
    "\n"
    "All notable changes to the A-Renamer Tool are documented in this file.\n"
)

GROUPS = [
    ("feat", "Features"),
    ("fix", "Bug Fixes"),
    ("perf", "Performance"),
    ("refactor", "Refactoring"),
    ("docs", "Documentation"),
    ("test", "Tests"),
    ("build", "Build & Packaging"),
    ("ci", "CI"),
    ("chore", "Chores"),
    ("style", "Style"),
]
OTHER = "Other"
SECTION_RE = re.compile(r"(?ms)^## \[(\d+\.\d+\.\d+)\][^\n]*\n.*?(?=^## \[\d+\.\d+\.\d+\]|\Z)")


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def read_version() -> str:
    import tomllib

    with open(PYPROJECT, "rb") as f:
        return tomllib.load(f)["project"]["version"]


def set_version(version: str) -> None:
    with open(PYPROJECT, "r", encoding="utf-8") as f:
        src = f.read()
    new, n = re.subn(r'(?m)^version\s*=\s*"[^"]*"', f'version = "{version}"', src)
    if n != 1:
        sys.exit("error: expected exactly one version line in pyproject.toml")
    with open(PYPROJECT, "w", encoding="utf-8") as f:
        f.write(new)
    if os.path.isfile(PACKAGE_JSON):
        with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
            pkg = f.read()
        new, n = re.subn(r'(?m)^(\s*)"version"\s*:\s*"[^"]*"', rf'\g<1>"version": "{version}"', pkg)
        if n == 1:
            with open(PACKAGE_JSON, "w", encoding="utf-8") as f:
                f.write(new)


def last_tag() -> str | None:
    try:
        return git("describe", "--tags", "--abbrev=0")
    except RuntimeError:
        return None


def bump_level(subject: str, body: str) -> str | None:
    if "BREAKING CHANGE" in body:
        return "major"
    m = re.match(r"^(\w+)(\([^)]*\))?!?:", subject.strip())
    if not m:
        return None
    if m.group(2) == "!":
        return "major"
    t = m.group(1).lower()
    if t == "feat":
        return "minor"
    if t in ("fix", "perf", "bugfix"):
        return "patch"
    return None


def group_of(subject: str) -> str:
    m = re.match(r"^(\w+)(\([^)]*\))?!?:", subject.strip())
    if m:
        t = m.group(1).lower()
        for key, label in GROUPS:
            if t == key:
                return label
    return "Other"


def commits_in_range(rng: str) -> list[tuple[str, str, str]]:
    """(hash, subject, body) for the commits in `rng`, oldest first."""
    out = git("log", "--reverse", "--format=%x01%H%x00%s%x00%b", rng)
    result = []
    for rec in out.split("\x01"):
        rec = rec.strip("\n")
        if not rec:
            continue
        h, s, b = rec.split("\x00", 2)
        result.append((h, s, b))
    return result


def decide_bump(commits: list[tuple[str, str, str]]) -> str | None:
    levels = [bump_level(s, b) for _, s, b in commits]
    if "major" in levels:
        return "major"
    if "minor" in levels:
        return "minor"
    if "patch" in levels:
        return "patch"
    return "patch" if commits else None


def bump_version(version: str, level: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        sys.exit(f"error: version {version!r} is not semver X.Y.Z")
    x, y, z = (int(p) for p in parts)
    if level == "major":
        return f"{x + 1}.0.0"
    if level == "minor":
        return f"{x}.{y + 1}.0"
    return f"{x}.{y}.{z + 1}"


def section_for(version: str, date: str, commits: list[tuple[str, str, str]]) -> str:
    lines = [f"## [{version}] - {date}", ""]
    groups: dict[str, list[str]] = {}
    for h, s, _ in commits:
        groups.setdefault(group_of(s), []).append(f"- {s} ({h[:7]})")
    for _, label in GROUPS:
        if label in groups:
            lines.append(f"### {label}")
            lines.extend(groups[label])
            lines.append("")
    if "Other" in groups:
        lines.append("### Other")
        lines.extend(groups["Other"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def read_changelog() -> str:
    if os.path.isfile(CHANGELOG):
        with open(CHANGELOG, "r", encoding="utf-8") as f:
            return f.read()
    return HEADER + "\n"


def write_changelog(content: str) -> None:
    with open(CHANGELOG, "w", encoding="utf-8") as f:
        f.write(content)


def insert_section(content: str, section: str) -> str:
    """Insert a new section after the header, before the first existing one."""
    m = re.search(r"(?m)^## \[\d+\.\d+\.\d+\]", content)
    if m:
        return content[: m.start()] + section + "\n" + content[m.start():]
    return content.rstrip() + "\n\n" + section


def version_key(v: str) -> tuple[int, int, int]:
    return tuple(int(p) for p in v.split("."))


def cmd_bump(args: argparse.Namespace) -> None:
    if git("status", "--porcelain"):
        sys.exit("error: working tree is not clean - commit or stash your changes first")
    base = read_version()
    tag = last_tag()
    if tag and tag[1:] != base:
        print(f"warning: last tag {tag} does not match pyproject version {base}")
    commits = commits_in_range(f"{tag}..HEAD" if tag else "HEAD")
    if not commits:
        print(f"nothing to do: no commits since {tag or 'the beginning'}")
        return
    level = args.level or decide_bump(commits)
    new = bump_version(base, level)
    date = datetime.date.today().isoformat()
    section = section_for(new, date, commits)
    print(f"bump: {base} -> {new} ({level}) from {len(commits)} commit(s) since {tag or 'the beginning'}")
    if args.dry_run:
        print("\n--- changelog.md (dry run, nothing written) ---\n")
        print(section)
        return
    set_version(new)
    write_changelog(insert_section(read_changelog(), section))
    git("add", "pyproject.toml", "changelog.md")
    if os.path.isfile(PACKAGE_JSON):
        git("add", "frontend/package.json")
    git("commit", "-m", f"chore(release): v{new}")
    if args.no_tag:
        print(f"committed release; tag v{new} skipped (--no-tag)")
    else:
        git("tag", f"v{new}")
        print(f"tagged v{new}")


def cmd_changelog(_args: argparse.Namespace) -> None:
    tags = [t for t in git("tag", "--list").splitlines() if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
    if not tags:
        sys.exit("no version tags found")
    tags.sort(key=lambda t: version_key(t[1:]), reverse=True)
    content = read_changelog()
    existing = {m.group(1): m.group(0) for m in SECTION_RE.finditer(content)}
    m = re.search(r"(?m)^## \[\d+\.\d+\.\d+\]", content)
    preamble = content[: m.start()] if m else content
    missing: list[tuple[str, str]] = []
    for i, t in enumerate(tags):
        v = t[1:]
        if v in existing:
            continue
        prev = tags[i + 1] if i + 1 < len(tags) else None
        commits = commits_in_range(f"{prev}..{t}" if prev else t)
        date = git("show", "-s", "--format=%cd", "--date=short", t)
        missing.append((v, section_for(v, date, commits)))
        print(f"added section for {t} ({len(commits)} commit(s))")
    if not missing:
        print("changelog.md is up to date")
        return
    sections = sorted(list(existing.items()) + missing, key=lambda kv: version_key(kv[0]), reverse=True)
    write_changelog(preamble.rstrip() + "\n\n" + "\n".join(text for _, text in sections))


def venv_python() -> str:
    """Prefer the project virtualenv's interpreter (has PyInstaller + deps)."""
    for name in (".venv", "venv"):
        for binname in ("bin/python", "Scripts/python.exe"):
            p = os.path.join(REPO_ROOT, name, binname)
            if os.path.isfile(p):
                return p
    return sys.executable


def cmd_build(args: argparse.Namespace) -> None:
    """Build the desktop app: frontend -> PyInstaller -> versioned archive in dist/."""
    py = venv_python()
    cmd = [py, os.path.join(REPO_ROOT, "build", "build.py")]
    if args.no_frontend:
        cmd.append("--no-frontend")
    print(f"building with {py}")
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def cmd_test(_args: argparse.Namespace) -> None:
    """Run the test suite (engine + API) with pytest."""
    py = venv_python()
    subprocess.run([py, "-m", "pytest", "tests/", "-v"], cwd=REPO_ROOT, check=True)


def main() -> None:
    p = argparse.ArgumentParser(prog="do", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    pb = sub.add_parser("bump", help="bump version, write changelog, commit and tag")
    pb.add_argument("level", nargs="?", choices=["major", "minor", "patch"], help="force the bump level")
    pb.add_argument("--dry-run", action="store_true", help="show what would happen, change nothing")
    pb.add_argument("--no-tag", action="store_true", help="commit the release but skip creating the tag")
    pb.set_defaults(func=cmd_bump)
    pc = sub.add_parser("changelog", help="backfill changelog.md sections for existing tags")
    pc.set_defaults(func=cmd_changelog)
    pbd = sub.add_parser("build", help="build the desktop app (frontend + PyInstaller + archive)")
    pbd.add_argument("--no-frontend", action="store_true", help="reuse an existing backend/static")
    pbd.set_defaults(func=cmd_build)
    pt = sub.add_parser("test", help="run the pytest suite (engine + API)")
    pt.set_defaults(func=cmd_test)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
