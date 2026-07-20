<template>
  <div class="container mt-5">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label class="form-label">Name</label>
        <input v-model="name" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" v-model="email" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Password</label>
        <input type="password" v-model="password" class="form-control" required />
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <button type="submit" class="btn btn-primary">Register</button>
    </form>

    <p class="mt-3">
      Already have an account?
      <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async register() {
      this.error = ''
      try {
        const r = await fetch('http://localhost:5000/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.name,
            email: this.email,
            password: this.password
          })
        })

        const d = await r.json()

        if (!r.ok) throw new Error(d.msg || 'Registration failed')

        this.$router.push('/login?registered=true')
      } catch (e) {
        this.error = e.message
      }
    }
  }
}
</script>
