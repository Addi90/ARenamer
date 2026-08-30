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
    <!-- Independent view chips: each type shows/hides on its own. -->
    <div class="chips">
      <button class="chip" class:on={state.showFiles} type="button" aria-pressed={state.showFiles}
              aria-label={t("fileList.toggleFiles")} onclick={() => setShowFiles(!state.showFiles)}>
        {t("fileList.toggleFiles")}
      </button>
      <button class="chip" class:on={state.showDirs} type="button" aria-pressed={state.showDirs}
              aria-label={t("fileList.toggleDirs")} onclick={() => setShowDirs(!state.showDirs)}>
        {t("fileList.toggleDirs")}
      </button>
    </div>
    <span class="spacer"></span>
    <button class="ghost" type="button" onclick={selectAll}>{t("fileList.selectAll")}</button>
    <button class="ghost" type="button" disabled={state.selection.length === 0} onclick={clearSelection}>{t("fileList.clear")}</button>
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
          <th class="col-arrow" aria-hidden="true"></th>
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
            <td class="col-arrow" aria-hidden="true">→</td>
            <td class="col-new" class:changed={prev?.changed} title={prev ? prev.full_new_name : file.name}>
              {prev ? prev.full_new_name : file.name}{duplicate ? " ⚠" : ""}
            </td>
          </tr>
        {/each}
        {#if visible.length === 0}
          <tr class="empty">
            <td colspan="4">{state.busy ? t("common.loading") : t("fileList.empty")}</td>
          </tr>
        {/if}
      </tbody>
    </table>
  </div>
</div>

<style>
  /* Fills the center pane of App's three-pane layout; the table scrolls inside. */
  .filelist { display: flex; flex-direction: column; min-height: 0; height: 100%; }

  .toolbar {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    flex: none;
  }
  .chips { display: flex; gap: 6px; }
  .chip {
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-size: 12px;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 999px;
    cursor: pointer;
    transition: background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
  }
  .chip:hover {
    background: var(--surface-2);
    border-color: var(--border-strong);
    color: var(--text);
  }
  .chip:active {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
  .chip.on {
    background: var(--accent-soft);
    border-color: color-mix(in srgb, var(--accent) 45%, var(--border));
    color: var(--accent-bright);
    font-weight: 600;
  }
  .ghost {
    border: 1px solid var(--border);
    background: transparent;
    color: var(--muted);
    font-size: 12.5px;
    font-weight: 500;
    padding: 6px 12px;
    border-radius: var(--r-md);
    cursor: pointer;
    transition: background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
  }
  .ghost:hover:not(:disabled) {
    background: var(--surface-2);
    border-color: var(--border-strong);
    color: var(--text);
  }
  .ghost:active:not(:disabled) { transform: translateY(1px); }
  .spacer { flex: 1; }

  .table-wrap { flex: 1; min-height: 0; overflow: auto; }
  .table-wrap.empty { min-height: 0; }
  .files {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 13px;
  }
  thead th {
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--faint);
    background: var(--surface-2);
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
  }
  tbody td {
    padding: 7px 12px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr { cursor: pointer; }
  tbody tr:hover { background: var(--row-hover); }
  tr.selected { background: var(--sel); }
  tr.selected:hover { background: color-mix(in srgb, var(--sel), var(--row-hover)); }
  tr.duplicate td { background: color-mix(in srgb, var(--danger) 4%, transparent); color: var(--danger); }
  tr.duplicate:hover td { background: color-mix(in srgb, var(--danger) 12%, transparent); }

  /* No side padding: an 18px checkbox must not overflow the 34px cell —
     overflowing inline content triggers a stray "…" from the cell's
     text-overflow: ellipsis. */
  .col-check { width: 34px; text-align: center; padding-left: 0; padding-right: 0; }
  .col-arrow { width: 20px; text-align: center; color: var(--faint); }
  .badge {
    display: inline-block; margin-right: 6px; padding: 0 6px;
    font-size: 10.5px; line-height: 17px; border-radius: 999px;
    background: var(--accent-soft); color: var(--accent-bright);
    border: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);
  }
  .col-name { font-family: var(--mono); color: var(--text); }
  .col-new { font-family: var(--mono); color: var(--muted); }
  .col-new.changed { color: var(--success); font-weight: 600; }
  /* Changed names carry a small dot ahead of the new name. */
  .col-new.changed::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--success);
    margin-right: 7px;
    vertical-align: 1px;
  }

  tr.empty td {
    text-align: center;
    color: var(--faint);
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