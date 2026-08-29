<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // Bindings target the shared store's `date` config (see ReplaceModifier);
  // the card frame lives in ModifierCard.
</script>

<section class="controls">
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
    <label class="sep" title={t("date.nameSepTitle")}>{t("date.nameSeparator")}
      <input type="text" bind:value={state.config.date.name_separator} />
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
</section>

<style>
  .sep input[type="text"] { flex: 0 1 90px; width: auto; }
</style>