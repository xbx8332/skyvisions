<template>
  <div class="main-layout">
    <!-- Cesium 背景 -->
    <div ref="cesiumContainer" id="cesiumContainer" class="cesium-bg"></div>

    <!-- 顶部栏 -->
    <div class="top-panel" :class="{ hidden: !showTopPanel }">
      <el-button class="toggle-btn top" circle @click="toggleTopPanel">
        <el-icon><ArrowUp v-if="showTopPanel" /><ArrowDown v-else /></el-icon>
      </el-button>
      <div class="top-content">
        <h1 class="title">天视无人机可视化平台</h1>
        <div class="widgets">
          <span class="date">{{ currentDate }} {{ currentDay }}</span>
          <span class="weather">晴 25°C</span>
          <el-dropdown trigger="click">
            <el-button type="text" class="user-menu">
              <el-icon><User /></el-icon>
              {{ username }}
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button type="text" class="settings">
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 左侧栏 -->
    <div class="left-panel" :class="{ hidden: !showLeftPanel }">
      <el-button class="toggle-btn left" circle @click="toggleLeftPanel">
        <el-icon><ArrowLeft  v-if="showLeftPanel" /><ArrowRight v-else /></el-icon>
      </el-button>
      <div class="panel-content">
        <h3>ECharts 图表</h3>
        <div id="left-chart" class="chart-placeholder"></div>
      </div>
    </div>

    <!-- 右侧栏 -->
    <div class="right-panel" :class="{ hidden: !showRightPanel }">
      <el-button class="toggle-btn right" circle @click="toggleRightPanel">
        <el-icon><ArrowRight  v-if="showRightPanel" /><ArrowLeft v-else /></el-icon>
      </el-button>
      <div class="panel-content">
        <h3>ECharts 图表</h3>
        <div id="right-chart" class="chart-placeholder"></div>
      </div>
    </div>

    <!-- 底部栏 -->
    <div class="bottom-panel" :class="{ hidden: !showBottomPanel }">
      <el-button class="toggle-btn bottom" circle @click="toggleBottomPanel">
        <el-icon><ArrowDown v-if="showBottomPanel" /><ArrowUp  v-else /></el-icon>
      </el-button>
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

    <!-- 路由视图 -->
    <router-view class="content-view" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import {
  ArrowDown,
  ArrowUp,
  ArrowLeft,
  ArrowRight,
  User,
  Setting,
  Monitor,
  MapLocation,
  List
} from '@element-plus/icons-vue'
import * as Cesium from 'cesium'
// import 'cesium/Build/Cesium/Widgets/widgets.css'

// Cesium Ion 令牌
Cesium.Ion.defaultAccessToken =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2MTVhYTQ3YS0zZjMyLTQzMjUtOTU2NS0xOTM2MmQyMjFkMDgiLCJpZCI6MzA0MjYzLCJpYXQiOjE3NTA0MDI2OTB9.KLjEo1-dVK9KRsx2Z5KMI8-fCyax6CGxdqrQQZbbaa4'

// 面板显示状态
const showTopPanel = ref(true)
const showLeftPanel = ref(true)
const showRightPanel = ref(true)
const showBottomPanel = ref(true)

// 切换面板
const toggleTopPanel = () => {
  showTopPanel.value = !showTopPanel.value
}
const toggleLeftPanel = () => {
  showLeftPanel.value = !showLeftPanel.value
}
const toggleRightPanel = () => {
  showRightPanel.value = !showRightPanel.value
}
const toggleBottomPanel = () => {
  showBottomPanel.value = !showBottomPanel.value
}

// 日期和星期
const currentDate = computed(() => new Date().toLocaleDateString('zh-CN'))
const currentDay = computed(() => {
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return days[new Date().getDay()]
})

// 用户信息
const authStore = useAuthStore()
const username = ref('管理员') // 需从 authStore 获取

// 注销
const router = useRouter()
const route = useRoute()
const logout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  } catch (error) {
    console.error('注销失败:', error)
    ElMessage.error('注销失败')
  }
}

// Cesium 容器引用
const cesiumContainer = ref<HTMLElement | null>(null)
let viewer: Cesium.Viewer

// 初始化 Cesium
onMounted(async () => {
  try {
    // 等待 DOM 渲染
    await nextTick()

    // 验证容器
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

    // 使用 Cesium Ion 默认影像（无需显式 imageryProvider）
    viewer.scene.globe.enableLighting = true

    // 设置初始视角（北京）
    viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(116.39, 39.9, 10000)
    })

    // 渲染错误处理
    viewer.scene.renderError.addEventListener((scene, error) => {
      console.error('Cesium 渲染错误:', error)
      ElMessage.error('地球渲染失败: ' + error.message)
    })

    // 验证地形加载
    console.log('地形加载成功:', terrainProvider.ready)
  } catch (error) {
    console.error('Cesium 初始化失败:', error)
    ElMessage.error('无法初始化地球: ' + (error.message || '未知错误'))
  }
})
</script>

<style scoped lang="scss">
.main-layout {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

#app {
  max-width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  height: 100vh;
}

.cesium-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.top-panel,
.left-panel,
.right-panel,
.bottom-panel {
  position: absolute;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  z-index: 2;
  transition: transform 0.3s ease;
}

.top-panel {
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  &.hidden {
    transform: translateY(-60px);
  }
}

.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title {
  color: #fff;
  font-size: 24px;
  font-weight: bold;
}

.widgets {
  display: flex;
  align-items: center;
  gap: 20px;
  color: #fff;
}

.date,
.weather {
  font-size: 14px;
}

.user-menu,
.settings {
  color: #fff;
}

.left-panel {
  top: 60px;
  left: 0;
  width: 300px;
  height: calc(100vh - 120px);
  background-image: url('@/assets/images/sidebar-bg/hud-frame.png');
  background-size: cover;
  background-position: center;
  &.hidden {
    transform: translateX(-300px);
  }
}

.right-panel {
  top: 60px;
  right: 0;
  width: 300px;
  height: calc(100vh - 120px);
  background-image: url('@/assets/images/sidebar-bg/hud-frame.png');
  background-size: cover;
  background-position: center;
  &.hidden {
    transform: translateX(300px);
  }
}

.panel-content {
  padding: 20px;
  color: #fff;
}

.chart-placeholder {
  width: 100%;
  height: 200px;
  background: rgba(0, 0, 0, 0.5);
}

.bottom-panel {
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  &.hidden {
    transform: translateY(60px);
  }
}

.bottom-menu {
  background: transparent;
  border: none;
  flex-grow: 1;
  :deep(.el-menu-item) {
    color: #fff;
    &.is-active {
      background: rgba(0, 212, 255, 0.2);
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
  &.top {
    bottom: -20px;
    left: 50%;
    transform: translateX(-50%);
  }
  &.left {
    right: -20px;
    top: 50%;
    transform: translateY(-50%);
  }
  &.right {
    left: -20px;
    top: 50%;
    transform: translateY(-50%);
  }
  &.bottom {
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
  }
}

.content-view {
  position: relative;
  z-index: 2;
  margin: 60px 300px;
  height: calc(100vh - 120px);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: auto;
}
</style>