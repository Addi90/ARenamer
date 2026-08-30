<script>
  import { t } from "../lib/i18n/index.svelte.js";
  import { state as appState, reorderModifier, defaultConfig } from "../lib/state/store.svelte.js";

  // Each modifier is a numbered *step* of the pipeline. The head (number + name
  // + enable dot) toggles the modifier on/off — the former per-panel checkbox —
  // and a disabled step folds its controls away (the prototype's behavior, and
  // what keeps the sidebar scannable with all seven steps).
  //
  // Drag & drop via the grip handle: the card only becomes `draggable` while the
  // grip is pressed, so text selection in the panel's inputs keeps working.
  // `index` is the card's position in the store's `pipeline_order`. While
  // hovering, `slot` marks the insertion gap the pointer sits in (0 = before
  // this card, 1 = after, null = not hovered) and is drawn as a line between
  // cards, so it is always clear where the card will slot in. The drop is
  // deferred to the next frame so the browser finishes the drag (dragend)
  // before the {#each} re-renders the reordered cards.
  let { id, index, children } = $props();

  let cardEl;
  let dragging = $state(false);
  let slot = $state(null); // 0 = insert before, 1 = insert after, null = idle
  let horiz = $state(false); // marker orientation (true = cards sit side by side)

  const enabled = $derived(!!appState.config[id].enabled);
  const name = $derived(t(`${id}.title`));

  function toggleEnabled() {
    appState.config[id].enabled = !enabled;
  }

  // Reset this one modifier's fields to the defaults (order stays where dragged).
  function resetModifier() {
    Object.assign(appState.config[id], defaultConfig()[id]);
  }

  function startDrag() {
    if (cardEl) cardEl.draggable = true;
  }

  function onDragStart(e) {
    dragging = true;
    e.dataTransfer.setData("text/plain", id);
    e.dataTransfer.effectAllowed = "move";
  }

  function endDrag() {
    if (cardEl) cardEl.draggable = false;
    dragging = false;
    slot = null;
  }

  // True when the card sits side by side with other cards (multiple columns
  // fit in the list), in which case the marker runs vertically along the
  // card's left/right edge. Measured via card vs. container width, because
  // the narrow-screen layout is a *grid* even when only one column (stacked
  // cards) actually fits — `display: grid` alone is not enough.
  function isHorizontal() {
    const list = cardEl?.closest(".modifiers");
    if (!list) return false;
    return cardEl.getBoundingClientRect().width < list.clientWidth * 0.9;
  }

  function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    const r = cardEl.getBoundingClientRect();
    const h = isHorizontal();
    const before = h ? e.clientX < r.left + r.width / 2 : e.clientY < r.top + r.height / 2;
    const next = before ? 0 : 1;
    if (slot !== next) slot = next;
    if (horiz !== h) horiz = h;
  }

  function onDragLeave(e) {
    if (cardEl && e.relatedTarget && cardEl.contains(e.relatedTarget)) return;
    slot = null;
  }

  function onDrop(e) {
    e.preventDefault();
    const s = slot;
    slot = null;
    if (s === null) return;
    const draggedId = e.dataTransfer.getData("text/plain");
    if (!draggedId || draggedId === id) return;
    const from = appState.config.pipeline_order.indexOf(draggedId);
    if (from < 0) return;
    const to = index + s; // insertion slot: before (index) or after (index + 1)
    requestAnimationFrame(() => reorderModifier(from, to));
  }
</script>

<div class="card" role="listitem" class:on={enabled} class:dragging class:over={slot !== null} bind:this={cardEl} draggable={false}
     ondragstart={onDragStart} ondragend={endDrag} ondragover={onDragOver} ondragleave={onDragLeave} ondrop={onDrop}>
  <span class="marker" class:before={slot === 0} class:after={slot === 1} class:vert={horiz} aria-hidden="true"></span>
  <div class="step-head" role="button" tabindex="0" aria-pressed={enabled}
       title={enabled ? t("modifiers.dragHint") : t("modifiers.reset")}
       onclick={toggleEnabled}
       onkeydown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), toggleEnabled())}>
    <span class="step-num" aria-hidden="true">{index + 1}</span>
    <span class="step-name">{name}</span>
    <span class="dot" aria-hidden="true"></span>
    <button class="reset-mini" type="button" title={t("modifiers.reset")} aria-label={t("modifiers.reset") + " " + name}
            onclick={(e) => (e.stopPropagation(), resetModifier())}>
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" width="12" height="12" aria-hidden="true">
        <path d="M3 8a5 5 0 1 1 1.6 3.7" />
        <path d="M3 11.7V8h3.7" />
      </svg>
    </button>
    <!-- Decorative (aria-hidden): dragging is a mouse-only affordance; the
         accessible controls are step-head (toggle) and reset-mini (reset).
         Keeping it focusable would add a tab stop that keyboard Enter can't use. -->
    <span class="grip" aria-hidden="true" title={t("modifiers.dragHint")}
          onmousedown={startDrag} onclick={(e) => e.stopPropagation()}>
      <svg viewBox="0 0 8 12" fill="currentColor" width="8" height="12" aria-hidden="true">
        <circle cx="2" cy="2" r="1.1" /><circle cx="6" cy="2" r="1.1" />
        <circle cx="2" cy="6" r="1.1" /><circle cx="6" cy="6" r="1.1" />
        <circle cx="2" cy="10" r="1.1" /><circle cx="6" cy="10" r="1.1" />
      </svg>
    </span>
  </div>
  <div class="step-body" class:off={!enabled}>
    {@render children()}
  </div>
</div>

<style>
  .card {
    position: relative;
    border: 1px solid var(--border);
    background: var(--surface-2);
    border-radius: var(--r-md);
    transition: border-color 0.12s ease, background 0.12s ease, opacity 0.1s ease;
  }
  .card.on {
    border-color: color-mix(in srgb, var(--accent) 45%, var(--border));
    background: var(--surface);
  }
  .card.dragging {
    opacity: 0.4;
  }

  /* Insertion line in the gap at the edge the pointer is in (before/after),
     so the hover state marks a *position* instead of a card. */
  .marker {
    display: none;
    position: absolute;
    z-index: 2;
    pointer-events: none;
    background: var(--accent);
    border-radius: 2px;
  }
  .card.over .marker {
    display: block;
  }
  .marker.before { left: -6px; right: -6px; top: -8px; height: 3px; }
  .marker.after { left: -6px; right: -6px; bottom: -8px; height: 3px; }
  .marker.vert.before { left: -8px; right: auto; top: 6px; bottom: 6px; width: 3px; height: auto; }
  .marker.vert.after { right: -8px; left: auto; top: 6px; bottom: 6px; width: 3px; height: auto; }

  .step-head {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    cursor: pointer;
    user-select: none;
  }
  .step-head:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: -2px;
  }
  .step-num {
    display: grid;
    place-items: center;
    width: 22px;
    height: 22px;
    flex: none;
    border-radius: 7px;
    background: var(--surface-3);
    color: var(--faint);
    font-size: 11px;
    font-weight: 600;
    transition: background 0.12s ease, color 0.12s ease;
  }
  .card.on .step-num {
    background: var(--accent-soft);
    color: var(--accent-bright);
  }
  .step-name {
    font-size: 13px;
    font-weight: 550;
  }
  .card.on .step-name {
    font-weight: 600;
  }
  .dot {
    margin-left: auto;
    width: 8px;
    height: 8px;
    flex: none;
    border-radius: 50%;
    border: 1.5px solid var(--border-strong);
    background: transparent;
    transition: background 0.12s ease, border-color 0.12s ease;
  }
  .card.on .dot {
    background: var(--accent);
    border-color: var(--accent);
  }
  .reset-mini {
    margin-left: 10px;
    width: 24px;
    height: 24px;
    display: grid;
    place-items: center;
    border-radius: 7px;
    border: none;
    background: none;
    color: var(--faint);
    opacity: 0;
    transition: opacity 0.12s ease, background 0.12s ease, color 0.12s ease;
  }
  .step-head:hover .reset-mini,
  .reset-mini:focus-visible {
    opacity: 1;
  }
  .reset-mini:hover {
    background: var(--surface-3);
    color: var(--text);
  }
  .reset-mini:active {
    color: var(--accent-bright);
  }
  .grip {
    width: 12px;
    height: 16px;
    display: grid;
    place-items: center;
    cursor: grab;
    color: var(--faint);
    flex: none;
  }
  .grip:hover {
    color: var(--muted);
  }
  .card.dragging .grip {
    cursor: grabbing;
    color: var(--accent-bright);
  }

  .step-body {
    padding: 2px 12px 12px 44px;
  }
  .step-body.off {
    display: none;
  }
</style>