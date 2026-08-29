<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // Bindings target the shared store's `add` config (see ReplaceModifier);
  // the card frame lives in ModifierCard.
</script>

<section class="controls">
  <label>{t("add.prefix")}
    <input class="mono" type="text" bind:value={state.config.add.prefix} placeholder={t("add.prefixPh")} />
  </label>
  <label>{t("add.suffix")}
    <input class="mono" type="text" bind:value={state.config.add.suffix} placeholder={t("add.suffixPh")} />
  </label>
  <div class="row">
    <label>{t("add.insert")}
      <input class="mono" type="text" bind:value={state.config.add.insert} placeholder={t("add.insertPh")} />
    </label>
    <label class="pos">{t("common.pos")}
      <input type="number" min="0" bind:value={state.config.add.insert_pos} />
    </label>
  </div>
</section>