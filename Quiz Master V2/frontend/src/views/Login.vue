<template>
  <div class="login">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin" class="mt-4">
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" class="form-control" id="email" v-model="email" required>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model="password" required>
      </div>
      <button type="submit" class="btn btn-primary">Login</button>
    </form>
    <p class="mt-3">
      Don't have an account? <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        const authStore = useAuthStore()
        await authStore.login(this.email, this.password)
        
        if (authStore.isAdmin) {
          this.$router.push('/admin')
        } else {
          this.$router.push('/')
        }
      } catch (error) {
        console.error('Login failed:', error)
        alert('Login failed. Please check your credentials.')
      }
    }
  }
}
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}
</style> 