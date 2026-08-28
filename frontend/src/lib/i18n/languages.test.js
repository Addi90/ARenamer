import { describe, it, expect, beforeEach, vi } from "vitest";
import { en } from "./en.js";
import { de } from "./de.js";

// The en/de key-set contract is load-bearing: a missing key silently falls back
// to English (or the raw key) in t(), so a typo or forgotten translation would
// never crash — only look wrong.
describe("i18n table parity", () => {
  it("en and de have identical key sets", () => {
    expect(Object.keys(de).sort()).toEqual(Object.keys(en).sort());
  });

  it("every value is a non-empty string", () => {
    for (const [code, table] of Object.entries({ en, de })) {
      for (const [key, value] of Object.entries(table)) {
        expect(value, `${code}[${key}]`).toBeTypeOf("string");
        expect(value.trim().length, `${code}[${key}]`).toBeGreaterThan(0);
      }
    }
  });
});

describe("language detection and t()", () => {
  // `language.current` is module-level $state, so every test gets a fresh
  // module via vi.resetModules(). The i18n module's localStorage access is
  // try/catch-wrapped; a minimal in-memory shim (happy-dom's global may be
  // absent here) is all we need.
  const storage = {
    map: new Map(),
    getItem: (k) => storage.map.get(k) ?? null,
    setItem: (k, v) => storage.map.set(k, String(v)),
    removeItem: (k) => storage.map.delete(k),
    clear: () => storage.map.clear(),
  };

  // Detect() runs at module init, so tests set storage state BEFORE calling
  // loadI18n(); the fresh baseline is established in beforeEach instead.
  const loadI18n = async () => {
    vi.resetModules();
    globalThis.localStorage = storage;
    return import("./index.svelte.js");
  };

  beforeEach(() => {
    Object.defineProperty(navigator, "language", { value: "en-US", configurable: true });
    globalThis.localStorage = storage;
    storage.clear();
  });

  it("prefers a saved user choice over the browser locale", async () => {
    storage.setItem("arenamer.language", "de");
    const i18n = await loadI18n();
    expect(i18n.language.current).toBe("de");
  });

  it("falls back to the browser locale (de* → German, else English)", async () => {
    Object.defineProperty(navigator, "language", { value: "de-DE", configurable: true });
    const i18n = await loadI18n();
    expect(i18n.language.current).toBe("de");

    Object.defineProperty(navigator, "language", { value: "en-GB", configurable: true });
    const fresh = await loadI18n();
    expect(fresh.language.current).toBe("en");
  });

  it("translates in the current language", async () => {
    const i18n = await loadI18n();
    // Pick a key whose translation actually differs, so the assertion is
    // meaningful (e.g. "app.title" is identical in both languages).
    const key = Object.keys(en).find((k) => en[k] !== de[k]);
    expect(key, "en/de tables share at least one differing string").toBeTruthy();
    i18n.setLanguage("de");
    expect(i18n.t(key)).toBe(de[key]);
    i18n.setLanguage("en");
    expect(i18n.t(key)).toBe(en[key]);
  });

  it("interpolates {var} placeholders", async () => {
    const i18n = await loadI18n();
    // Unknown keys fall back to the raw key, so any {var} in the key itself
    // still gets substituted — a stable way to exercise the interpolation loop.
    expect(i18n.t("rename.{n} files", { n: 5 })).toBe("rename.5 files");
  });

  it("falls back to the raw key for unknown keys", async () => {
    const i18n = await loadI18n();
    expect(i18n.t("no.such.key")).toBe("no.such.key");
  });

  it("setLanguage persists the choice and ignores unknown codes", async () => {
    const i18n = await loadI18n();
    i18n.setLanguage("de");
    expect(i18n.language.current).toBe("de");
    expect(storage.getItem("arenamer.language")).toBe("de");

    i18n.setLanguage("bogus");
    expect(i18n.language.current).toBe("de");
  });
});
