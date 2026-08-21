<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // All bindings target the shared store's `case` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
</script>

<section class="panel" class:active={state.config.case.enabled}>
  <header>
    <label class="toggle">
      <input type="checkbox" bind:checked={state.config.case.enabled} />
      {t("case.title")} {state.config.case.enabled ? "✓" : "✗"}
    </label>
  </header>

  <div class="controls" class:disabled={!state.config.case.enabled}>
    <div class="row">
      <label>{t("case.mode")}
        <select bind:value={state.config.case.mode}>
          <option value="upper">{t("case.upper")}</option>
          <option value="lower">{t("case.lower")}</option>
          <option value="title">{t("case.titleCase")}</option>
          <option value="sentence">{t("case.sentenceCase")}</option>
        </select>
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
  select { padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-size: 0.85rem; color: #374151; }
  .row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
</style>
