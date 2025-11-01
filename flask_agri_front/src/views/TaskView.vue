<template>
    <el-container>
      <el-main>
        <el-card>
          <el-table :data="tasks" contentType="width:">
            <el-table-column prop="id" label="任务ID" />
            <el-table-column prop="description" label="任务描述" />
            <el-table-column prop="status" label="状态" />
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </template>
  
  <script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { taskApi } from '@/api/task'
  
  interface Task {
    id: string
    description: string
    status: string
  }
  
  const tasks = ref<Task[]>([])
  
  const fetchTasks = async () => {
    try {
      tasks.value = await taskApi.getTasks()
    } catch (error) {
      console.error('获取任务失败:', error)
    }
  }
  
  onMounted(fetchTasks)
  </script>
  
  <style>
    .el-main {
      background-color: $background-color;
    }
  </style>