import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// Under Vitest's SSR-style transform, plain exports resolution picks Svelte's
// server entry (index-server.js), so mount() throws
// "lifecycle_function_unavailable". Alias the bare "svelte" specifier to the
// client entry explicitly — the conditions approach alone did not take effect
// for the SSR transform of node_modules deps.
const svelteClientEntry = fileURLToPath(
  new URL("./node_modules/svelte/src/index-client.js", import.meta.url)
);

// Test-only config: reuses the Svelte plugin so .svelte / .svelte.js (rune)
// files compile, and runs in a lightweight DOM environment. Keep separate from
// vite.config.js so the production build (→ ../backend/static) is untouched.
export default defineConfig({
  plugins: [svelte()],
  resolve: {
    conditions: ["svelte"],
    alias: [{ find: /^svelte$/, replacement: svelteClientEntry }],
  },
  ssr: {
    noExternal: ["svelte", "@testing-library/svelte", "@testing-library/svelte-core"],
    resolve: {
      conditions: ["svelte"],
    },
  },
  test: {
    environment: "happy-dom",
    include: ["src/**/*.test.js"],
  },
});
