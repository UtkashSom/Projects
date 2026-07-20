<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div class="container">
        <router-link class="navbar-brand" to="/">MAD 2 Vehicle Parking App</router-link>
        
        <button 
          class="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
          aria-controls="navbarNav" 
          aria-expanded="false" 
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item" v-if="!isAuthenticated">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item" v-if="!isAuthenticated">
              <router-link class="nav-link" to="/register">Register</router-link>
            </li>
            
            <li class="nav-item" v-if="isAuthenticated">
              <button 
                @click="handleLogout" 
                class="btn btn-outline-light"
              >
                Logout
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    
    <div class="container">
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('token');
    }
  },
  methods: {
    handleLogout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
}
</script>

<style>
body {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.navbar {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.navbar-brand {
  font-weight: bold;
}

.nav-link {
  padding: 0.5rem 1rem;
  margin: 0 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.btn-outline-light {
  border-color: rgba(255,255,255,0.5);
  margin-left: 0.5rem;
}

.btn-outline-light:hover {
  background-color: rgba(255,255,255,0.1);
}

@media (max-width: 991.98px) {
  .navbar-nav {
    padding: 1rem 0;
  }
  
  .nav-item {
    margin: 0.25rem 0;
  }
  
  .btn-outline-light {
    margin-left: 0;
    width: 100%;
    text-align: left;
    padding: 0.5rem 1rem;
  }
}
</style>