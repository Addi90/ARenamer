<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // All bindings target the shared store's `remove` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
</script>

<section class="panel" class:active={state.config.remove.enabled}>
  <header>
    <label class="toggle">
      <input type="checkbox" bind:checked={state.config.remove.enabled} />
      {t("remove.title")} {state.config.remove.enabled ? "✓" : "✗"}
    </label>
  </header>

  <div class="controls" class:disabled={!state.config.remove.enabled}>
    <div class="row">
      <label title={t("remove.firstTitle")}>{t("remove.first")}
        <input type="number" min="0" bind:value={state.config.remove.front} />
      </label>
      <label title={t("remove.lastTitle")}>{t("remove.last")}
        <input type="number" min="0" bind:value={state.config.remove.back} />
      </label>
    </div>
    <div class="row" class:dimmed={!state.config.remove.range_enabled}>
      <label class="check"><input type="checkbox" bind:checked={state.config.remove.range_enabled} /> {t("remove.range")}</label>
      <label title={t("remove.fromTitle")}>{t("remove.from")}
        <input type="number" min="1" bind:value={state.config.remove.range_start} disabled={!state.config.remove.range_enabled} />
      </label>
      <label title={t("remove.toTitle")}>{t("remove.to")}
        <input type="number" min="1" bind:value={state.config.remove.range_end} disabled={!state.config.remove.range_enabled || state.config.remove.until_end} />
      </label>
      <label class="check"><input type="checkbox" bind:checked={state.config.remove.until_end} disabled={!state.config.remove.range_enabled} /> {t("remove.untilEnd")}</label>
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
  input[type="number"] { width: 72px; padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; }
  .row { display: flex; gap: 12px; align-items: center; }
  .row.dimmed { opacity: 0.45; }
  .check { cursor: pointer; }
</style>
