<script>
  import { state } from "../../lib/state/store.svelte.js";
  import { t } from "../../lib/i18n/index.svelte.js";

  // Bindings target the shared store's `ifthen` config (see ReplaceModifier);
  // the card frame lives in ModifierCard.
</script>

<section class="controls">
  <div class="row">
    <span class="tag" title={t("ifthen.condTitle")}>{t("ifthen.ifTag")}</span>
    <select
      value={state.config.ifthen.contains_not ? "not" : ""}
      onchange={(e) => (state.config.ifthen.contains_not = e.target.value === "not")}>
      <option value="">{t("ifthen.contains")}</option>
      <option value="not">{t("ifthen.notContains")}</option>
    </select>
    <input class="mono" type="text" bind:value={state.config.ifthen.expression} placeholder={t("ifthen.exprPh")} />
  </div>
  <div class="row">
    <label class="check"><input type="checkbox" bind:checked={state.config.ifthen.regex} /> {t("common.regex")}</label>
    <label class="check"><input type="checkbox" bind:checked={state.config.ifthen.case_sensitive} /> {t("common.caseSensitive")}</label>
  </div>
  <div class="row">
    <span class="tag" title={t("ifthen.consTitle")}>{t("ifthen.thenTag")}</span>
    <input class="mono" type="text" bind:value={state.config.ifthen.string} placeholder={t("ifthen.stringPh")} />
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
</section>
