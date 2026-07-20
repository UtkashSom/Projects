<template>
  <div class="register">
    <h2>Register</h2>
    <div v-if="error" class="alert alert-danger">
      {{ error }}
      <div v-if="error.includes('Cannot connect to server')" class="mt-2">
        <p>Please make sure:</p>
        <ol>
          <li>The backend server is running</li>
          <li>You're running the server with: <code>python -m flask run</code></li>
          <li>The server is running on http://localhost:5000</li>
        </ol>
      </div>
    </div>
    <form @submit.prevent="handleRegister" class="mt-4">
      <div class="mb-3">
        <label for="fullName" class="form-label">Full Name</label>
        <input type="text" class="form-control" id="fullName" v-model="fullName" required>
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" class="form-control" id="email" v-model="email" required>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model="password" required>
      </div>
      <div class="mb-3">
        <label for="qualification" class="form-label">Qualification</label>
        <input type="text" class="form-control" id="qualification" v-model="qualification" required>
      </div>
      <div class="mb-3">
        <label for="dateOfBirth" class="form-label">Date of Birth</label>
        <input type="date" class="form-control" id="dateOfBirth" v-model="dateOfBirth" required>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">
        {{ loading ? 'Registering...' : 'Register' }}
      </button>
    </form>
    <p class="mt-3">
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Register',
  data() {
    return {
      fullName: '',
      email: '',
      password: '',
      qualification: '',
      dateOfBirth: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async handleRegister() {
      this.loading = true
      this.error = null
      
      try {
        // Format date to YYYY-MM-DD
        const formattedDate = new Date(this.dateOfBirth).toISOString().split('T')[0]
        
        const authStore = useAuthStore()
        await authStore.register({
          full_name: this.fullName,
          email: this.email,
          password: this.password,
          qualification: this.qualification,
          date_of_birth: formattedDate
        })
        
        this.$router.push('/login')
      } catch (error) {
        console.error('Registration failed:', error)
        this.error = error.message || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}
</style> 