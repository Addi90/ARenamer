<script>
  import { onMount } from "svelte";
  // Aliased to avoid the `$state` rune / `state` binding name collision.
  import { state as appState } from "../lib/state/store.svelte.js";
  import * as api from "../lib/api.js";
  import TreeNode from "./TreeNode.svelte";

  // The tree is rooted at the home directory (like the original's QFileSystemModel);
  // children load lazily per expansion. `root` is a plain node: { name, path, ... }.
  let root = $state(null);

  onMount(async () => {
    try {
      const res = await api.homeDir();
      root = { name: res.path.split("/").filter(Boolean).pop() || res.path, path: res.path, expanded: true };
      const dirs = await api.listDirs(res.path);
      root.children = dirs.dirs.map((d) => ({ name: d.name, path: d.path }));
      root.loaded = true;
    } catch (e) {
      appState.error = e.message || String(e);
    }
  });
</script>

<div class="tree" aria-label="Directories">
  {#if root}
    <TreeNode node={root} depth={0} />
  {:else if appState.busy}
    <div class="placeholder">Loading…</div>
  {:else}
    <div class="placeholder">No directory tree available.</div>
  {/if}
</div>

<style>
  .tree {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #fff;
    overflow-y: auto;
    padding: 4px;
    min-height: 120px;
  }
  .placeholder { color: #9aa0ab; font-size: 0.85rem; padding: 12px; text-align: center; }
</style>
