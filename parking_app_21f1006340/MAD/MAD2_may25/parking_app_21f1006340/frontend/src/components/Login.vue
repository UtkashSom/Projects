<template>
  <div class="container mt-5">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div class="mb-3">
        <label for="email" class="form-label">Username or Email</label>
        <input type="email" v-model="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" v-model="password" class="form-control" required />
      </div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <button type="submit" class="btn btn-primary">Login</button>
    </form>
    <p class="mt-3">
      Don't have an account?
      <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script>

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async login() {
      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.email,
            password: this.password
          })
        });

        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.msg || 'Login failed');
        }

        if (!data.access_token) {
          throw new Error('No access token received');
        }

        localStorage.setItem('token', data.access_token);
        
        if (data.role === 'admin') {
          this.$router.push('/admin');
        } else {
          this.$router.push('/user');
        }
      } catch (err) {
        console.error('Login error:', err);
        this.error = err.message || 'Failed to login. Please check your credentials.';
      }
    }
  }
}
</script>
