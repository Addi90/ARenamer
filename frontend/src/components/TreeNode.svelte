<script>
  import { state, loadDir } from "../lib/state/store.svelte.js";
  import * as api from "../lib/api.js";
  // Self-import for recursion (the modern replacement for `<svelte:self>`).
  import TreeNode from "./TreeNode.svelte";

  let { node, depth = 0 } = $props();

  const isCurrent = $derived(state.currentPath === node.path);

  // Lazy-load children on first expansion (mirrors the original's QFileSystemModel).
  async function loadChildren() {
    if (node.loaded || node.loading) return;
    node.loading = true;
    try {
      const res = await api.listDirs(node.path);
      node.children = res.dirs.map((d) => ({ name: d.name, path: d.path }));
      node.loaded = true;
    } catch (e) {
      state.error = e.message || String(e);
    } finally {
      node.loading = false;
    }
  }

  function onTwisty(e) {
    e.stopPropagation(); // don't also trigger the label's loadDir
    if (node.expanded) {
      node.expanded = false;
    } else {
      node.expanded = true;
      loadChildren();
    }
  }

  function onLabel() {
    loadDir(node.path); // re-roots the file list (and clears its selection)
    if (!node.expanded) {
      node.expanded = true;
      loadChildren();
    }
  }
</script>

<div class="row" style:padding-left="{depth * 14}px">
  <button class="twisty" onclick={onTwisty} aria-label={node.expanded ? "Collapse" : "Expand"}>
    {#if node.loading}…{:else if node.expanded}▾{:else if node.loaded}▸{/if}
  </button>
  <button class="label" class:current={isCurrent} title={node.path} onclick={onLabel}>{node.name}</button>
</div>

{#if node.expanded && node.children}
  {#each node.children as child (child.path)}
    <TreeNode node={child} depth={depth + 1} />
  {/each}
{/if}

<style>
  .row { display: flex; align-items: center; gap: 2px; padding-right: 8px; }
  .twisty {
    width: 18px;
    height: 20px;
    flex: 0 0 auto;
    border: none;
    background: transparent;
    cursor: pointer;
    color: #6b7280;
    font-size: 0.8rem;
    padding: 0;
  }
  .twisty:hover { color: #2563eb; }
  .label {
    flex: 1;
    min-width: 0;
    border: none;
    background: transparent;
    text-align: left;
    font-family: inherit;
    cursor: pointer;
    font-size: 0.85rem;
    color: #374151;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 2px 4px;
    border-radius: 4px;
  }
  .label:hover { background: #f3f4f6; }
  .label.current { background: #eef4ff; color: #1d4ed8; font-weight: 600; }
</style>
