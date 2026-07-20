<template>
  <div class="admin-dashboard">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/admin">Quiz Master Admin</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/subjects">Subjects</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/users">Users</router-link>
            </li>
          </ul>
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <button class="btn btn-outline-light" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AdminDashboard',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const logout = async () => {
      await authStore.logout()
      router.push('/login')
    }

    return {
      logout
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style> 