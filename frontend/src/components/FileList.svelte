<script>
  import {
    state, toggleSelect, selectAll, clearSelection, setShowFiles, setShowDirs,
  } from "../lib/state/store.svelte.js";
  import { t } from "../lib/i18n/index.svelte.js";

  // Optional actions slot (Svelte 5 function-prop syntax) — e.g. the Rename button.
  let { actions } = $props();

  // Entries rendered given the view toggles (default: files only). Hidden entries
  // are never selectable, so the table, header checkbox and select-all all key
  // off this derived list instead of state.files.
  const visible = $derived(state.files.filter((f) => (f.type === "dir" ? state.showDirs : state.showFiles)));

  // Header checkbox reflects the selection; clicking it selects all / clears.
  const allSelected = $derived(visible.length > 0 && state.selection.length === visible.length);

  function onHeaderToggle(e) {
    e.currentTarget.checked ? selectAll() : clearSelection();
  }

  // Clicking a checkbox shouldn't also fire the row's click handler (would double-toggle).
  function onCheckboxClick(e) {
    e.stopPropagation();
  }
</script>

<div class="filelist">
  <div class="toolbar">
    <label class="toggle">
      <input type="checkbox" checked={state.showFiles} onchange={(e) => setShowFiles(e.currentTarget.checked)} />
      {t("fileList.toggleFiles")}
    </label>
    <label class="toggle">
      <input type="checkbox" checked={state.showDirs} onchange={(e) => setShowDirs(e.currentTarget.checked)} />
      {t("fileList.toggleDirs")}
    </label>
    <span class="divider"></span>
    <button onclick={selectAll}>{t("fileList.selectAll")}</button>
    <button onclick={clearSelection} disabled={state.selection.length === 0}>{t("fileList.clear")}</button>
    <span class="spacer"></span>
    {@render actions?.()}
  </div>

  <div class="table-wrap" class:empty={visible.length === 0}>
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
        {#each visible as file (file.name)}
          {@const selected = state.selection.includes(file.name)}
          {@const prev = state.previews[file.name]}
          {@const duplicate = state.duplicateNames.includes(file.name)}
          <tr class:selected={selected} class:duplicate={duplicate} onclick={() => toggleSelect(file.name)}>
            <td class="col-check">
              <input type="checkbox" checked={selected} onclick={onCheckboxClick} onchange={() => toggleSelect(file.name)} />
            </td>
            <td class="col-name" title={file.name}>
              {#if file.type === "dir"}<span class="badge">{t("fileList.typeDir")}</span>{/if}
              {file.name}
            </td>
            <td class="col-new" class:changed={prev?.changed} class:muted={!selected} title={prev ? prev.full_new_name : file.name}>
              {prev ? prev.full_new_name : file.name}{duplicate ? " ⚠" : ""}
            </td>
          </tr>
        {/each}
        {#if visible.length === 0}
          <tr class="empty">
            <td colspan="3">{state.busy ? t("common.loading") : t("fileList.empty")}</td>
          </tr>
        {/if}
      </tbody>
    </table>
  </div>
</div>

<style>
  /* Fills the center column of App's three-pane layout; the table scrolls inside. */
  .filelist { display: flex; flex-direction: column; min-height: 0; height: 100%; }

  .toolbar { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
  .toolbar .toggle { display: flex; align-items: center; gap: 4px; font-size: 0.85rem; color: #374151; cursor: pointer; }
  .toolbar .toggle input { margin: 0; }
  .toolbar .divider { width: 1px; height: 18px; background: #e5e7eb; }
  .toolbar button { padding: 6px 12px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
  .toolbar button:hover:not(:disabled) { background: #f3f4f6; }
  .toolbar button:disabled { opacity: 0.5; cursor: not-allowed; }
  .spacer { flex: 1; }

  .table-wrap {
    flex: 1;
    min-height: 0;
    overflow: auto;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }
  .table-wrap.empty { min-height: 0; }
  .files {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.9rem;
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
  tbody tr:last-child td { border-bottom: none; }
  tbody tr { cursor: pointer; }
  tbody tr:hover { background: #f5f8ff; }
  tr.selected { background: #eef4ff; }
  tr.selected:hover { background: #e3edff; }
  tr.duplicate td { background: #fdecec; color: #7f1d1d; }
  tr.duplicate:hover td { background: #fadbd8; }

  .col-check { width: 28px; text-align: center; }
  .badge {
    display: inline-block; margin-right: 6px; padding: 0 5px;
    font-size: 0.7rem; line-height: 15px; border-radius: 8px;
    background: #eef4ff; color: #1d4ed8; border: 1px solid #c7d8fe;
  }
  .col-name { font-family: ui-monospace, "SF Mono", Menlo, monospace; white-space: nowrap; }
  .col-new { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  .col-new.changed { color: #15803d; font-weight: 600; }
  .col-new.muted { color: #b6bcc6; }

  tr.empty td {
    text-align: center;
    color: #9aa0ab;
    padding: 24px;
    cursor: default;
  }

  /* Stacked (narrow) layout: no definite parent height, so cap the table and let
     the page scroll instead. */
  @media (max-width: 980px) {
    .filelist { height: auto; }
    .table-wrap { max-height: calc(100vh - 260px); min-height: 240px; }
  }
</style>
