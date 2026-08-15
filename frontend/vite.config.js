import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// The built SPA is emitted into backend/static so the FastAPI app can serve it
// (and pywebview can load http://127.0.0.1:8000). In dev, /api is proxied to the
// FastAPI backend on :8000 so there are no CORS issues.
export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "../backend/static",
    emptyOutDir: true,
  },
});
