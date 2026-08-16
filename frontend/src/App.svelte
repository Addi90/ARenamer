<script>
  import { onMount } from "svelte";
  import FileList from "./components/FileList.svelte";
  import AddModifier from "./components/modifiers/AddModifier.svelte";
  import { state as appState, loadDir, openHome, refreshPreview } from "./lib/state/store.svelte.js";

  // Draft path in the input; committed only on Open/Enter (so typing doesn't
  // re-trigger preview with a half-typed path).
  let pathInput = $state("");

  function commitPath() {
    const p = pathInput.trim();
    if (p) loadDir(p);
  }

  // Keep the input in sync when a directory is loaded.
  $effect(() => {
    pathInput = appState.currentPath;
  });

  // Live preview: recompute (debounced) whenever the config, selection, or
  // directory changes. JSON.stringify deep-tracks every config field; joining the
  // selection tracks it; currentPath tracks directory changes.
  $effect(() => {
    const cfgFingerprint = JSON.stringify(appState.config); // eslint-disable-line no-unused-expressions
    const selKey = appState.selection.join("\u0000"); // eslint-disable-line no-unused-expressions
    const path = appState.currentPath;

    if (!path || appState.selection.length === 0) {
      appState.previews = {};
      return;
    }
    const t = setTimeout(() => refreshPreview(), 150);
    return () => clearTimeout(t);
  });

  onMount(() => {
    openHome(); // start in the home directory so there's something to work with
  });
</script>

<main class="shell">
  <h1>A-Renamer Tool</h1>
  <p class="sub">Select files, configure modifiers, preview the new names, then rename.</p>

  <div class="pathbar">
    <button onclick={openHome} title="Open the home directory">Home</button>
    <input type="text" class="path" bind:value={pathInput} placeholder="/path/to/directory" onkeydown={(e) => e.key === "Enter" && commitPath()} />
    <button class="primary" onclick={commitPath}>Open</button>
  </div>

  {#if state.error}
    <div class="error">{state.error}</div>
  {/if}

  <FileList />

  <section class="modifiers">
    <AddModifier />
  </section>
</main>

<style>
  .shell {
    max-width: 900px;
    margin: 24px auto;
    padding: 0 20px;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: #1f2430;
  }
  h1 { margin-bottom: 2px; font-size: 1.6rem; }
  .sub { color: #6b7280; margin-top: 0; font-size: 0.9rem; }

  .pathbar { display: flex; gap: 8px; margin: 16px 0; }
  .pathbar input.path { flex: 1; padding: 8px 10px; border: 1px solid #d1d5db; border-radius: 6px; font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  button { padding: 8px 14px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
  button:hover { background: #f3f4f6; }
  button.primary { background: #2563eb; border-color: #2563eb; color: #fff; }
  button.primary:hover { background: #1d4ed8; }

  .error { margin-bottom: 12px; padding: 8px 12px; border-radius: 6px; background: #fdecec; color: #7f1d1d; font-size: 0.85rem; }

  .modifiers { margin-top: 16px; display: flex; flex-direction: column; gap: 12px; }
</style>
