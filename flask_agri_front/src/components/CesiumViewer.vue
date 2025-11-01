<template>
    <div ref="cesiumContainer" id="cesiumContainer" class="cesium-bg"></div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, nextTick } from 'vue'
  import { ElMessage } from 'element-plus'
  import * as Cesium from 'cesium'
  import 'cesium/Build/Cesium/Widgets/widgets.css'
  
  defineProps<{
    ionToken: string
  }>()
  
  const cesiumContainer = ref<HTMLElement | null>(null)
  let viewer: Cesium.Viewer
  
  onMounted(async () => {
    try {
      await nextTick()
      if (!cesiumContainer.value) {
        throw new Error('cesiumContainer 未找到')
      }
  
      // 强制容器样式
      cesiumContainer.value.style.width = '100vw'
      cesiumContainer.value.style.height = '100vh'
      cesiumContainer.value.style.position = 'absolute'
      cesiumContainer.value.style.top = '0'
      cesiumContainer.value.style.left = '0'
      cesiumContainer.value.style.zIndex = '1'
  
      // 加载地形
      const terrainProvider = await Cesium.createWorldTerrainAsync()
  
      // 初始化 Viewer
      viewer = new Cesium.Viewer(cesiumContainer.value, {
        terrainProvider,
        animation: false,
        baseLayerPicker: false,
        fullscreenButton: false,
        geocoder: false,
        homeButton: false,
        infoBox: false,
        sceneModePicker: false,
        selectionIndicator: false,
        timeline: false,
        navigationHelpButton: false,
        shouldAnimate: true
      })
  
      viewer.scene.globe.enableLighting = true
      viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(116.39, 39.9, 10000)
      })
  
      viewer.scene.renderError.addEventListener((scene, error) => {
        console.error('Cesium 渲染错误:', error)
        ElMessage.error('地球渲染失败: ' + error.message)
      })
  
      console.log('地形加载成功:', terrainProvider.ready)
    } catch (error) {
      console.error('Cesium 初始化失败:', error)
      ElMessage.error('无法初始化地球: ' + (error.message || '未知错误'))
    }
  })
  </script>
  
  <style scoped lang="scss">
  .cesium-bg {
    position:absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }
  </style>