import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Code splitting
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'query-vendor': ['@tanstack/react-query'],
          'animation': ['framer-motion'],
          'icons': ['lucide-react'],
          'utils': ['axios'],
        },
      },
    },
    // Optimizations (use esbuild default minifier)
    minify: 'esbuild',
    sourcemap: false,
    cssCodeSplit: true,
    chunkSizeWarningLimit: 500,
  },
  // Development optimizations
  server: {
    middlewareMode: false,
    hmr: true,
  },
})
