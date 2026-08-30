<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // Bindings target the shared store's `counting` config (see ReplaceModifier);
  // the card frame lives in ModifierCard.
</script>

<fieldset class="controls" disabled={!state.config.counting.enabled}>
  <div class="row">
    <select bind:value={state.config.counting.position}>
      <option value="prefix">{t("position.prefix")}</option>
      <option value="suffix">{t("position.suffix")}</option>
      <option value="insert">{t("position.insert")}</option>
    </select>
    <label title={t("counting.startTitle")}>{t("counting.start")}
      <input type="number" min="1" bind:value={state.config.counting.start} />
    </label>
    <label title={t("counting.padTitle")}>{t("counting.pad")}
      <input type="number" min="0" bind:value={state.config.counting.padding} />
    </label>
  </div>
  {#if state.config.counting.position === "insert"}
    <label class="pos">{t("counting.insertAt")}
      <input type="number" min="0" bind:value={state.config.counting.insert_pos} />
    </label>
  {/if}
</fieldset>