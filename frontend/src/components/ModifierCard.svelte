<script>
  import { t } from "../lib/i18n/index.svelte.js";
  import { state as appState, reorderModifier } from "../lib/state/store.svelte.js";

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
  let horiz = $state(false); // marker orientation (side-by-side cards on narrow screens)

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

  // True when the cards sit side by side (narrow-screen grid) and the insertion
  // marker runs vertically along the card's left/right edge.
  function isHorizontal() {
    const list = cardEl?.closest(".modifiers");
    return list ? getComputedStyle(list).display === "grid" : false;
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

<div class="card" class:dragging class:over={slot !== null} bind:this={cardEl} draggable={false}
     ondragstart={onDragStart} ondragend={endDrag} ondragover={onDragOver} ondragleave={onDragLeave} ondrop={onDrop}>
  <span class="marker" class:before={slot === 0} class:after={slot === 1} class:vert={horiz}></span>
  <span class="grip" role="button" onmousedown={startDrag} title={t("modifiers.dragHint")} aria-label={t("modifiers.dragHint")}>⠿</span>
  {@render children()}
</div>

<style>
  .card { position: relative; border-radius: 8px; transition: opacity 0.1s ease; }
  .card.dragging { opacity: 0.4; }

  /* Insertion line in the gap at the edge the pointer is in (before/after),
     so the hover state marks a *position* instead of a card. */
  .marker { display: none; position: absolute; z-index: 2; pointer-events: none; background: #2563eb; border-radius: 2px; }
  .card.over .marker { display: block; }
  .marker.before { left: -6px; right: -6px; top: -8px; height: 3px; }
  .marker.after { left: -6px; right: -6px; bottom: -8px; height: 3px; }
  .marker.vert.before { left: -8px; right: auto; top: 6px; bottom: 6px; width: 3px; height: auto; }
  .marker.vert.after { right: -8px; left: auto; top: 6px; bottom: 6px; width: 3px; height: auto; }

  .grip {
    position: absolute;
    top: 4px;
    right: 6px;
    z-index: 1;
    cursor: grab;
    user-select: none;
    color: #9ca3af;
    font-size: 1rem;
    line-height: 1;
  }
  .grip:hover { color: #4b5563; }
  .card.dragging .grip { cursor: grabbing; }
</style>
