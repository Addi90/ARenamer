<script>
  import { state } from "../../lib/state/store.svelte.js";

  // All bindings target the shared store's `ifthen` config directly, so edits are
  // reactive and immediately picked up by the live-preview effect in App.svelte.
</script>

<section class="panel" class:active={state.config.ifthen.enabled}>
  <header>
    <label class="toggle">
      <input type="checkbox" bind:checked={state.config.ifthen.enabled} />
      If-Then {state.config.ifthen.enabled ? "✓" : "✗"}
    </label>
  </header>

  <div class="controls" class:disabled={!state.config.ifthen.enabled}>
    <div class="row">
      <span class="tag" title="Condition — tested against the original name">If</span>
      <select
        value={state.config.ifthen.contains_not ? "not" : ""}
        onchange={(e) => (state.config.ifthen.contains_not = e.target.value === "not")}>
        <option value="">Contains</option>
        <option value="not">Does not contain</option>
      </select>
      <input type="text" bind:value={state.config.ifthen.expression} placeholder="e.g. report" />
    </div>
    <div class="row">
      <label class="check"><input type="checkbox" bind:checked={state.config.ifthen.regex} /> Regex</label>
      <label class="check"><input type="checkbox" bind:checked={state.config.ifthen.case_sensitive} /> Case sensitive</label>
    </div>
    <div class="row">
      <span class="tag" title="Consequence — applied when the condition matches">Then</span>
      <input type="text" bind:value={state.config.ifthen.string} placeholder="e.g. [archived]" />
      <select bind:value={state.config.ifthen.action}>
        <option value="prefix">as prefix</option>
        <option value="insert">at position</option>
        <option value="suffix">as suffix</option>
      </select>
      {#if state.config.ifthen.action === "insert"}
        <label class="pos">Pos.
          <input type="number" min="0" bind:value={state.config.ifthen.insert_pos} />
        </label>
      {/if}
    </div>
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
  input[type="text"] { flex: 1; padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  input[type="number"] { width: 72px; padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; }
  select { padding: 5px 8px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; font-size: 0.85rem; color: #374151; }
  .row { display: flex; gap: 12px; align-items: center; }
  .check { cursor: pointer; }
  .tag { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.04em; }
  .pos { flex: 0 0 auto; }
</style>
