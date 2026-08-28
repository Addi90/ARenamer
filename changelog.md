# Changelog

All notable changes to the A-Renamer Tool are documented in this file.

## [0.3.0] - 2026-08-28

### Features
- feat: support custom modifier pipeline order in config (fced19b)
- feat: drag-and-drop modifier ordering in sidebar (9b91c9b)
- feat(engine): support renaming directories as extension-less entries (27e8580)
- feat(api): list directories with type, accept dirs in preview/check/rename (7a51988)
- feat(frontend): view toggles for files and directories in the store (7c7ea2f)
- feat(frontend): directory rows with type badge, view toggles, tree refresh (a1a86f2)
- feat: show reset-order button when the modifier order was changed (57a2ba4)
- feat(frontend): add app logo and favicon (rounded purple folder + Helvetica 'A') (47af772)
- feat(build): use the app logo as the native app icon (macOS .app + Windows exe) (c35fa15)
- feat(ui): dismissible error banner (6c80e5e)

### Bug Fixes
- fix: use children snippet instead of deprecated slot in ModifierCard (1ccd9f5)
- fix: mark insertion slot (between cards) while dragging modifiers (af44b6e)
- fix: keep drop markers of the first modifier card visible (9983dcc)
- fix(engine): treat dot-files as extension-less (whole name is the base) (faceae5)
- fix(frontend): resolve a11y warnings in the drag-and-drop modifier card (edd09ce)
- fix(ci): add httpx2 to dev requirements (starlette TestClient needs it in clean envs) (a6f8a60)
- fix(ui): directory tree no longer freezes at one level (dceb10e)
- fix(ui): anchor the header subtitle to the title baseline (6844ec8)
- fix(api): return a friendly 403 for unreadable directories (51d86aa)
- fix(build): never fail the build on icon (re)generation (411de6e)
- fix: fix the build and release workflows to properly trigger on merge (1089079)

### Documentation
- docs: document adjustable modifier order (a5bcd98)
- docs: document frontend test workflow (6639f4d)
- docs: document directory renaming and list view toggles (c85796d)
- docs: document CI workflows (ci/release/build) in README + AGENTS.md (b53059c)
- docs: trim AGENTS.md to the necessary — fix stale spots, drop filler (0b14d49)

### Tests
- test: add vitest + testing-library scaffolding for frontend (722b671)
- test: cover config sanitize and i18n key parity (f84be97)
- test: unit test store actions with mocked api (ca37a19)
- test: smoke test FileList, Dialog, RenameButton (2c35b36)
- test: move pytest suite to tests/backend/, keep frontend tests co-located (d745b53)

### Build & Packaging
- build: run frontend vitest suite in 'do test' (79052b9)

### CI
- ci: add GitHub Actions development pipeline (pytest, vitest, SPA build, version sync) (324e92b)
- ci: add release workflow (do bump + do tag on master merge) and build workflow (3-OS PyInstaller, smoke test, GitHub Release) (9a32cd2)

### Other
- Merge branch 'release/v0.2.0' into develop (88dcd0b)
- Merge pull request #4 from Addi90/feat/flexible-modifier-order (de8b7b2)
- Merge pull request #5 from Addi90/feat/frontend-tests (1276dad)
- Merge pull request #8 from Addi90/feat/github-actions-for-development-and-release (7e0ef78)
- Merge pull request #9 from Addi90/feat/folder-editing (44a780b)
- Merge pull request #10 from Addi90/feat/add-logos-and-favicon (c757e5a)
- Merge pull request #11 from Addi90/fix/icon-build-fallback (575da2b)
- Merge pull request #12 from Addi90/fix/tree-depth-and-permissions (f4d40ee)
- Merge branch 'fix/github-release-workflow' into release/v0.3.0 (5c941e5)
- Merge pull request #17 from Addi90/release/v0.3.0 (4c1ad14)

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
