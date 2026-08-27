<script>
  import { onMount } from "svelte";
  // Aliased to avoid the `$state` rune / `state` binding name collision.
  import { state as appState } from "../lib/state/store.svelte.js";
  import * as api from "../lib/api.js";
  import { t } from "../lib/i18n/index.svelte.js";
  import TreeNode from "./TreeNode.svelte";

  // The tree starts rooted at the home directory (like the original's QFileSystemModel);
  // children load lazily per expansion. `root` is a plain node: { name, path, ... }.
  // When the current directory moves outside the tree (Up / Open dialog), the tree
  // re-roots at the common ancestor and expands the chain to the current directory.
  let root = $state(null);

  function parts(p) {
    return p.split("/").filter(Boolean);
  }

  // Longest common directory prefix of two absolute paths (at least "/").
  function commonAncestor(a, b) {
    const pa = parts(a);
    const pb = parts(b);
    let i = 0;
    while (i < pa.length && i < pb.length && pa[i] === pb[i]) i++;
    return "/" + pa.slice(0, i).join("/");
  }

  async function loadChildren(node) {
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

  // Expand the node chain from `node` down to `target` (which must be inside node.path).
  async function ensureExpandedTo(node, target) {
    if (node.path === target) {
      node.expanded = true;
      return true;
    }
    if (!target.startsWith(node.path + "/")) return false;
    if (!node.loaded) await loadChildren(node);
    const nextName = target.slice(node.path.length + 1).split("/")[0];
    const child = (node.children || []).find((c) => c.name === nextName);
    if (!child) return false;
    node.expanded = true;
    return ensureExpandedTo(child, target);
  }

  async function syncTo(path) {
    if (!path) return;
    if (!root) {
      const res = await api.homeDir();
      root = {
        name: res.path.split("/").filter(Boolean).pop() || res.path,
        path: res.path,
        expanded: true
      };
      await loadChildren(root);
    }
    const inside = path === root.path || path.startsWith(root.path + "/");
    if (!inside) {
      const ancestor = commonAncestor(root.path, path);
      if (ancestor !== root.path) {
        root = { name: parts(ancestor).pop() || ancestor, path: ancestor, expanded: true };
        await loadChildren(root);
      }
    }
    await ensureExpandedTo(root, path);
  }

  // Serialize syncs so rapid navigation can't race (each awaits the previous).
  let pending = Promise.resolve();
  function requestSync() {
    pending = pending
      .then(() => syncTo(appState.currentPath))
      .catch((e) => {
        appState.error = e.message || String(e);
      });
  }

  onMount(requestSync);

  $effect(() => {
    appState.currentPath; // track
    requestSync();
  });

  // Re-fetch the children of every loaded node so its labels are current.
  // Walks bottom-up so a renamed directory (a child of a loaded node) is
  // refreshed even when the rename happened in a deeper directory.
  async function refreshLoaded(node) {
    if (!node) return;
    for (const child of node.children || []) {
      await refreshLoaded(child);
    }
    if (node.loaded && !node.loading) {
      node.loading = true;
      try {
        const res = await api.listDirs(node.path);
        node.children = res.dirs.map((d) => ({ name: d.name, path: d.path }));
      } catch (e) {
        appState.error = e.message || String(e);
      } finally {
        node.loading = false;
      }
    }
  }

  // The store bumps treeVersion after a successful rename — refreshed labels
  // (a renamed directory is shown under its new name in the tree).
  $effect(() => {
    appState.treeVersion; // track
    refreshLoaded(root);
  });
</script>

<div class="tree" aria-label={t("tree.directories")}>
  {#if root}
    <TreeNode node={root} depth={0} />
  {:else if appState.busy}
    <div class="placeholder">{t("common.loading")}</div>
  {:else}
    <div class="placeholder">{t("tree.empty")}</div>
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
