// M1 sanity test: proves the vitest toolchain compiles our modules (config.js
// is plain JS; later milestones add real coverage here and elsewhere).
import { describe, it, expect } from "vitest";
import { defaultConfig, PIPELINE_ORDER } from "./config.js";

describe("defaultConfig", () => {
  it("returns an object with a top-level key per modifier", () => {
    const cfg = defaultConfig();
    for (const id of PIPELINE_ORDER) {
      expect(cfg[id]).toBeTypeOf("object");
    }
  });

  it("defaults every modifier to disabled", () => {
    const cfg = defaultConfig();
    for (const id of PIPELINE_ORDER) {
      expect(cfg[id].enabled).toBe(false);
    }
  });
});
