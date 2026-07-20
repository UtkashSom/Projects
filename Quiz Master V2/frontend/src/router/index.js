import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/admin',
      component: () => import('../views/admin/Dashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          redirect: { name: 'admin-subjects' }
        },
        {
          path: 'subjects',
          name: 'admin-subjects',
          component: () => import('../views/admin/Subjects.vue')
        },
        {
          path: 'subjects/:subjectId/chapters',
          name: 'admin-chapters',
          component: () => import('../views/admin/Chapters.vue')
        },
        {
          path: 'chapters/:chapterId/quizzes',
          name: 'admin-quizzes',
          component: () => import('../views/admin/Quizzes.vue')
        },
        {
          path: 'quizzes/:quizId/questions',
          name: 'admin-questions',
          component: () => import('../views/admin/Questions.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/Users.vue')
        }
      ]
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'login' })
  } else if (to.meta.requiresAdmin && !user.is_admin) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router 