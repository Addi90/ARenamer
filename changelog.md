# Changelog

All notable changes to the A-Renamer Tool are documented in this file.

## [0.2.0] - 2026-08-22

### Features
- feat: add Case modifier to engine (upper/lower/title/sentence) + tests (a9a2a7e)
- feat: add Case modifier panel to frontend (select, i18n, pipeline order) (224acdf)
- feat: extend Case modifier with word cases (camel/pascal/snake/kebab/constant/train) (320a9d6)
- feat: add word-case options to Case panel (UI + i18n + docs) (323b6cd)

### Bug Fixes
- fix: re-root directory tree to follow current path (up / open) (e422591)
- fix: render directory tree (legacy $state store collision in TreeNode) (261c09a)
- fix: remove double declaration of rowEl (1be79aa)

### Documentation
- docs: Case modifier in README/AGENTS.md + plan (665845d)
- docs: add README.md info about dev. setup (9824d3c)

### Build & Packaging
- build: add release tooling: do bump (semver + changelog + tag) and do changelog backfill (8861ffb)
- build: add do build and do test commands (venv-aware) (3df793f)

### Chores
- chore: decouple tagging from `do bump` (new master-only `do tag`) (9b16bc5)

### Other
- Merge pull request #2 from Addi90/add-upper-lower-case-modifier (4f7d8e9)
- Merge branch 'fix-directory-tree-view' into develop (e692973)

## [0.1.0] - 2026-08-19

### Other
- scaffold + rename engine (milestones 1-2) (fead2e7)
- add rename API layer (milestone 3) (f4366cf)
- add frontend core: store, live preview, add modifier (milestone 4) (f644cd6)
- add directory tree, rename workflow + dialogs (milestone 5) (bfb2ad6)
- add all modifier panels + config sanitization (milestone 6) (d5da7eb)
- add i18n: German + English, runtime switcher, locale auto-detect (milestone 7) (b072c47)
- fix modifier panel overflow; add optional name separator to date modifier (dbbaae7)
- fix file list overflow: truncate long names with ellipsis instead of stretching the view (45f0cd0)
- add full-viewport three-pane layout + PyInstaller packaging (d6c3bbe)
- add README: feature overview, quick start, dev and packaging instructions (e0e520a)
- add GPL v3 license: LICENSE file, README section with copyright, pyproject metadata (c690657)
