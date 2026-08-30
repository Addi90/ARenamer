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
  import {
    state as appState, loadDir, openHome, clearError, refreshPreview,
    resetModifierOrder, defaultConfig,
  } from "./lib/state/store.svelte.js";
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

  // Theme: "dark" (default) or "light", persisted, applied to <html> before
  // paint (the inline script in index.html reads the same key to avoid a flash).
  let theme = $state(
    (typeof localStorage !== "undefined" && localStorage.getItem("arenamer.theme")) || "dark"
  );
  $effect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("arenamer.theme", theme);
  });

  // Draft path in the input; committed only on Open/Enter (so typing doesn't
  // re-trigger preview with a half-typed path).
  let pathInput = $state("");

  // True while the modifier order differs from the canonical default order.
  const orderChanged = $derived(
    appState.config.pipeline_order.some((id, i) => id !== defaultConfig().pipeline_order[i])
  );

  // Path segments for the breadcrumb bar ("" segments filtered — "/" → []).
  const pathParts = $derived((appState.currentPath || "").split("/").filter(Boolean));

  function loadCrumb(i) {
    loadDir("/" + pathParts.slice(0, i + 1).join("/"));
  }

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
  <header class="topbar">
    <div class="brand">
      <img class="logo" src="/favicon.svg" alt="" aria-hidden="true" />
      <h1>{t("app.title")}</h1>
    </div>
    <div class="top-actions">
      <label class="lang">
        {t("lang.label")}
        <select value={language.current} onchange={(e) => setLanguage(e.target.value)}>
          {#each languages as l (l.code)}
            <option value={l.code}>{l.label}</option>
          {/each}
        </select>
      </label>
      <button class="icon-btn" type="button" title={t("app.theme")} aria-label={t("app.theme")}
              onclick={() => (theme = theme === "dark" ? "light" : "dark")}>
        {#if theme === "dark"}
          <!-- sun -->
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" width="17" height="17" aria-hidden="true">
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4m11.4-11.4 1.4-1.4" />
          </svg>
        {:else}
          <!-- moon -->
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="17" height="17" aria-hidden="true">
            <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
          </svg>
        {/if}
      </button>
    </div>
  </header>

  <div class="crumbs" role="navigation" aria-label={t("crumbs.aria")}>
    <div class="crumbs-left">
      <button class="crumb home" type="button" title={t("app.homeTitle")} onclick={openHome}
              aria-current={pathParts.length === 0 ? "page" : undefined}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14" aria-hidden="true">
          <path d="M3 10.5 12 3l9 7.5" />
          <path d="M5 9.5V21h14V9.5" />
        </svg>
      </button>
      {#each pathParts as part, i (part + i)}
        <span class="sep" aria-hidden="true">/</span>
        <button class="crumb" class:current={i === pathParts.length - 1} type="button"
                aria-current={i === pathParts.length - 1 ? "page" : undefined}
                title={"/" + pathParts.slice(0, i + 1).join("/")}
                onclick={() => loadCrumb(i)}>
          {part}
        </button>
      {/each}
    </div>
    <div class="crumbs-right">
      <input type="text" class="path" bind:value={pathInput} placeholder="/path/to/directory"
             onkeydown={(e) => e.key === "Enter" && commitPath()} />
      <button class="ghost" type="button" onclick={commitPath}>{t("app.open")}</button>
    </div>
  </div>

  {#if appState.error}
    <div class="error" role="alert">
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
    <aside class="pane pane-tree">
      <div class="pane-head"><h2>{t("tree.directories")}</h2></div>
      <DirectoryTree />
    </aside>
    <section class="pane pane-center">
      {#snippet actions()}
        <RenameButton />
      {/snippet}
      <FileList {actions} />
    </section>
    <!-- Panels are rendered in `config.pipeline_order` (canonical default:
         Replace → Case → If-Then → Remove → Add → Counting → Date) so the
         composition order is visible to the user, and can be rearranged by
         dragging the cards. They live in a right-hand sidebar (scrollable) so
         they're always visible without page scrolling. -->
    <aside class="pane pane-mods">
      <div class="pane-head">
        <h2>{t("modifiers.title")}</h2>
        {#if orderChanged}
          <button class="mini" type="button" onclick={resetModifierOrder} title={t("modifiers.resetOrder")}>
            {t("modifiers.resetOrder")}
          </button>
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
  /* App frame: the page itself never scrolls (desktop); each pane scrolls
     internally. Tokens live in index.css (:root + [data-theme]). */
  .shell {
    width: 100%;
    height: 100vh;
    height: 100dvh;
    margin: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    height: 48px;
    flex: none;
    padding: 0 16px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
  }
  .brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
  .logo { width: 22px; height: 22px; border-radius: 6px; flex: none; }
  h1 { margin: 0; font-size: 15px; font-weight: 650; letter-spacing: -0.01em; }

  .top-actions { display: flex; align-items: center; gap: 8px; }
  .lang {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--faint);
  }
  .lang select {
    width: auto;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 12px;
  }
  .icon-btn {
    width: 32px;
    height: 32px;
    display: grid;
    place-items: center;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--muted);
    border-radius: var(--r-md);
    cursor: pointer;
    transition: background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
  }
  .icon-btn:hover { background: var(--surface-3); color: var(--text); }
  .icon-btn:active { transform: translateY(1px); }

  .crumbs {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    height: 40px;
    flex: none;
    padding: 0 16px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
  }
  .crumbs-left {
    display: flex;
    align-items: center;
    gap: 4px;
    min-width: 0;
    overflow: hidden;
    flex: 1;
  }
  .crumb {
    flex: none;
    display: inline-flex;
    align-items: center;
    border: none;
    background: none;
    font-size: 13px;
    color: var(--muted);
    padding: 4px 7px;
    border-radius: var(--r-sm);
    cursor: pointer;
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: background 0.1s ease, color 0.1s ease;
  }
  .crumb:hover { background: var(--surface-2); color: var(--text); }
  .crumb.current { color: var(--text); font-weight: 600; }
  .crumb.home { width: 28px; height: 28px; justify-content: center; max-width: none; }
  .sep { color: var(--faint); font-size: 12px; flex: none; }
  .crumbs-right { display: flex; align-items: center; gap: 8px; flex: none; }
  .crumbs-right .path {
    width: min(44vw, 420px);
    border-radius: 999px;
    font-size: 12.5px;
    color: var(--muted);
  }
  .crumbs-right input::placeholder { color: var(--faint); }
  .ghost {
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-size: 12.5px;
    font-weight: 500;
    padding: 6px 12px;
    border-radius: var(--r-md);
    cursor: pointer;
    transition: background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
  }
  .ghost:hover {
    background: var(--surface-2);
    border-color: var(--border-strong);
    color: var(--text);
  }
  .ghost:active { transform: translateY(1px); }

  .error {
    margin: 10px 16px 0;
    padding: 8px 12px;
    border-radius: var(--r-md);
    background: color-mix(in srgb, var(--danger) 5%, var(--surface));
    border: 1px solid color-mix(in srgb, var(--danger) 35%, var(--border));
    color: var(--text);
    font-size: 12.5px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex: none;
  }
  .error .msg { flex: 1; min-width: 0; }
  .error .dismiss {
    flex: none;
    padding: 4px;
    border: none;
    background: none;
    color: var(--muted);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
  }
  .error .dismiss:hover { color: var(--danger); }

  .main {
    flex: 1;
    min-height: 0;
    display: flex;
    gap: 12px;
    padding: 12px 16px 16px;
    align-items: stretch;
  }
  .pane {
    display: flex;
    flex-direction: column;
    min-height: 0;
    min-width: 0;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    overflow: hidden;
  }
  .pane-tree { flex: 0 0 240px; }
  .pane-center { flex: 1; }
  .pane-mods { flex: 0 0 350px; }

  .pane-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 12px 14px 0;
    flex: none;
  }
  .pane-head h2 {
    margin: 0;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--faint);
  }
  .mini {
    border: none;
    background: none;
    color: var(--muted);
    font-size: 12px;
    cursor: pointer;
    padding: 3px 8px;
    border-radius: 999px;
  }
  .mini:hover { color: var(--text); background: var(--surface-2); }
  .hint {
    margin: 2px 14px 0;
    font-size: 11.5px;
    color: var(--faint);
    flex: none;
  }
  /* The padding keeps the drop markers of the first/last card (which extend
     past the card edges) inside the scroll container — `overflow-y: auto`
     would otherwise clip anything drawn above the top edge. */
  .modifiers {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 10px 8px;
  }

  /* Narrow screens (phones / small browser windows): fall back to the stacked
     layout and let the page scroll, since three columns can't fit. */
  @media (max-width: 980px) {
    .shell { height: auto; min-height: 100vh; overflow: visible; }
    .main { flex-direction: column; align-items: stretch; }
    .pane-tree { flex: none; width: 100%; }
    .pane-center, .pane-mods { flex: none; width: 100%; }
    .modifiers { flex: none; overflow: visible; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(320px, 1fr), 1fr)); }
  }
</style>