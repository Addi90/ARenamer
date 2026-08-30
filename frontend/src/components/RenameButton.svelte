<script>
  import { state, checkDuplicates, performRename, loadDir, showDialog, bumpTreeVersion } from "../lib/state/store.svelte.js";
  import { t } from "../lib/i18n/index.svelte.js";

  const disabled = $derived(state.selection.length === 0 || state.renaming);

  // The backend's 409 body is `{"duplicates": N, "names": [...]}`; api.js stringifies
  // non-string details into `Error.message`, so parse it back for row highlighting.
  function dupNamesFromError(e) {
    try {
      return JSON.parse(e.message).names ?? [];
    } catch {
      return [];
    }
  }

  async function onRename() {
    if (state.selection.length === 0 || state.renaming) return;

    // 1. Duplicate check — blocking warning (Abort only), then stop.
    let check;
    try {
      check = await checkDuplicates();
    } catch (e) {
      state.error = e.message || String(e);
      return;
    }
    if (check.duplicates > 0) {
      await showDialog({
        variant: "warning",
        title: t("rename.dupTitle"),
        message: t("rename.dupMsg", { n: check.duplicates }),
        buttons: [{ id: "abort", label: t("dialog.abort") }],
        dismissId: "abort",
      });
      return; // duplicateNames stays set, so the offending rows remain highlighted
    }

    // 2. Confirmation — "Rename N File(s)?" with Ok / Abort.
    const choice = await showDialog({
      variant: "confirm",
      title: t("rename.confirmTitle"),
      message: t("rename.confirmMsg", { n: state.selection.length }),
      buttons: [
        { id: "ok", label: t("dialog.ok"), primary: true },
        { id: "abort", label: t("dialog.abort") },
      ],
      dismissId: "abort",
    });
    if (choice !== "ok") return;

    // 3. Perform the renames on disk.
    let result;
    try {
      result = await performRename();
    } catch (e) {
      // 409 safety net: a duplicate appeared between the check and the rename.
      state.duplicateNames = dupNamesFromError(e);
      await showDialog({
        variant: "warning",
        title: t("rename.dupTitle"),
        message: t("rename.dupMsg", { n: state.duplicateNames.length }),
        buttons: [{ id: "abort", label: t("dialog.abort") }],
        dismissId: "abort",
      });
      return;
    }

    // 4. Success (with a note if any individual file failed).
    let message = t("rename.successMsg", { n: result.renamed });
    if (result.errors.length > 0) {
      message += `\n${t("rename.errorNote", { n: result.errors.length })}`;
    }
    await showDialog({
      variant: "info",
      title: t("rename.successTitle"),
      message,
      buttons: [{ id: "ok", label: t("dialog.ok") }],
      dismissId: "ok",
    });

    // Re-list the directory — names have changed (loadDir clears selection + duplicates).
    await loadDir(state.currentPath);
    // Let the directory tree refresh the labels of any renamed directories.
    if (result.renamed > 0) bumpTreeVersion();
  }
</script>

<button class="primary" disabled={disabled} onclick={onRename}>
  {state.renaming ? t("rename.renaming") : t("rename.button")}
  {#if !state.renaming && state.selection.length}
    <span class="pill">{state.selection.length}</span>
  {/if}
</button>

<style>
  button.primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 1px solid transparent;
    background: var(--primary);
    color: var(--primary-contrast);
    font-size: 13px;
    font-weight: 600;
    padding: 7px 14px;
    border-radius: 999px;
    cursor: pointer;
    box-shadow: var(--shadow-btn);
    transition: background 0.12s ease, transform 0.05s ease;
  }
  button.primary:hover:not(:disabled) { background: var(--primary-hover); }
  button.primary:active:not(:disabled) { transform: translateY(1px); }
  /* Selection count. Dark: near-white pill + ink (APCA 96) — accent on
     accent-contrast is only 66; light theme overrides below (77.5). */
  .pill {
    display: grid;
    place-items: center;
    min-width: 20px;
    height: 20px;
    padding: 0 6px;
    border-radius: 999px;
    background: var(--text);
    color: var(--bg);
    font-size: 11px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
  /* Light-theme pill override lives in index.css (global): an html-attribute
     ancestor in scoped CSS trips svelte's css_unused_selector check. */
</style>