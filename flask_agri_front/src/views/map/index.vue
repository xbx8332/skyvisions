<template>
    <div class="main-layout">
      <!-- <language-switcher /> -->
        <cesium-map 
        :ion-token="ionToken"
        :initial-view="initalView"
        :viewer-options="viewerOptions"
        />
    </div>
</template>
<script setup lang="ts">
// import Languageswitcher from '@/components/Common/LanguageSwitcher.vue'
import CesiumMap from './components/CesiumMap.vue'

const ionToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2MTVhYTQ3YS0zZjMyLTQzMjUtOTU2NS0xOTM2MmQyMjFkMDgiLCJpZCI6MzA0MjYzLCJpYXQiOjE3NTA0MDI2OTB9.KLjEo1-dVK9KRsx2Z5KMI8-fCyax6CGxdqrQQZbbaa4'
const  initalView = { 
  longitude: 119.30, // 福 HD 福州市经度,
  latitude: 26.08,  // 福州市纬度
  height: 10000 
}
const viewerOptions = {
  animation: false, 
  timeline: false
}
</script>
<style lang="scss">
 .main-layout {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: $background-color;
  }
</style>