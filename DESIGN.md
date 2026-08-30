# A-Renamer — Design System

Dark-first desktop web utility (pywebview / WKWebView, mouse + keyboard). Batch file &
directory renamer: directory tree · file list with live previews · 7-step modifier
pipeline. Accent family is derived from the product logo (`frontend/public/favicon.svg`,
purple folder gradient `#a855f7 → #6d28d9`).

Reference implementation of these tokens: `frontend/src/index.css` (the committed SPA's stylesheet).

```yaml
name: A-Renamer
description: >
  Dark-first desktop renaming utility. Layered dark surfaces, one logo-purple accent,
  mono filenames, dense 13px working grid, numbered modifier pipeline.
colors:
  bg: "#0e0f12"            # light: #f2f3f6
  surface: "#16181d"       # light: #ffffff
  surface-2: "#1d2026"     # light: #f6f7f9
  surface-3: "#242830"     # light: #eceef2
  border: "#262b33"        # light: #e4e7ee
  border-strong: "#333945" # light: #d3d8e2
  primary: "#8b36e8"        # filled button bg; light: #7c3aed
  primary-hover: "#6d28d9"  # both themes
  primary-contrast: "#ffffff" # both themes
  accent: "#a855f7"         # light: #7c3aed
  accent-deep: "#8b36e8"   # light: #6d28d9
  accent-bright: "#e9d5ff" # light: #6523d6
  accent-contrast: "#0e0f12" # light: #ffffff
  accent-soft: "#a855f724" # 14% alpha; light: #7c3aed17 (9%)
  sel: "#a855f71a"         # 10% alpha; light: #7c3aed0f (6%)
  row-hover: "#ffffff09"   # 3.5% alpha; light: #14182809
  success: "#70e4a1"       # light: #157a49
  danger: "#ffc1b8"        # light: #b42c21
  text: "#edeff2"          # light: #181b21
  muted: "#d0d6df"         # light: #545e6e
  faint: "#7c8694"         # light: #4e5767
typography:
  font-family: [system-ui, -apple-system, Segoe UI, Roboto, sans-serif]
  mono: [ui-monospace, SF Mono, Menlo, monospace]
  text-scale: [10.5, 11, 11.5, 12, 12.5, 13, 14]   # dense utility grid (not 1.25 modular)
rounded:
  sm: 8px
  md: 10px
  lg: 14px
  pill: 99px
spacing:
  unit: 4px               # grid 4/8/12/16/20; 2px subgrid for tight control padding
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.accent-contrast}"
    rounded: "{rounded.sm}"
    padding: 7px 14px
  button-ghost:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
    rounded: "{rounded.sm}"
    padding: 6px 12px
  chip-on:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-bright}"
    rounded: "{rounded.sm}"
  input:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
  pane:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.lg}"
  step-card:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
  step-number-chip:
    backgroundColor: "{colors.surface-3}"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
  step-number-chip-active:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-contrast}"
    rounded: "{rounded.pill}"
  badge:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-bright}"
    rounded: "{rounded.pill}"
  hint:
    textColor: "{colors.faint}"
  warning:
    textColor: "{colors.danger}"
  changed-name:
    textColor: "{colors.success}"
  row-hover:
    backgroundColor: "{colors.row-hover}"
  row-selected:
    backgroundColor: "{colors.sel}"
```

## Colors

Two themes, same token names. All values live in `:root` / `[data-theme]` blocks;
components use `var(--token)` only.

| Token | Dark | Light | Role |
|---|---|---|---|
| `--bg` | `#0e0f12` | `#f2f3f6` | page background |
| `--surface` | `#16181d` | `#ffffff` | panes, cards |
| `--surface-2` | `#1d2026` | `#f6f7f9` | inactive step cards, segment wells |
| `--surface-3` | `#242830` | `#eceef2` | step number chips (off) |
| `--border` | `#262b33` | `#e4e7ee` | hairlines, card borders |
| `--border-strong` | `#333945` | `#d3d8e2` | inactive status dots |
| `--text` / `--muted` / `--faint` | see frontmatter | see frontmatter | 3 text tiers |
| `--primary` / `--primary-hover` | `#8b36e8` / `#6d28d9` | `#7c3aed` / `#6d28d9` | filled primary button + hover (white text, APCA 82/89) |
| `--accent` / `--accent-deep` | `#a855f7` / `#8b36e8` | `#7c3aed` / `#6d28d9` | logo gradient stops |
| `--accent-bright` | `#e9d5ff` | `#6523d6` | accent text on soft fills (APCA ≥75 in both themes) |
| `--accent-soft` / `--sel` | 14% / 10% | 9% / 6% | tints, selection |
| `--success` | `#70e4a1` | `#157a49` | changed-name highlight |
| `--danger` | `#ffc1b8` | `#b42c21` | errors, warnings |

**Contrast (measured, gate: WCAG AA 4.5 hard floor, APCA 75 target for primary text):**

| Pair | Dark | Light |
|---|---|---|
| body (`--text` on `--surface`) | WCAG 15.4 · APCA 96 ✓ | WCAG 17.3 · APCA 104 ✓ |
| `--muted` on `--surface` | WCAG 12.1 · APCA 80 ✓ | WCAG 6.6 · APCA 82.5 ✓ |
| `--faint` on `--surface` | WCAG 4.8 · APCA 36.1* | WCAG 7.3 · APCA 85 ✓ (worst fill `--surface-3`: 75.1) |
| crumb (`--muted` on `--bg`) | WCAG 13.1 · APCA 81 ✓ | WCAG 5.9 · APCA 75 ✓ |
| primary button (white on `--primary`) | WCAG 5.5 · APCA 81.9 ✓ | WCAG 5.7 · APCA 82.8 ✓ |
| primary hover (white on `--primary-hover`) | WCAG 7.1 · APCA 88.3 ✓ | WCAG 7.3 · APCA 89.4 ✓ |
| changed name (`--success`) | WCAG 11.2 · APCA 75.8 ✓ | WCAG 5.4 · APCA 76.3 ✓ |
| badge (`--accent-bright` on soft) | WCAG 10.3 · APCA 81.7 ✓ | WCAG 6.6 · APCA 75.1 ✓ |
| `--danger` | WCAG 11.5 · APCA 76.9 ✓ | WCAG 6.3 · APCA 80.0 ✓ |

\* One documented deviation remains: dark `--faint` (APCA 36.1, WCAG 4.8 ✓).
It is the metadata tier (table headers, step numbers, 10.5–11.5px labels,
placeholders, hints) and only reads on `--surface`/`--surface-2`. Raising it to
APCA 75 would flatten it into `--muted` (APCA 80) and kill the 3-tier hierarchy —
the known APCA dark-mode tradeoff. (Duplicate-row *hover* is transient: danger
text on the 12% danger tint reaches APCA 67–73, WCAG ≥4.5 — accepted.) Every
other pair in both themes passes APCA 75 at the sizes where it is used.

**Known ceiling:** `data:` URI glyphs (e.g. the `<select>` chevron) cannot use
`var()` — their stroke color duplicates `--muted` per theme as a hardcoded value.
Kept to exactly that one exception.

**`@google/design.md lint` notes (0 errors, 5 accepted warnings):** the frontmatter
models one flat palette (dark values + light in comments), so (a) `chip-on`/`badge`
contrast warnings composite dark-theme ink over an alpha tint on a white canvas — the
per-theme measured values in the table above are the real ones; (b) `--border`/`--border-strong`
are reported orphaned because the schema's component sub-tokens (`backgroundColor`,
`textColor`, …) cannot express borders — they are used throughout per the Elevation rules; (c) `accent-deep`
is the logo's second gradient stop (`favicon.svg`) — brand vocabulary, kept for completeness.
`--primary-hover` is now an explicit token (both themes share `#6d28d9`).

## Typography

- UI: system stack. Filenames & paths: mono. Never a third family.
- Dense utility scale (14 base): 10.5 (field labels) · 11 (section headings, uppercase) ·
  11.5 (hints) · 12 (checkboxes) · 12.5 (mono names, crumbs) · 13 (rows, buttons) ·
  14 (default). We deliberately do not use a 1.25 modular scale — a renaming tool's
  value is rows-per-screen, not display typography.
- Uppercase + `letter-spacing: 0.06–0.08em` reserved for section headings only.
- Tabular figures (`font-variant-numeric: tabular-nums`) for counts.

## Layout

Three panes: tree (232px fixed) · file list (flex) · pipeline (332px fixed), 12px gutters,
12/16/20px outer padding. Spacing snaps to the 4px grid (4/8/12/16/20); tight
control-internal padding may use the 2px subgrid. Below 980px the
panes stack. The window never scrolls vertically; panes scroll internally.

## Elevation

Three named levels, no ad-hoc shadows:

| Level | Recipe (dark) | Use |
|---|---|---|
| `--shadow` (resting) | `inset 0 1px 0 rgba(255,255,255,.04), 0 8px 28px rgba(0,0,0,.38)` | panes, dialogs |
| `--shadow-btn` (raised) | `0 1px 2px rgba(0,0,0,.4), inset 0 0 0 1px rgba(255,255,255,.06)` | primary button |
| focus ring | `0 0 0 3px var(--accent-soft)` | focused inputs, active status dots |

Light theme uses `rgba(16,24,40,…)` at 5–12%. Separation order: whitespace → background
shift (`--surface-2`) → elevation. A border is the last resort; panes combine a 1px
`--border` with `--shadow` (border + elevation together is the pane recipe, never a
border alone as a card).

## Shapes

`--r-sm: 8px` (inputs, buttons, chips) · `--r-md: 10px` (step cards) · `--r-lg: 14px`
(panes, dialogs) · `99px` (pills, dots, badges). No other radii.

## Components & states

Every interactive element declares the full state set. Global contract:

```css
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
:disabled { opacity: 0.5; cursor: not-allowed; }
.primary:active { transform: translateY(1px); }  /* pressed: physical dip on pill controls */
.ghost:active, .icon-btn:active, .chip:active, .lang:active { transform: translateY(1px); }
.crumb:active, .node:active { background: var(--surface-3); }  /* flat surfaces deepen instead */
```

Inputs override the outline with the 3px `--accent-soft` ring (their focus-visible
treatment); everything else keeps the outline.

- **Button (primary)** — `--primary` / `--primary-contrast` (white in both themes) /
  `--r-sm` / `--shadow-btn`; hover → `--primary-hover`. The dark button uses
  `--accent-deep` as its base stop: white on `--accent` is APCA 37, on `--accent-deep`
  82. Disabled → 45% opacity; selection count in a pill (dark: `--text` bg / `--bg`
  text, APCA 96; light: `--accent-contrast` bg / `--accent` text, 77.5).
- **Button (ghost)** — `--surface` + `--border` / `--muted`; hover → `--surface-2` +
  `--text`; disabled → 45%.
- **Chip (view toggle)** — off: `--surface`/`--faint`; on: `--accent-soft` fill,
  `--accent-bright`, border mixed 45% accent.
- **Step card (modifier)** — off: `--surface-2`, collapsed to one line, status dot
  `--border-strong`, number chip `--surface-3`/`--faint`; on: `--surface`, expanded,
  dot `--accent` + 3px `--accent-soft` ring, number chip `--accent`/`--accent-contrast`.
- **Table row** — hover `--row-hover`; selected `--sel` (hover: `--accent-soft`);
  changed names `--success` semibold + 5px dot indicator.
- **Tree node** — `--muted`; hover → `--text`; current → `--accent-soft` + `--text`.
- **Input/Select** — `--bg` field on `--surface` cards (the one deliberate inversion,
  light field on light card); focus ring per contract.
- **Dialog** — `--surface`, `--r-lg`, `--shadow`; confirm → primary, abort → ghost;
  warning icon/title `--danger`.

## Do's & Don'ts

Do:
- Use tokens only; two themes are the whole palette story.
- Mono for anything that is a filename or a path.
- Hierarchy by tier (`text` → `muted` → `faint`) and weight, not by color.
- Semantic color only: `--success` = name changed, `--danger` = error/warning, accent =
  interactive/selected — nothing else.

Don't:
- No gradients except the logo. No glassmorphism, no glow (the one allowed "glow" is
  the 3px focus/soft ring on status dots).
- No shadows as texture — only `--shadow`, `--shadow-btn`, focus ring.
- No off-scale sizes, no off-grid spacing, no new accent hues.
- No 1px-border-only cards; no borders in place of a background shift.
- Don't introduce a light-default reflex: dark is the default theme.