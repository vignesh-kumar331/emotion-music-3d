import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/emotion-music-3d/' : '/',
  server: { proxy: { '/api': 'http://127.0.0.1:8001' } }
})
