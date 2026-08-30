<script>
  // Aliased (as in DirectoryTree.svelte): with a `state` binding in scope, Svelte 5
  // would parse `$state` as the legacy store auto-subscription (`state.subscribe`),
  // not the `$state` rune.
  import { state as appState, loadDir } from "../lib/state/store.svelte.js";
  import * as api from "../lib/api.js";
  import { t } from "../lib/i18n/index.svelte.js";
  // Self-import for recursion (the modern replacement for `<svelte:self>`).
  import TreeNode from "./TreeNode.svelte";

  let { node, depth = 0 } = $props();

  const isCurrent = $derived(appState.currentPath === node.path);

  // Keep the current directory visible when the tree re-roots / expands to it.
  // A plain `let` (not `$state`): DOM-element bindings don't need reactivity, and
  // writing `$state` here would collide with the legacy store syntax (see above).
  let rowEl = null;
  $effect(() => {
    if (isCurrent && rowEl) rowEl.scrollIntoView({ block: "nearest" });
  });

  // Lazy-load children on first expansion (mirrors the original's QFileSystemModel).
  async function loadChildren() {
    if (node.loaded || node.loading) return;
    node.loading = true;
    try {
      const res = await api.listDirs(node.path);
      node.children = res.dirs.map((d) => ({ name: d.name, path: d.path }));
      node.loaded = true;
    } catch (e) {
      appState.error = e.message || String(e);
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

<div class="row" bind:this={rowEl} style:padding-left="{depth * 14}px">
  <button class="twisty" onclick={onTwisty} aria-label={node.expanded ? t("tree.collapse") : t("tree.expand")}>
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
  .row { display: flex; align-items: center; gap: 4px; padding: 2px 6px; border-radius: var(--r-sm); }
  .row:hover { background: var(--row-hover); }
  .twisty {
    width: 18px;
    height: 20px;
    flex: 0 0 auto;
    border: none;
    background: transparent;
    cursor: pointer;
    color: var(--faint);
    font-size: 11px;
    padding: 0;
  }
  .twisty:hover { color: var(--accent-bright); }
  .label {
    flex: 1;
    min-width: 0;
    border: none;
    background: transparent;
    text-align: left;
    font-family: inherit;
    cursor: pointer;
    font-size: 13px;
    color: var(--muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 3px 6px;
    border-radius: 6px;
    transition: background 0.1s ease, color 0.1s ease;
  }
  .label:hover { color: var(--text); }
  .label.current { background: var(--accent-soft); color: var(--text); font-weight: 600; }
  .label.current:hover { background: var(--accent-soft); }
</style>
