<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // All bindings target the shared store's `add` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
</script>

<section class="panel" class:active={state.config.add.enabled}>
  <header>
    <label class="toggle">
      <input type="checkbox" bind:checked={state.config.add.enabled} />
      {t("add.title")} {state.config.add.enabled ? "✓" : "✗"}
    </label>
  </header>

  <div class="controls" class:disabled={!state.config.add.enabled}>
    <label>{t("add.prefix")}
      <input type="text" bind:value={state.config.add.prefix} placeholder={t("add.prefixPh")} />
    </label>
    <label>{t("add.suffix")}
      <input type="text" bind:value={state.config.add.suffix} placeholder={t("add.suffixPh")} />
    </label>
    <div class="row">
      <label>{t("add.insert")}
        <input type="text" bind:value={state.config.add.insert} placeholder={t("add.insertPh")} />
      </label>
      <label class="pos">{t("common.pos")}
        <input type="number" min="0" bind:value={state.config.add.insert_pos} />
      </label>
    </div>
  </div>
</section>

<style>
  .panel {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px 12px;
    background: #fff;
  }
  .panel.active { border-color: #93c5fd; box-shadow: 0 0 0 1px #bfdbfe inset; }
  header { margin-bottom: 8px; }
  .toggle { font-weight: 600; color: #374151; display: flex; align-items: center; gap: 8px; cursor: pointer; }
  .controls { display: flex; flex-direction: column; gap: 8px; }
  .controls.disabled { opacity: 0.45; pointer-events: none; }
  label { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #4b5563; }
  input[type="text"] { flex: 1; padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  input[type="number"] { width: 72px; padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; }
  .row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .pos { flex: 0 0 auto; }
</style>
