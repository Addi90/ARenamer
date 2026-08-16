<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // All bindings target the shared store's `ifthen` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
</script>

<section class="panel" class:active={state.config.ifthen.enabled}>
  <header>
    <label class="toggle">
      <input type="checkbox" bind:checked={state.config.ifthen.enabled} />
      {t("ifthen.title")} {state.config.ifthen.enabled ? "✓" : "✗"}
    </label>
  </header>

  <div class="controls" class:disabled={!state.config.ifthen.enabled}>
    <div class="row">
      <span class="tag" title={t("ifthen.condTitle")}>{t("ifthen.ifTag")}</span>
      <select
        value={state.config.ifthen.contains_not ? "not" : ""}
        onchange={(e) => (state.config.ifthen.contains_not = e.target.value === "not")}>
        <option value="">{t("ifthen.contains")}</option>
        <option value="not">{t("ifthen.notContains")}</option>
      </select>
      <input type="text" bind:value={state.config.ifthen.expression} placeholder={t("ifthen.exprPh")} />
    </div>
    <div class="row">
      <label class="check"><input type="checkbox" bind:checked={state.config.ifthen.regex} /> {t("common.regex")}</label>
      <label class="check"><input type="checkbox" bind:checked={state.config.ifthen.case_sensitive} /> {t("common.caseSensitive")}</label>
    </div>
    <div class="row">
      <span class="tag" title={t("ifthen.consTitle")}>{t("ifthen.thenTag")}</span>
      <input type="text" bind:value={state.config.ifthen.string} placeholder={t("ifthen.stringPh")} />
      <select bind:value={state.config.ifthen.action}>
        <option value="prefix">{t("ifthen.asPrefix")}</option>
        <option value="insert">{t("ifthen.atPosition")}</option>
        <option value="suffix">{t("ifthen.asSuffix")}</option>
      </select>
      {#if state.config.ifthen.action === "insert"}
        <label class="pos">{t("common.pos")}
          <input type="number" min="0" bind:value={state.config.ifthen.insert_pos} />
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
  select { padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-size: 0.85rem; color: #374151; }
  .row { display: flex; gap: 12px; align-items: center; }
  .check { cursor: pointer; }
  .tag { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; }
  .pos { flex: 0 0 auto; }
</style>
