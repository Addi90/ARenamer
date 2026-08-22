# Plan: Case modifier (upper / lower / title / sentence)

## Design

New **Case** modifier with one mode dropdown, applied to the base name only
(extension is preserved and re-appended, like every other modifier):

| Mode | Behavior |
|------|----------|
| `upper` | `str.upper()` |
| `lower` | `str.lower()` |
| `title` | `str.title()` (document the apostrophe quirk: `it's` → `It'S`) |
| `sentence` | `str.capitalize()` (first char upper, rest lower) |

(Alternating case was considered and dropped to keep the panel minimal.)

## Pipeline position

Insert Case **right after Replace**:

```
Replace → Case → If-Then → Remove → Add → Counting → Date
```

Rationale: case is a text *transformation* like Replace, so it belongs with the
text-editing group. Content inserted later (Add prefix/suffix, numbers, dates,
If-Then consequences) keeps its own casing — the least surprising behavior.
Placing Case last would re-case inserted text, which is surprising. If-Then is
unaffected either way (its condition tests the original base name).

The old order is a locked contract (`tests/test_engine.py` `TestPipelineOrder`),
so the order change ships with updated tests.

## Changes

### Backend
1. `backend/engine/case.py` (new) — `modify(files, cfg)` switching on `cfg.mode`.
2. `backend/engine/models.py` — `CaseConfig(enabled=False, mode="upper")`; add
   `case` field to `Config` (from_dict/to_dict iterate dataclass fields
   generically — verify it picks the new field up automatically).
3. `backend/engine/pipeline.py` — import + apply after Replace; update the
   order docstring.
4. `backend/engine/__init__.py` — export `CaseConfig`.
5. `tests/test_engine.py` — new `TestCase` class (all 4 modes, no-op when
   disabled, extension untouched) + extend `TestPipelineOrder` (case between
   replace and ifthen; update `test_full_sequence`).

### Frontend
6. `frontend/src/lib/config.js` — `case: { enabled: false, mode: "upper" }` in
   `defaultConfig()` (no numeric fields → no `sanitizeConfig` change).
7. `frontend/src/components/modifiers/CaseModifier.svelte` (new) — same panel
   shape as the others: enable toggle + ✓/✗ indicator, one `<select>`,
   controls greyed out when disabled.
8. `frontend/src/App.svelte` — import + render after `<ReplaceModifier />`,
   update the pipeline-order comment.
9. `frontend/src/lib/i18n/en.js` + `de.js` — `case.title`, `case.mode`, mode
   labels (identical key set in both languages).

### Layout

No layout change needed. The right sidebar (`.modifiers-pane` → `.modifiers`)
already scrolls internally (`overflow-y: auto`), so a 7th panel just extends
the scroll. The Case panel is the smallest possible shape (toggle + one
select), adding ~60px. If the list gets genuinely unwieldy later, the fix is
collapsible panels — that belongs in milestone 8 (polish), not now.

### Docs
10. `README.md` — pipeline order line + modifier description.
11. `AGENTS.md` — §2 pipeline order, §3 checklist (six → seven modifiers),
    §4 behavior decision (position + title-case quirk).

## Verification

- `python3 -m pytest tests/ -v`
- `cd frontend && npm run build`
