import { defineConfig } from "vitest/config";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// Test-only config: reuses the Svelte plugin so .svelte / .svelte.js (rune)
// files compile, and runs in a lightweight DOM environment. Keep separate from
// vite.config.js so the production build (→ ../backend/static) is untouched.
export default defineConfig({
  plugins: [svelte()],
  test: {
    environment: "happy-dom",
    include: ["src/**/*.test.js"],
  },
});
