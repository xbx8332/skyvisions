import { createI18n } from 'vue-i18n'

const messages = {
  en: {
    loading: 'Loading globe...',
    error: {
      containerNotFound: 'Container not found',
      ionTokenMissing: 'Ion token not provided',
      ionTokenInvalid: 'Invalid ion token: {message}',
      initializationFailed: 'Failed to initialize globe: {message}',
      renderError: 'Globe rendering failed: {message}',
      modelLoadFailed: 'Failed to load drone model: {message}',
      unknown: 'Unknown error'
    }
  },
  zh: {
    loading: '正在加载地球...',
    error: {
      containerNotFound: '容器未找到',
      ionTokenMissing: 'ionToken 未提供',
      ionTokenInvalid: 'ionToken 无效: {message}',
      initializationFailed: '无法初始化地球: {message}',
      renderError: '地球渲染失败: {message}',
      modelLoadFailed: '无人机模型加载失败: {message}',
      unknown: '未知错误'
    }
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'en',
  messages
})

export default i18n