/**
 * Runtime i18n (Svelte 5 runes).
 *
 * - `language.current` is a `$state` property, so every `t()` call made in a
 *   component template is reactive: switching the language re-renders all strings.
 * - Startup detection mirrors the original's `QLocale::system()`: a saved user
 *   choice (localStorage) wins, otherwise the browser locale (`navigator.language`,
 *   `de*` → German, anything else → English).
 * - Option labels in the switcher are always shown in their own language.
 */

import { en } from "./en.js";
import { de } from "./de.js";

const translations = { en, de };

export const languages = [
  { code: "en", label: "English" },
  { code: "de", label: "Deutsch" },
];

const STORAGE_KEY = "arenamer.language";

function detect() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && translations[saved]) return saved;
  } catch {
    // no localStorage available (private mode, non-browser host) — fall through
  }
  const lang = (navigator.language || "en").toLowerCase();
  return lang.startsWith("de") ? "de" : "en";
}

export const language = $state({ current: detect() });

/** Switch the UI language at runtime and remember the choice for next launch. */
export function setLanguage(code) {
  if (!translations[code] || code === language.current) return;
  language.current = code;
  try {
    localStorage.setItem(STORAGE_KEY, code);
  } catch {
    // ignore — the switch still applies for this session
  }
}

/** Translate a key, interpolating `{var}` placeholders. Falls back to English, then the raw key. */
export function t(key, vars = {}) {
  let str = translations[language.current]?.[key] ?? en[key] ?? key;
  for (const [name, value] of Object.entries(vars)) {
    str = str.split(`{${name}}`).join(String(value));
  }
  return str;
}
