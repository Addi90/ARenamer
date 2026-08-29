<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // Bindings target the shared store's `remove` config (see ReplaceModifier);
  // the card frame lives in ModifierCard.
</script>

<fieldset class="controls" disabled={!state.config.remove.enabled}>
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
</fieldset>

<style>
  .dimmed { opacity: 0.45; }
</style>