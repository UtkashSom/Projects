import { createRouter, createWebHistory } from 'vue-router'
import Home from './components/Home.vue'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import UserDashboard from './components/UserDashboard.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/user', name: 'UserDashboard', component: UserDashboard }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
