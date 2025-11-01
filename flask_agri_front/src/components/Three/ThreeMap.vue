<template>
  <div ref="threeContainer" class="three-container"></div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useThreeScene } from '@/hooks/useThreeScene'

const threeContainer = ref<HTMLElement | null>(null)

// 使用 hook 初始化 Three.js 场景并添加中国地图
useThreeScene(threeContainer, {
  particleCount: 5000,
  backgroundColor: 0x1a1a2e,
  backgroundAlpha: 0.5, // 场景背景透明度
  initialCameraZ: 100,
  minZoom: 50,
  maxZoom: 500,
  zoomSpeed: 1.0,
  rotationSpeed: 1.0,
  particleSize: 2,
  mapGeoJsonUrl: '/assets/json/china.json', // 替换为实际 GeoJSON 文件路径
  fujianGeoJsonUrl: '/assets/json/fujian.json', // 福建省市级 GeoJSON
  mapScale: 6.5, // 调整缩放比例以适合视野
})
</script>

<style scoped lang="scss">
.three-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
}
</style>