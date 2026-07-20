import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { jwtDecode } from 'jwt-decode';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null);
  const user = ref(null);

  if (token.value) {
    try {
      const decoded = jwtDecode(token.value);
      user.value = {
        id: decoded.id,
        email: decoded.email || decoded.username,
        role: decoded.role || 'user'
      };
    } catch (e) {
      console.error('Invalid token:', e);
      logout();
    }
  }

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isUser = computed(() => user.value?.role === 'user');

  function setToken(newToken) {
    token.value = newToken;
    localStorage.setItem('access_token', newToken);
    
    try {
      const decoded = jwtDecode(newToken);
      user.value = {
        id: decoded.id,
        email: decoded.email || decoded.username,
        role: decoded.role || 'user'
      };
    } catch (e) {
      console.error('Invalid token:', e);
      logout();
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    isUser,
    setToken,
    logout
  };
});
