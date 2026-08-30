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
    background: var(--scrim);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }
  .box {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    border-radius: var(--r-lg);
    padding: 20px 24px;
    min-width: 320px;
    max-width: 480px;
    box-shadow: var(--shadow);
  }
  h2 { margin: 0 0 8px; font-size: 15px; font-weight: 650; color: var(--text); display: flex; align-items: center; gap: 8px; }
  h2.warning { color: var(--danger); }
  .icon { font-size: 15px; }
  .msg { margin: 0 0 18px; color: var(--muted); font-size: 13px; white-space: pre-line; }
  .buttons { display: flex; justify-content: flex-end; gap: 8px; }
  button {
    padding: 7px 16px;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--text);
    border-radius: var(--r-md);
    cursor: pointer;
    font-size: 13px;
    transition: background 0.12s ease, border-color 0.12s ease;
  }
  button:hover { background: var(--surface-3); border-color: var(--border-strong); }
  button:active { transform: translateY(1px); }
  button.primary {
    background: var(--primary);
    border-color: var(--primary);
    color: var(--primary-contrast);
    font-weight: 600;
    box-shadow: var(--shadow-btn);
  }
  button.primary:hover { background: var(--primary-hover); border-color: var(--primary-hover); }
</style>