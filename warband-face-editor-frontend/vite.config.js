import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3005,
    open: true
  },
  build: {
    outDir: 'dist'
  },
  publicDir: 'public'
});