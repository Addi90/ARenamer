import { describe, it, expect } from "vitest";
import { defaultConfig, sanitizeConfig, PIPELINE_ORDER } from "./config.js";

describe("defaultConfig", () => {
  it("has a top-level key per modifier and defaults every modifier to disabled", () => {
    const cfg = defaultConfig();
    for (const id of PIPELINE_ORDER) {
      expect(cfg[id]).toBeTypeOf("object");
      expect(cfg[id].enabled).toBe(false);
    }
  });

  it("ships the canonical pipeline order", () => {
    expect(defaultConfig().pipeline_order).toEqual(PIPELINE_ORDER);
  });

  it("returns a fresh object each call (no shared mutable state)", () => {
    const a = defaultConfig();
    a.add.prefix = "x";
    expect(defaultConfig().add.prefix).toBe("");
  });
});

describe("sanitizeConfig", () => {
  it("coerces null numeric fields to 0 (Svelte clears number inputs to null)", () => {
    const cfg = defaultConfig();
    cfg.add.insert_pos = null;
    cfg.ifthen.insert_pos = null;
    cfg.remove.front = null;
    cfg.remove.back = null;
    cfg.remove.range_start = null;
    cfg.remove.range_end = null;
    cfg.counting.start = null;
    cfg.counting.padding = null;
    cfg.counting.insert_pos = null;
    cfg.date.insert_pos = null;

    const safe = sanitizeConfig(cfg);
    const numbers = [
      safe.add.insert_pos,
      safe.ifthen.insert_pos,
      safe.remove.front,
      safe.remove.back,
      safe.remove.range_start,
      safe.remove.range_end,
      safe.counting.start,
      safe.counting.padding,
      safe.counting.insert_pos,
      safe.date.insert_pos,
    ];
    for (const n of numbers) {
      expect(typeof n).toBe("number");
      expect(Number.isFinite(n)).toBe(true);
    }
  });

  it("coerces string numbers and drops garbage values", () => {
    const cfg = defaultConfig();
    cfg.counting.start = "5";
    cfg.counting.padding = "not-a-number";
    const safe = sanitizeConfig(cfg);
    expect(safe.counting.start).toBe(5);
    expect(safe.counting.padding).toBe(0);
  });

  it("clamps range bounds to >= 1 and counting start/padding to >= 0", () => {
    const cfg = defaultConfig();
    cfg.remove.range_start = 0;
    cfg.remove.range_end = -3;
    cfg.counting.start = -1;
    cfg.counting.padding = -2;
    const safe = sanitizeConfig(cfg);
    expect(safe.remove.range_start).toBe(1);
    expect(safe.remove.range_end).toBe(1);
    expect(safe.counting.start).toBe(0);
    expect(safe.counting.padding).toBe(0);
  });

  it("leaves non-numeric fields and unknown keys untouched", () => {
    const cfg = defaultConfig();
    cfg.replace.search = "  spaced  ";
    cfg.replace.unknown_key = 42;
    const safe = sanitizeConfig(cfg);
    expect(safe.replace.search).toBe("  spaced  ");
    expect(safe.replace.unknown_key).toBe(42);
  });

  it("does not mutate the input config", () => {
    const cfg = defaultConfig();
    cfg.counting.start = null;
    sanitizeConfig(cfg);
    expect(cfg.counting.start).toBeNull();
  });
});
