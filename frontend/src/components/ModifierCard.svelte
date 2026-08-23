<script>
  import { t } from "../lib/i18n/index.svelte.js";
  import { state as appState, reorderModifier } from "../lib/state/store.svelte.js";

  // Drag & drop via the grip handle: the card only becomes `draggable` while the
  // grip is pressed, so text selection in the panel's inputs keeps working.
  // `index` is the card's position in the store's `pipeline_order` (the drop
  // slot). The drop is deferred to the next frame so the browser finishes the
  // drag (dragend) before the {#each} re-renders the reordered cards.
  let { id, index } = $props();

  let cardEl;
  let dragging = $state(false);
  let over = $state(false);

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
    over = false;
  }

  function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (!over) over = true;
  }

  function onDragLeave(e) {
    if (cardEl && e.relatedTarget && cardEl.contains(e.relatedTarget)) return;
    over = false;
  }

  function onDrop(e) {
    e.preventDefault();
    over = false;
    const draggedId = e.dataTransfer.getData("text/plain");
    if (!draggedId || draggedId === id) return;
    const from = appState.config.pipeline_order.indexOf(draggedId);
    if (from < 0) return;
    requestAnimationFrame(() => reorderModifier(from, index));
  }
</script>

<div class="card" class:dragging class:over bind:this={cardEl} draggable={false}
     ondragstart={onDragStart} ondragend={endDrag} ondragover={onDragOver} ondragleave={onDragLeave} ondrop={onDrop}>
  <span class="grip" role="button" onmousedown={startDrag} title={t("modifiers.dragHint")} aria-label={t("modifiers.dragHint")}>⠿</span>
  <slot />
</div>

<style>
  .card { position: relative; border-radius: 8px; transition: opacity 0.1s ease; }
  .card.dragging { opacity: 0.4; }
  .card.over { outline: 2px dashed #2563eb; outline-offset: 2px; }
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
