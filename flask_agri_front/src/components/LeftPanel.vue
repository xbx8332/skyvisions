<template>
  <div class="left-panel" :class="{ hidden: !showPanel }">
    <dv-border-box-1 class="border-box">
      <dv-decoration-2 class="decoration" />
      <div class="panel-content">
        <h3>数据分析</h3>
        <div id="left-chart" class="chart-placeholder"></div>
      </div>
    </dv-border-box-1>
    <el-button class="toggle-btn left" circle @click="togglePanel">
      <el-icon><ArrowRight v-if="showPanel" /><ArrowLeft v-else /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, ArrowLeft } from '@element-plus/icons-vue'

defineProps<{
  showPanel: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle-panel'): void
}>()

const togglePanel = () => emit('toggle-panel')
</script>

<style scoped lang="scss">
.left-panel {
  position: absolute;
  z-index: 2;
  transition: transform 0.3s ease;
  top: 100px;
  left: 0;
  width: 350px;
  height: calc(100vh - 220px);
  &.hidden {
    transform: translateX(-350px);
  }
}

.border-box {
  height: 100%;
  // padding: 20px;
  background: rgba(26, 26, 46, 0.8);
}

.decoration {
  height: 10px;
  margin-bottom: 10px;
}

.panel-content {
  padding: 20px;
  color: #fff;
}

h3 {
  color: $primary-color;
  font-size: 18px;
  margin-bottom: 15px;
}

.chart-placeholder {
  width: 100%;
  height: 250px;
  background: rgba(0, 0, 0, 0.5);
}

.toggle-btn {
  position: absolute;
  z-index: 3;
  background: linear-gradient(90deg, #00d4ff, #007acc);
  border: none;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
}
</style>