<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // Bindings target the shared store's `case` config (see ReplaceModifier);
  // the card frame lives in ModifierCard.
</script>

<section class="controls">
  <div class="row">
    <label>{t("case.mode")}
      <select bind:value={state.config.case.mode}>
        <option value="upper">{t("case.upper")}</option>
        <option value="lower">{t("case.lower")}</option>
        <option value="title">{t("case.titleCase")}</option>
        <option value="sentence">{t("case.sentenceCase")}</option>
        <option value="camel">{t("case.camel")}</option>
        <option value="pascal">{t("case.pascal")}</option>
        <option value="snake">{t("case.snake")}</option>
        <option value="kebab">{t("case.kebab")}</option>
        <option value="constant">{t("case.constant")}</option>
        <option value="train">{t("case.train")}</option>
      </select>
    </label>
  </div>
</section>
