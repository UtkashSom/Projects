<template>
  <div class="container mt-5" style="max-width: 500px;">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h4 class="mb-0">Login</h4>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleLogin">
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" required>
          </div>
          
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required>
          </div>
          
          <button type="submit" class="btn btn-primary w-100">Login</button>
          
          <div class="text-center mt-3">
            <router-link to="/register">Don't have an account? Register</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        this.error = '';
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            email: this.email, 
            password: this.password 
          })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.msg || 'Login failed');
        }
        
     
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        if (data.user && data.user.is_admin) {
          this.$router.push('/admin');
        } else {
          this.$router.push('/user');
        }
      } catch (err) {
        console.error('Login error:', err);
        this.error = err.message || 'An error occurred during login';
      }
    }
  }
}
</script>