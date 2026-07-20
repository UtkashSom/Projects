<template>
  <div class="home">
    <h1>Welcome to Quiz Master</h1>
    <p>Test your knowledge with our interactive quizzes!</p>
    <div class="mt-4">
      <router-link to="/login" class="btn btn-primary me-2">Login</router-link>
      <router-link to="/register" class="btn btn-success">Register</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}
</style> 