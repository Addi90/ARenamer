/**
 * Modifier-config helpers (plain JS — no runes, so importable from anywhere).
 *
 * The config object is the JSON contract with the backend: its shape MUST mirror
 * `Config.to_dict()` in `backend/engine/models.py` exactly. `Config.from_dict`
 * silently ignores unknown keys, so a mismatched field name is a silent no-op.
 */

/** A fresh, all-disabled modifier config (mirrors `Config.to_dict()`). */
export function defaultConfig() {
  return {
    add: { enabled: false, prefix: "", suffix: "", insert: "", insert_pos: 0 },
    ifthen: {
      enabled: false,
      contains_not: false, // condition mode: CONTAINS (false) / CONTAINS NOT (true)
      expression: "",
      regex: false,
      case_sensitive: false,
      action: "prefix", // "prefix" | "insert" | "suffix"
      string: "",
      insert_pos: 0,
    },
    replace: { enabled: false, search: "", replace: "", regex: false, case_sensitive: false },
    remove: { enabled: false, front: 0, back: 0, range_enabled: false, range_start: 1, range_end: 1, until_end: false },
    counting: { enabled: false, position: "prefix", start: 1, padding: 0, insert_pos: 0 },
    date: { enabled: false, format: "ymd", separator: "-", name_separator: "", source: "today", custom_date: "", position: "suffix", insert_pos: 0 },
  };
}

/**
 * Coerce a config into a safe API payload. Svelte binds `<input type="number">`
 * to `null` when the field is cleared, and the engine expects ints — a null would
 * crash `min(None, len)` inside a modifier and 500 the live preview. Every numeric
 * field is coerced to an int here (null / non-numeric -> the field's default).
 */
export function sanitizeConfig(cfg) {
  // JSON round-trip detaches the value from Svelte's reactive proxy. (A plain
  // `structuredClone` throws DataCloneError on the proxy — verified against the
  // Svelte 5 client runtime.)
  const c = JSON.parse(JSON.stringify(cfg));

  const int = (v, d = 0) => {
    const n = typeof v === "number" ? v : parseInt(v, 10);
    return Number.isFinite(n) ? n : d;
  };

  c.add.insert_pos = int(c.add?.insert_pos);
  c.ifthen.insert_pos = int(c.ifthen?.insert_pos);
  c.remove.front = int(c.remove?.front);
  c.remove.back = int(c.remove?.back);
  c.remove.range_start = Math.max(1, int(c.remove?.range_start, 1));
  c.remove.range_end = Math.max(1, int(c.remove?.range_end, 1));
  c.counting.start = Math.max(0, int(c.counting?.start, 1));
  c.counting.padding = Math.max(0, int(c.counting?.padding));
  c.counting.insert_pos = int(c.counting?.insert_pos);
  c.date.insert_pos = int(c.date?.insert_pos);

  return c;
}
