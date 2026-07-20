<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/">Vehicle Parking</router-link>
        <div>
          <router-link class="btn btn-outline-light me-2" to="/login">Login</router-link>
          <router-link class="btn btn-outline-light" to="/register">Register</router-link>
        </div>
      </div>
    </nav>
  </template>
  
  <script>
  export default {
    name: 'Navbar'
  }
  </script>
  