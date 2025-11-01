<template>
    <el-container>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card>
              <div ref="threeContainer" class="three-container"></div>
            </el-card>
          </el-col>
          <el-col :span="16">
            <el-card>
              <el-table :data="drones" style="width: 100%">
                <el-table-column prop="id" label="ID" />
                <el-table-column prop="status" label="状态" />
                <el-table-column prop="battery" label="电池" />
                <el-table-column prop="location" label="位置" />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </template>
  
  <script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import * as THREE from 'three'
//   import { droneApi } from '@/api/drone'
  
  interface Drone {
    id: number
    status: string
    battery: string
    location: string
  }
  
  const threeContainer = ref<HTMLElement | null>(null)
  const drones = ref<Drone[]>([])
  
  const fetchDrones = async () => {
    try {
        drones.value = []
    //   drones.value = await droneApi.getDrones()
    } catch (error) {
      console.error('获取无人机数据失败:', error)
    }
  }
  
  onMounted(async () => {
    await fetchDrones()
  
    if (!threeContainer.value) return
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(
      75,
      threeContainer.value.clientWidth / 300,
      0.1,
      1000
    )
    const renderer = new THREE.WebGLRenderer()
    renderer.setSize(threeContainer.value.clientWidth, 300)
    threeContainer.value.appendChild(renderer.domElement)
  
    const geometry = new THREE.BoxGeometry(1, 1, 1)
    const material = new THREE.MeshBasicMaterial({ color: '#4caf50' })
    const cube = new THREE.Mesh(geometry, material)
    scene.add(cube)
    camera.position.z = 5
  
    const animate = () => {
      requestAnimationFrame(animate)
      cube.rotation.x += 0.01
      cube.rotation.y += 0.01
      renderer.render(scene, camera)
    }
    animate()
  })
  </script>
  
  <style scoped lang="scss">
  .three-container {
    height: 300px;
    background-color: $background-color;
  }
  </style>