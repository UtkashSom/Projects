import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/Login.vue';
import Register from '../components/Register.vue';
import AdminDashboard from '../components/AdminDashboard.vue';
import UserDashboard from '../components/UserDashboard.vue';
import LotDetails from '../components/LotDetails.vue'; 
import AdminAnalytics from '../components/AdminAnalytics.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { 
    path: '/admin', 
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/lots/:id',       
    component: LotDetails,
    meta: { requiresAuth: true, role: 'admin' }
  },
  { 
    path: '/user', 
    component: UserDashboard,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  if (requiresAuth && !token) {
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/admin'); 
  } else {
    next();
  }
});

export default router;
