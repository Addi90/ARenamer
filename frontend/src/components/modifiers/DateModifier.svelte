<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // All bindings target the shared store's `date` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
</script>

<section class="panel" class:active={state.config.date.enabled}>
  <header>
    <label class="toggle">
      <input type="checkbox" bind:checked={state.config.date.enabled} />
      {t("date.title")} {state.config.date.enabled ? "✓" : "✗"}
    </label>
  </header>

  <div class="controls" class:disabled={!state.config.date.enabled}>
    <div class="row">
      <!-- Format options are codes (DD-MM-YYYY …), identical in both languages. -->
      <select bind:value={state.config.date.format}>
        <option value="dmy">DD-MM-YYYY</option>
        <option value="ymd">YYYY-MM-DD</option>
        <option value="mdy">MM-DD-YYYY</option>
      </select>
      <label class="sep" title={t("date.sepTitle")}>{t("date.separator")}
        <input type="text" bind:value={state.config.date.separator} />
      </label>
    </div>
    <div class="row">
      <select bind:value={state.config.date.source}>
        <option value="created">{t("date.created")}</option>
        <option value="modified">{t("date.modified")}</option>
        <option value="today">{t("date.today")}</option>
        <option value="custom">{t("date.custom")}</option>
      </select>
      {#if state.config.date.source === "custom"}
        <input type="date" bind:value={state.config.date.custom_date} />
      {/if}
    </div>
    <div class="row">
      <select bind:value={state.config.date.position}>
        <option value="prefix">{t("position.prefix")}</option>
        <option value="suffix">{t("position.suffix")}</option>
        <option value="insert">{t("position.insert")}</option>
      </select>
      {#if state.config.date.position === "insert"}
        <label class="pos">{t("common.pos")}
          <input type="number" min="0" bind:value={state.config.date.insert_pos} />
        </label>
      {/if}
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
  input[type="date"] { padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; }
  select { padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-size: 0.85rem; color: #374151; }
  .row { display: flex; gap: 12px; align-items: center; }
  .sep input[type="text"] { flex: 0 1 90px; }
  .pos { flex: 0 0 auto; }
</style>
