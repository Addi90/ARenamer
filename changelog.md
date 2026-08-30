# Changelog

All notable changes to the A-Renamer Tool are documented in this file.

## [0.4.0] - 2026-08-30

### Features
- feat: support custom modifier pipeline order in config (4e3a4d3)
- feat: drag-and-drop modifier ordering in sidebar (5945fd1)
- feat: show reset-order button when the modifier order was changed (ae978b4)
- feat(engine): support renaming directories as extension-less entries (020a12f)
- feat(api): list directories with type, accept dirs in preview/check/rename (c237921)
- feat(frontend): view toggles for files and directories in the store (7400b3a)
- feat(frontend): directory rows with type badge, view toggles, tree refresh (83ebeed)
- feat(frontend): add app logo and favicon (rounded purple folder + Helvetica 'A') (28a3913)
- feat(build): use the app logo as the native app icon (macOS .app + Windows exe) (76820a6)
- feat(ui): dismissible error banner (f0ffdef)
- feat: modern UI — design tokens, dark mode, APCA-tuned contrast (adb7108)

### Bug Fixes
- fix: use children snippet instead of deprecated slot in ModifierCard (f70e132)
- fix: mark insertion slot (between cards) while dragging modifiers (4e40732)
- fix: keep drop markers of the first modifier card visible (f0621af)
- fix(ci): add httpx2 to dev requirements (starlette TestClient needs it in clean envs) (ce385a2)
- fix(engine): treat dot-files as extension-less (whole name is the base) (90eb526)
- fix(frontend): resolve a11y warnings in the drag-and-drop modifier card (f53235d)
- fix(ui): anchor the header subtitle to the title baseline (7af3628)
- fix(build): never fail the build on icon (re)generation (c9c7c0a)
- fix(ui): directory tree no longer freezes at one level (ee02e25)
- fix(api): return a friendly 403 for unreadable directories (66c520d)
- fix: stray ellipsis next to file-list checkboxes (b459dcf)
- fix: use a real disabled state for disabled modifier panels (3973c83)
- fix: place Remove's range toggle on its own row (7c5e32a)
- fix: silence two svelte build warnings (f85e7df)

### Documentation
- docs: document adjustable modifier order (7087744)
- docs: document frontend test workflow (c1d22e5)
- docs: document CI workflows (ci/release/build) in README + AGENTS.md (10cf22e)
- docs: document directory renaming and list view toggles (972cafb)
- docs: trim AGENTS.md to the necessary — fix stale spots, drop filler (4b4ce6c)
- docs: align AGENTS.md and README with v0.3.0 (9585999)
- docs: sync AGENTS.md vitest counts to the new test suite (3dc5a92)
- docs: sync AGENTS.md, README and DESIGN.md with the modern UI branch (b95d940)

### Tests
- test: add vitest + testing-library scaffolding for frontend (2cd912d)
- test: cover config sanitize and i18n key parity (3ec8f66)
- test: unit test store actions with mocked api (b64e173)
- test: smoke test FileList, Dialog, RenameButton (676b3fb)
- test: move pytest suite to tests/backend/, keep frontend tests co-located (0072531)
- test: tighten frontend tests to their actual contracts (649af8b)
- test: add missing frontend coverage (api client + modifier panels) (403e97c)

### Build & Packaging
- build: run frontend vitest suite in 'do test' (7c5ad7f)

### CI
- ci: add GitHub Actions development pipeline (pytest, vitest, SPA build, version sync) (09c3465)
- ci: add release workflow (do bump + do tag on master merge) and build workflow (3-OS PyInstaller, smoke test, GitHub Release) (194a8d0)

### Other
- Merge branch 'release/v0.2.0' into develop (b5435bb)
- Merge pull request #4 from Addi90/feat/flexible-modifier-order (16bbe1d)
- Merge pull request #5 from Addi90/feat/frontend-tests (48a7f15)
- Merge pull request #8 from Addi90/feat/github-actions-for-development-and-release (dd1274a)
- Merge pull request #9 from Addi90/feat/folder-editing (6770216)
- Merge pull request #10 from Addi90/feat/add-logos-and-favicon (f5305c4)
- Merge pull request #11 from Addi90/fix/icon-build-fallback (bcea52c)
- Merge pull request #12 from Addi90/fix/tree-depth-and-permissions (ad3f2b9)
- Merge branch 'master' into develop (a46e57d)
- Merge pull request #19 from Addi90/docs/v0.3.0-doc-sync (b34d4ef)
- Merge pull request #21 from Addi90/port/modern-ui (14556ed)
- Merge pull request #20 from Addi90/test/frontend-hardening (ba21121)
- Merge pull request #23 from Addi90/release/v0.4.0 (e270f24)

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
