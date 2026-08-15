<script>
  import { onMount } from "svelte";

  let health = $state("checking…");
  let error = $state("");

  onMount(async () => {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      health = `backend ok (${data.app})`;
    } catch (e) {
      error = String(e);
      health = "backend unreachable";
    }
  });
</script>

<main class="shell">
  <h1>A-Renamer Tool</h1>
  <p class="sub">Python + Svelte rebuild — scaffold (Milestone 1)</p>

  <div class="status" class:ok={!error} class:err={!!error}>
    {health}{#if error}<span> — {error}</span>{/if}
  </div>

  <p class="hint">
    The file browser, live preview and modifier panels arrive in later milestones.
  </p>
</main>

<style>
  .shell {
    max-width: 720px;
    margin: 10vh auto;
    padding: 0 24px;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: #1f2430;
  }
  h1 { margin-bottom: 4px; font-size: 2rem; }
  .sub { color: #6b7280; margin-top: 0; }
  .status {
    margin-top: 24px;
    padding: 10px 14px;
    border-radius: 8px;
    background: #f3f4f6;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
  }
  .status.ok { background: #e7f6ec; color: #14532d; }
  .status.err { background: #fdecec; color: #7f1d1d; }
  .hint { margin-top: 24px; color: #9aa0ab; font-size: 0.9rem; }
</style>
