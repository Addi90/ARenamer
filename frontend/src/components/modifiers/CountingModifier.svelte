<script>
  import { state } from "../../lib/state/store.svelte.js";

  // All bindings target the shared store's `counting` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
</script>

<section class="panel" class:active={state.config.counting.enabled}>
  <header>
    <label class="toggle">
      <input type="checkbox" bind:checked={state.config.counting.enabled} />
      Number {state.config.counting.enabled ? "✓" : "✗"}
    </label>
  </header>

  <div class="controls" class:disabled={!state.config.counting.enabled}>
    <div class="row">
      <select bind:value={state.config.counting.position}>
        <option value="prefix">Prefix</option>
        <option value="suffix">Suffix</option>
        <option value="insert">At position</option>
      </select>
      <label title="First number in the sequence (files are numbered in list order)">Start
        <input type="number" min="1" bind:value={state.config.counting.start} />
      </label>
      <label title="Zero-pad the number to this width (e.g. 3 → 001)">Pad
        <input type="number" min="0" bind:value={state.config.counting.padding} />
      </label>
    </div>
    {#if state.config.counting.position === "insert"}
      <label class="pos">Insert at position
        <input type="number" min="0" bind:value={state.config.counting.insert_pos} />
      </label>
    {/if}
  </div>
</section>

<style>
  .panel {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px 12px;
    background: #fff;
  }
  .panel.active { border-color: #93c5fd; box-shadow: 0 0 0 1px #bfdbfe inset; }
  header { margin-bottom: 8px; }
  .toggle { font-weight: 600; color: #374151; display: flex; align-items: center; gap: 8px; cursor: pointer; }
  .controls { display: flex; flex-direction: column; gap: 8px; }
  .controls.disabled { opacity: 0.45; pointer-events: none; }
  label { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #4b5563; }
  input[type="number"] { width: 72px; padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; }
  select { padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-size: 0.85rem; color: #374151; }
  .row { display: flex; gap: 12px; align-items: center; }
  .pos { flex: 0 0 auto; }
</style>
