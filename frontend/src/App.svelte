<script>
  import { onMount } from "svelte";
  import FileList from "./components/FileList.svelte";
  import DirectoryTree from "./components/DirectoryTree.svelte";
  import RenameButton from "./components/RenameButton.svelte";
  import Dialog from "./components/Dialog.svelte";
  import ReplaceModifier from "./components/modifiers/ReplaceModifier.svelte";
  import IfThenModifier from "./components/modifiers/IfThenModifier.svelte";
  import RemoveModifier from "./components/modifiers/RemoveModifier.svelte";
  import AddModifier from "./components/modifiers/AddModifier.svelte";
  import CountingModifier from "./components/modifiers/CountingModifier.svelte";
  import DateModifier from "./components/modifiers/DateModifier.svelte";
  import { state as appState, loadDir, openHome, goUp, refreshPreview } from "./lib/state/store.svelte.js";
  import { language, setLanguage, t, languages } from "./lib/i18n/index.svelte.js";

  // Draft path in the input; committed only on Open/Enter (so typing doesn't
  // re-trigger preview with a half-typed path).
  let pathInput = $state("");

  function commitPath() {
    const p = pathInput.trim();
    if (p) loadDir(p);
  }

  const canGoUp = $derived(!!appState.currentPath && appState.currentPath !== "/");

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
    const timer = setTimeout(() => refreshPreview(), 150);
    return () => clearTimeout(timer);
  });

  // Keep <html lang> in sync (accessibility / screen readers).
  $effect(() => {
    document.documentElement.lang = language.current; // eslint-disable-line no-unused-expressions
  });

  onMount(() => {
    openHome(); // start in the home directory so there's something to work with
  });
</script>

<main class="shell">
  <header class="head">
    <div>
      <h1>{t("app.title")}</h1>
      <p class="sub">{t("app.subtitle")}</p>
    </div>
    <label class="lang">
      {t("lang.label")}
      <select value={language.current} onchange={(e) => setLanguage(e.target.value)}>
        {#each languages as l (l.code)}
          <option value={l.code}>{l.label}</option>
        {/each}
      </select>
    </label>
  </header>

  <div class="pathbar">
    <button onclick={openHome} title={t("app.homeTitle")}>{t("app.home")}</button>
    <button disabled={!canGoUp} onclick={goUp} title={t("app.upTitle")}>{t("app.up")}</button>
    <input type="text" class="path" bind:value={pathInput} placeholder="/path/to/directory" onkeydown={(e) => e.key === "Enter" && commitPath()} />
    <button class="primary" onclick={commitPath}>{t("app.open")}</button>
  </div>

  {#if appState.error}
    <div class="error">{appState.error}</div>
  {/if}

  <div class="main">
    <aside class="tree-pane">
      <DirectoryTree />
    </aside>
    <div class="content">
      <FileList>
        <RenameButton slot="actions" />
      </FileList>

      <!-- Panels are rendered in pipeline order (Replace → If-Then → Remove → Add →
           Counting → Date) so the composition order is visible to the user. -->
      <section class="modifiers">
        <ReplaceModifier />
        <IfThenModifier />
        <RemoveModifier />
        <AddModifier />
        <CountingModifier />
        <DateModifier />
      </section>
    </div>
  </div>

  <Dialog />
</main>

<style>
  .shell {
    max-width: 1100px;
    margin: 24px auto;
    padding: 0 20px;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: #1f2430;
  }
  .head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
  h1 { margin-bottom: 2px; font-size: 1.6rem; }
  .sub { color: #6b7280; margin-top: 0; font-size: 0.9rem; }
  .lang { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #4b5563; }
  .lang select { padding: 6px 8px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-size: 0.9rem; color: #1f2430; }

  .pathbar { display: flex; gap: 8px; margin: 16px 0; }
  .pathbar input.path { flex: 1; padding: 8px 10px; border: 1px solid #d1d5db; border-radius: 6px; font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  button { padding: 8px 14px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
  button:hover:not(:disabled) { background: #f3f4f6; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  button.primary { background: #2563eb; border-color: #2563eb; color: #fff; }
  button.primary:hover:not(:disabled) { background: #1d4ed8; }

  .error { margin-bottom: 12px; padding: 8px 12px; border-radius: 6px; background: #fdecec; color: #7f1d1d; font-size: 0.85rem; }

  .main { display: flex; gap: 16px; align-items: flex-start; }
  .tree-pane { flex: 0 0 30%; max-width: 320px; }
  .tree-pane :global(.tree) { max-height: calc(100vh - 260px); min-height: 240px; }
  .content { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 16px; }

  .modifiers { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(320px, 100%), 1fr)); gap: 12px; }
</style>
