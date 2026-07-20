import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import AdminDashboard from '../components/AdminDashboard.vue'
import UserDashboard from '../components/UserDashboard.vue'
import ParkingLotList from '../components/admin/ParkingLotList.vue'  // new import

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/admin', component: AdminDashboard },
  { path: '/user', component: UserDashboard },
  { path: '/admin/lots', component: ParkingLotList }  // new route
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
