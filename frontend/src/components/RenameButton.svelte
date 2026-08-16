<script>
  import { state, checkDuplicates, performRename, loadDir, showDialog } from "../lib/state/store.svelte.js";
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
  }
</script>

<button class="primary" disabled={disabled} onclick={onRename}>
  {state.renaming ? t("rename.renaming") : `${t("rename.button")}${state.selection.length ? ` (${state.selection.length})` : ""}`}
</button>

<style>
  button { padding: 8px 14px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
  button:hover:not(:disabled) { background: #f3f4f6; }
  button.primary { background: #2563eb; border-color: #2563eb; color: #fff; }
  button.primary:hover:not(:disabled) { background: #1d4ed8; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
