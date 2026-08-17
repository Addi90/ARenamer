<script>
  import { state, toggleSelect, selectAll, clearSelection } from "../lib/state/store.svelte.js";
  import { t } from "../lib/i18n/index.svelte.js";

  // Optional actions slot (Svelte 5 function-prop syntax) — e.g. the Rename button.
  let { actions } = $props();

  // Header checkbox reflects the selection; clicking it selects all / clears.
  const allSelected = $derived(state.files.length > 0 && state.selection.length === state.files.length);

  function onHeaderToggle(e) {
    e.currentTarget.checked ? selectAll() : clearSelection();
  }

  // Clicking a checkbox shouldn't also fire the row's click handler (would double-toggle).
  function onCheckboxClick(e) {
    e.stopPropagation();
  }
</script>

<div class="toolbar">
  <button onclick={selectAll}>{t("fileList.selectAll")}</button>
  <button onclick={clearSelection} disabled={state.selection.length === 0}>{t("fileList.clear")}</button>
  <span class="spacer"></span>
  {@render actions?.()}
</div>

<table class="files">
  <thead>
    <tr>
      <th class="col-check">
        <input type="checkbox" aria-label={t("fileList.selectAll")} checked={allSelected} onchange={onHeaderToggle} />
      </th>
      <th class="col-name">{t("fileList.name")}</th>
      <th class="col-new">{t("fileList.newName")}</th>
    </tr>
  </thead>
  <tbody>
    {#each state.files as file (file.name)}
      {@const selected = state.selection.includes(file.name)}
      {@const prev = state.previews[file.name]}
      {@const duplicate = state.duplicateNames.includes(file.name)}
      <tr class:selected={selected} class:duplicate={duplicate} onclick={() => toggleSelect(file.name)}>
        <td class="col-check">
          <input type="checkbox" checked={selected} onclick={onCheckboxClick} onchange={() => toggleSelect(file.name)} />
        </td>
        <td class="col-name" title={file.name}>{file.name}</td>
        <td class="col-new" class:changed={prev?.changed} class:muted={!selected} title={prev ? prev.full_new_name : file.name}>
          {prev ? prev.full_new_name : file.name}{duplicate ? " ⚠" : ""}
        </td>
      </tr>
    {/each}
    {#if state.files.length === 0}
      <tr class="empty">
        <td colspan="3">{state.busy ? t("common.loading") : t("fileList.empty")}</td>
      </tr>
    {/if}
  </tbody>
</table>

<style>
  .toolbar { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
  .toolbar button { padding: 6px 12px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
  .toolbar button:hover:not(:disabled) { background: #f3f4f6; }
  .toolbar button:disabled { opacity: 0.5; cursor: not-allowed; }
  .spacer { flex: 1; }

  .files {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.9rem;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
  }
  thead th {
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 600;
    color: #374151;
    background: #f9fafb;
    padding: 8px 12px;
    border-bottom: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
  }
  tbody td {
    padding: 6px 12px;
    border-bottom: 1px solid #f1f3f5;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  tbody tr { cursor: pointer; }
  tbody tr:hover { background: #f5f8ff; }
  tr.selected { background: #eef4ff; }
  tr.selected:hover { background: #e3edff; }
  tr.duplicate td { background: #fdecec; color: #7f1d1d; }
  tr.duplicate:hover td { background: #fadbd8; }

  .col-check { width: 28px; text-align: center; }
  .col-name { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  .col-new { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  .col-new.changed { color: #15803d; font-weight: 600; }
  .col-new.muted { color: #b6bcc6; }

  tr.empty td {
    text-align: center;
    color: #9aa0ab;
    padding: 24px;
    cursor: default;
  }
</style>
