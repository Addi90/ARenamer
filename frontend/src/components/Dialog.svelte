<script>
  import { state } from "../lib/state/store.svelte.js";

  // Resolves the pending promise (from `showDialog`) with the chosen button id.
  function choose(id) {
    const d = state.dialog;
    if (!d.open) return;
    d.open = false;
    d.resolve?.(id);
  }

  // Esc dismisses the dialog (resolves with its dismissId).
  $effect(() => {
    if (!state.dialog.open) return;
    function onKey(e) {
      if (e.key === "Escape") choose(state.dialog.dismissId);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const icon = $derived(state.dialog.variant === "warning" ? "⚠" : state.dialog.variant === "confirm" ? "?" : "ℹ");
</script>

{#if state.dialog.open}
  <!-- Clicking the backdrop (but not the box) dismisses. -->
  <div class="backdrop" role="presentation" onclick={(e) => e.target === e.currentTarget && choose(state.dialog.dismissId)}>
    <div class="box" role="alertdialog" aria-modal="true" tabindex="-1">
      <h2 class:warning={state.dialog.variant === "warning"}>
        <span class="icon">{icon}</span>{state.dialog.title}
      </h2>
      <p class="msg">{state.dialog.message}</p>
      <div class="buttons">
        {#each state.dialog.buttons as b (b.id)}
          <button class:primary={b.primary} onclick={() => choose(b.id)}>{b.label}</button>
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }
  .box {
    background: #fff;
    border-radius: 10px;
    padding: 20px 24px;
    min-width: 320px;
    max-width: 480px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  h2 { margin: 0 0 8px; font-size: 1.1rem; color: #1f2430; display: flex; align-items: center; gap: 8px; }
  h2.warning { color: #b45309; }
  .icon { font-size: 1.2rem; }
  .msg { margin: 0 0 18px; color: #4b5563; font-size: 0.9rem; white-space: pre-line; }
  .buttons { display: flex; justify-content: flex-end; gap: 8px; }
  button { padding: 7px 16px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
  button:hover { background: #f3f4f6; }
  button.primary { background: #2563eb; border-color: #2563eb; color: #fff; }
  button.primary:hover { background: #1d4ed8; }
</style>
