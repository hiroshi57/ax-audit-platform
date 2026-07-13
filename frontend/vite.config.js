import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// VITE_API でバックエンドURLを指定(既定 http://localhost:8000)
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
});
