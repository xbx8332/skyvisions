import axios from 'axios'
import  type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

interface RequestConfig extends AxiosRequestConfig {
  skipError?: boolean
}

const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL as string,
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
})

instance.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.accessToken && !config.headers?.Authorization) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  async (response: AxiosResponse) => {
    // 直接返回 refresh 接口的响应（无 ApiResponse 包装）
    if (response.config.url?.endsWith('/api/auth/refresh')) {
      return response
    }
    // 其他接口按 ApiResponse 处理
    const { code, message, data } = response.data as ApiResponse
    console.log('code>>>>>>>', response)
    if (code === 200) {
      return data
    }
    if (!response.config.skipError) {
      ElMessage.error(message || '请求失败')
    }
    // return Promise.reject(new Error(message))
  },
  async (error) => {
    const config = error.config as RequestConfig
    const authStore = useAuthStore()
    const router = useRouter()

    if (error.response?.status === 401 && !config.skipError) {
      try {
        const data = await authApi.refresh(authStore.refreshToken)
        authStore.accessToken = data.access_token
        localStorage.setItem('access_token', authStore.accessToken)
        config.headers = config.headers || {}
        config.headers.Authorization = `Bearer ${authStore.accessToken}`
        
        return instance(config)
      } catch (refreshError) {
        authStore.logout()
        router.push('/login')
        ElMessage.error('请重新登录')
        return Promise.reject(refreshError)
      }
    } else {
      if (!config.skipError) {
        ElMessage.error(error.message || '网络错误')
      }
      return Promise.reject(error)
    }
  }
)

const request = {
  get<T = any>(url: string, config: RequestConfig = {}): Promise<T> {
    return instance.get(url, config)
  },
  post<T = any>(url: string, data?: any, config: RequestConfig = {}): Promise<T> {
    return instance.post(url, data, config)
  },
  put<T = any>(url: string, data?: any, config: RequestConfig = {}): Promise<T> {
    return instance.put(url, data, config)
  },
  delete<T = any>(url: string, config: RequestConfig = {}): Promise<T> {
    return instance.delete(url, config)
  },
}

export default request