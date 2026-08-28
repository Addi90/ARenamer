<script>
  import { onMount } from "svelte";
  import FileList from "./components/FileList.svelte";
  import DirectoryTree from "./components/DirectoryTree.svelte";
  import RenameButton from "./components/RenameButton.svelte";
  import Dialog from "./components/Dialog.svelte";
  import ReplaceModifier from "./components/modifiers/ReplaceModifier.svelte";
  import CaseModifier from "./components/modifiers/CaseModifier.svelte";
  import IfThenModifier from "./components/modifiers/IfThenModifier.svelte";
  import RemoveModifier from "./components/modifiers/RemoveModifier.svelte";
  import AddModifier from "./components/modifiers/AddModifier.svelte";
  import CountingModifier from "./components/modifiers/CountingModifier.svelte";
  import DateModifier from "./components/modifiers/DateModifier.svelte";
  import ModifierCard from "./components/ModifierCard.svelte";
  import { state as appState, loadDir, openHome, goUp, clearError, refreshPreview, resetModifierOrder, defaultConfig } from "./lib/state/store.svelte.js";
  import { language, setLanguage, t, languages } from "./lib/i18n/index.svelte.js";

  // id -> panel component; the sidebar renders them in `config.pipeline_order`.
  const MODIFIERS = {
    replace: ReplaceModifier,
    case: CaseModifier,
    ifthen: IfThenModifier,
    remove: RemoveModifier,
    add: AddModifier,
    counting: CountingModifier,
    date: DateModifier,
  };

  // Draft path in the input; committed only on Open/Enter (so typing doesn't
  // re-trigger preview with a half-typed path).
  let pathInput = $state("");

  // True while the modifier order differs from the canonical default order.
  const orderChanged = $derived(
    appState.config.pipeline_order.some((id, i) => id !== defaultConfig().pipeline_order[i])
  );

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
    <div class="title">
      <img class="logo" src="/favicon.svg" alt="" aria-hidden="true" />
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
    <div class="error">
      <span class="msg">{appState.error}</span>
      <button class="dismiss" aria-label={t("app.errorDismiss")} title={t("app.errorDismiss")} onclick={clearError}>
        <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
          <circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5" />
          <path d="M5.5 5.5 L10.5 10.5 M10.5 5.5 L5.5 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
        </svg>
      </button>
    </div>
  {/if}

  <div class="main">
    <aside class="tree-pane">
      <DirectoryTree />
    </aside>
    <div class="content">
      {#snippet actions()}
        <RenameButton />
      {/snippet}
      <FileList {actions} />
    </div>
    <!-- Panels are rendered in `config.pipeline_order` (canonical default:
         Replace → Case → If-Then → Remove → Add → Counting → Date) so the
         composition order is visible to the user, and can be rearranged by
         dragging the cards. They live in a right-hand sidebar (scrollable) so
         they're always visible without page scrolling. -->
    <aside class="modifiers-pane">
      <div class="pane-head">
        <h2>{t("modifiers.title")}</h2>
        {#if orderChanged}
          <button onclick={resetModifierOrder} title={t("modifiers.resetOrder")}>{t("modifiers.resetOrder")}</button>
        {/if}
      </div>
      <p class="hint">{t("modifiers.dragHint")}</p>
      <section class="modifiers" role="list" aria-label={t("modifiers.title")}>
        {#each appState.config.pipeline_order as id, i (id)}
          {@const Comp = MODIFIERS[id]}
          <ModifierCard {id} index={i}>
            {#if Comp}<Comp />{/if}
          </ModifierCard>
        {/each}
      </section>
    </aside>
  </div>

  <Dialog />
</main>

<style>
  .shell {
    /* Full-viewport app frame: the page itself never scrolls; each pane below
       scrolls internally (native-app feel). */
    width: 100%;
    height: 100vh;
    height: 100dvh;
    margin: 0;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: #1f2430;
  }
  .head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
  .title { display: flex; align-items: baseline; gap: 10px; }
  .logo { width: 34px; height: 34px; border-radius: 8px; flex: none; }
  h1 { font-size: 1.6rem; line-height: 1.2; }
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

  .error { margin-bottom: 12px; padding: 8px 12px; border-radius: 6px; background: #fdecec; color: #7f1d1d; font-size: 0.85rem; display: flex; align-items: center; gap: 10px; }
  .error .msg { flex: 1; min-width: 0; }
  .error .dismiss { flex: none; padding: 3px; border: none; background: none; color: #7f1d1d; border-radius: 50%; cursor: pointer; display: flex; align-items: center; }
  .error .dismiss:hover { background: #f8d7d7; }

  .main { flex: 1; min-height: 0; display: flex; gap: 16px; align-items: stretch; }
  .tree-pane { flex: 0 0 240px; min-width: 0; display: flex; flex-direction: column; }
  .tree-pane :global(.tree) { flex: 1; min-height: 0; }
  .content { flex: 1; min-width: 0; display: flex; flex-direction: column; }

  .modifiers-pane {
    flex: 0 0 350px;
    min-width: 0;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  .modifiers-pane h2 { margin: 0 0 4px; font-size: 0.95rem; color: #374151; }
  .modifiers-pane .pane-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 0 0 4px; }
  .modifiers-pane .hint { margin: 0 0 8px; font-size: 0.8rem; color: #6b7280; }
  /* The padding keeps the drop markers of the first/last card (which extend
     past the card edges) inside the scroll container — `overflow-y: auto`
     would otherwise clip anything drawn above the top edge. */
  .modifiers { flex: 1; min-height: 0; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding: 10px 8px; }

  /* Narrow screens (phones / small browser windows): fall back to the stacked
     layout and let the page scroll, since three columns can't fit. */
  @media (max-width: 980px) {
    .shell { height: auto; min-height: 100vh; overflow: visible; }
    .main { flex-direction: column; align-items: stretch; }
    .tree-pane { flex: none; width: 100%; max-height: 260px; }
    .tree-pane :global(.tree) { flex: none; max-height: 240px; }
    .content { width: 100%; flex: none; }
    .modifiers-pane { flex: none; width: 100%; overflow: visible; }
    .modifiers { flex: none; overflow: visible; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(320px, 1fr), 1fr)); }
  }
</style>
