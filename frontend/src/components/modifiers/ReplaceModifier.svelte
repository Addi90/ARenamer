<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // All bindings target the shared store's `replace` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
  // The card frame (number, name, enable toggle, reset, drag grip) lives in
  // ModifierCard — this panel only holds the modifier's controls.
</script>

<fieldset class="controls" disabled={!state.config.replace.enabled}>
  <label>{t("replace.search")}
    <input class="mono" type="text" bind:value={state.config.replace.search} placeholder={t("replace.searchPh")} />
  </label>
  <label>{t("replace.replaceWith")}
    <input class="mono" type="text" bind:value={state.config.replace.replace} placeholder={t("replace.replacePh")} />
  </label>
  <div class="row">
    <label class="check"><input type="checkbox" bind:checked={state.config.replace.regex} /> {t("common.regex")}</label>
    <label class="check"><input type="checkbox" bind:checked={state.config.replace.case_sensitive} /> {t("common.caseSensitive")}</label>
  </div>
</fieldset>
