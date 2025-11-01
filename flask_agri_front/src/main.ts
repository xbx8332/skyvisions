import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import 'element-plus/dist/index.css'
import './assets/styles/index.scss'
import router from './router';
import { createPinia } from 'pinia';
import i18n from './i18n' // 引入 i18n 配置

import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@kjgl77/datav-vue3/dist/style.css'
import DataV from '@kjgl77/datav-vue3'


console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
console.log('VITE_ENV:', import.meta.env.VITE_ENV)

const app = createApp(App)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }
  

app.use(DataV,{ classNamePrefix: 'dv-' })
app.use(ElementPlus)
app.use(i18n) //注册 i18n
app.use(router)
app.use(createPinia())
app.mount('#app')
