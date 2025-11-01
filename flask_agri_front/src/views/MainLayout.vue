<template>
    <div class="main-layout">
      <!-- <cesium-viewer :ion-token="ionToken" /> -->
      <three-map />
      <top-panel :show-panel="showTopPanel" @toggle-panel="toggleTopPanel" />
      <left-panel :show-panel="showLeftPanel" @toggle-panel="toggleLeftPanel" />
      <right-panel :show-panel="showRightPanel" @toggle-panel="toggleRightPanel" />
      <bottom-panel :show-panel="showBottomPanel" @toggle-panel="toggleBottomPanel" />
      <router-view class="content-view" />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  // import CesiumViewer from '@/components/CesiumViewer.vue'
  import ThreeMap from '@/components/Three/ThreeMap.vue'
  import TopPanel from '@/components/TopPanel.vue'
  import LeftPanel from '@/components/LeftPanel.vue'
  import RightPanel from '@/components/RightPanel.vue'
  import BottomPanel from '@/components/BottomPanel.vue'
  
  const ionToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2MTVhYTQ3YS0zZjMyLTQzMjUtOTU2NS0xOTM2MmQyMjFkMDgiLCJpZCI6MzA0MjYzLCJpYXQiOjE3NTA0MDI2OTB9.KLjEo1-dVK9KRsx2Z5KMI8-fCyax6CGxdqrQQZbbaa4'
  
  const showTopPanel = ref(true)
  const showLeftPanel = ref(false)
  const showRightPanel = ref(false)
  const showBottomPanel = ref(true)
  
  const toggleTopPanel = () => { showTopPanel.value = !showTopPanel.value }
  const toggleLeftPanel = () => { showLeftPanel.value = !showLeftPanel.value }
  const toggleRightPanel = () => { showRightPanel.value = !showRightPanel.value }
  const toggleBottomPanel = () => { showBottomPanel.value = !showBottomPanel.value }
  </script>
  
  <style scoped lang="scss">
  .main-layout {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: $background-color;
  }
  
  #app {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    height: 100vh;
  }
  
  .content-view {
    position: relative;
    z-index: 2;
    margin: 80px 350px;
    height: calc(100vh - 160px);
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    overflow: auto;
  }
  </style>