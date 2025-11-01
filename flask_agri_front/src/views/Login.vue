<template>
  <div class="login-container">
    <el-form
      ref="formRef"
      :rules="rules"
      :model="form"
      class="login-form"
      label-width="100px"
      @submit.prevent="login"
    >
      <h2 class="form-title">天视无人机可视化平台</h2>
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="form.username"
          placeholder="请输入用户名"
          prefix-icon="User"
          clearable
        />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          prefix-icon="Lock"
          clearable
          show-password
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" class="login-btn">
          登录
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

const formRef = ref<FormInstance>()
const form = reactive({ username: '', password: '' })

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_]+$/,
      message: '用户名仅支持字母、数字和下划线',
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6-20 字符', trigger: 'blur' },
    // {
    //   pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]+$/,
    //   message: '密码必须包含字母和数字',
    //   trigger: 'blur'
    // }
  ]
})

const authStore = useAuthStore()
const router = useRouter()


const login = async () => {
  if(!formRef.value) return
  try {
    await formRef.value.validate();
    await authStore.login(form.username, form.password)
    router.push('/')
  } catch (error) {
    if (error instanceof Error && error.message.includes('validate')) {
      ElMessage.error('请填写正确的用户名和密码')
    } else {
      ElMessage.error('登录失败：' + (error.message || '请检查用户名和密码'))
    }
    console.error('登录失败:', error)
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100vw;
  height: 100vh;
  background-image: url('@/assets/images/login-bg.jpg');
  background-size: cover;
  background-position: center;
  animation: fadeIn 1s ease-in;
}

.login-form {
  width: 400px;
  padding: 30px;
  background: rgba(26, 26, 46, 0.5);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  animation: slideIn 0.5s ease-out;
}

.form-title {
  color: #fff;
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: bold;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-input {
  --el-input-bg-color: rgba(255, 255, 255, 0.1);
  --el-input-text-color: #fff;
  --el-input-border-color: #00d4ff;
  --el-input-focus-border: #00d4ff;
}

.login-btn {
  width: 100%;
  background: linear-gradient(90deg, #00d4ff, #007acc);
  border: none;
  font-size: 16px;
  transition: transform 0.3s, box-shadow 0.3s;
}

// .login-btn:hover {
//   transform: scale(1.05);
//   box-shadow: 0 0 15px rgba(0, 212, 255, 0.8);
// }

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>