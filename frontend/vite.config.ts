import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // The @thesysai/genui-sdk package.json "exports" map does not expose its
      // CSS file, causing Vite to throw a "Missing specifier" error. This alias
      // bypasses the exports map and points directly to the physical file.
      '@thesysai/genui-sdk/dist/genui-sdk.css': path.resolve(
        __dirname,
        'node_modules/@thesysai/genui-sdk/dist/genui-sdk.css'
      ),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8888',
        changeOrigin: true
      }
    }
  }
})
