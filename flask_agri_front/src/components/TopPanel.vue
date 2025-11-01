<template>
  <div class="top-panel" :class="{ hidden: !showPanel }">
    <dv-border-box-1 class="border-box">
      <dv-decoration-1 class="decoration" />
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
    </dv-border-box-1>
    <el-button class="toggle-btn top" circle @click="togglePanel">
      <el-icon><ArrowDown v-if="showPanel" /><ArrowUp v-else /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowUp, User, Setting } from '@element-plus/icons-vue'

defineProps<{
  showPanel: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle-panel'): void
}>()

const togglePanel = () => emit('toggle-panel')

const currentDate = computed(() => new Date().toLocaleDateString('zh-CN'))
const currentDay = computed(() => {
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return days[new Date().getDay()]
})

const authStore = useAuthStore()
const username = computed(() => authStore.username || '管理员')
const router = useRouter()

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
</script>

<style scoped lang="scss">
.top-panel {
  position: absolute;
  z-index: 2;
  transition: transform 0.3s ease;
  top: 0;
  left: 0;
  width: 100%;
  height: 90px;
  &.hidden {
    transform: translateY(-90px);
  }
}

.border-box {
  height: 100%;
  // padding: 10px;
  background: rgba(26, 26, 46, 0.8);
}

.decoration {
  height: 8px;
  margin-bottom: 5px;
}

.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.title {
  color: $primary-color;
  font-size: 26px;
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
  font-size: 16px;
}

.toggle-btn {
  position: absolute;
  z-index: 3;
  background: linear-gradient(90deg, #00d4ff, #007acc);
  border: none;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
}
</style>