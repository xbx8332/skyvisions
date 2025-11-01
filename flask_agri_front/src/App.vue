<template>
  <router-view />
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
</script>

<style scoped lang="scss">
#app {
  width: 100vw;
  height: 100vh;
}
</style>