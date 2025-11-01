<template>
  <div class="bottom-panel" :class="{ hidden: !showPanel }">
    <div class="border-box">
      <el-menu
        :default-active="$route.path"
        mode="horizontal"
        class="bottom-menu"
        router
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/map">
          <el-icon><MapLocation /></el-icon>
          <span>地图导航</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
      </el-menu>
    </div>
    <el-button class="toggle-btn bottom" circle @click="togglePanel">
      <el-icon><ArrowUp v-if="showPanel" /><ArrowDown v-else /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ArrowUp, ArrowDown, Monitor, MapLocation, List } from '@element-plus/icons-vue'

defineProps<{
  showPanel: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle-panel'): void
}>()

const togglePanel = () => emit('toggle-panel')
const route = useRoute()
</script>

<style scoped lang="scss">
.bottom-panel {
  position: absolute;
  z-index: 2;
  transition: transform 0.3s ease;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 80px;
  &.hidden {
    transform: translateY(80px);
  }
}

.border-box {
  height: 100%;
  padding: 10px;
  background: rgba(26, 26, 46, 0.8);
}

.bottom-menu {
  background: transparent;
  border: none;
  flex-grow: 1;
  :deep(.el-menu-item) {
    color: #fff;
    &.is-active {
      background: rgba(0, 212, 255, 0.2);
      color: $primary-color;
    }
    &:hover {
      background: rgba(0, 212, 255, 0.1);
    }
  }
}

.toggle-btn {
  position: absolute;
  z-index: 3;
  background: linear-gradient(90deg, #00d4ff, #007acc);
  border: none;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
}
</style>