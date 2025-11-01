import { createRouter, createWebHistory } from 'vue-router';

// import Dashboard from '../views/Dashboard.vue'
import MapView from '../views/map/index.vue'
import VideoView from '../views/VideoView.vue'
import TaskView from '../views/TaskView.vue'
import Login from '../views/Login.vue'
import MainLayout from "../views/MainLayout.vue";

const routes = [
    { path: '/', component: MainLayout, meta: { requiresAuth: true } },
    { path: '/map', component: MapView, meta: { requiresAuth: true } },
    { path: '/video', component: VideoView, meta: { requiresAuth: true } },
    { path: '/tasks', component: TaskView, meta: { requiresAuth: true } },
    { path: '/login', component: Login },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to, from ,next) => {
    const isAuthenticated = !!localStorage.getItem('access_token');

    if(to.meta.requiresAuth&& !isAuthenticated) {
        next('/login')
    } else {
        next()
    }

})

export default router;