import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import cesium from 'vite-plugin-cesium'
import { copy } from 'vite-plugin-copy'
import path from 'path'

export default defineConfig({
  base: '/skyvisions/',
  plugins: [
    vue(), 
    cesium(),
    copy({
      patterns: [
        {
          from: 'public/assets/**/*',
          to: 'assets/[name][ext]'
        },
        {
          from: 'public/models/**/*',
          to: 'models/[name][ext]'
        },
        {
          from: 'node_modules/cesium/Build/Cesium/*',
          to: 'cesium/[name][ext]'
        }
      ]
    })
  ],
  build:{
    outDir: 'dist',
    assetsDir: 'assets',
    // 确保公共目录被正确处理
    copyPublicDir: true
  },
  publicDir: 'public',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use '@/assets/styles/variables.scss' as *;
        `
      }
    }
  }
})