import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
})

// Add request interceptor for error handling
api.interceptors.request.use(
  config => {
    console.log('Making request to:', config.url)
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
api.interceptors.response.use(
  response => {
    console.log('Response received:', response.data)
    return response
  },
  error => {
    console.error('Response error:', error)
    if (error.code === 'ERR_NETWORK') {
      throw new Error('Cannot connect to server. Please make sure the backend server is running.')
    }
    return Promise.reject(error)
  }
)

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || '{}'),
    token: localStorage.getItem('token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user.is_admin || false
  },

  actions: {
    async login(email, password) {
      try {
        const response = await api.post('/auth/login', {
          email,
          password
        })
        
        this.token = response.data.access_token
        this.user = response.data.user
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return response.data
      } catch (error) {
        console.error('Login failed:', error)
        if (error.response?.data?.msg) {
          throw new Error(error.response.data.msg)
        }
        throw error
      }
    },

    async register(userData) {
      try {
        console.log('Sending registration data:', userData)
        const response = await api.post('/auth/register', userData)
        console.log('Registration response:', response.data)
        return response.data
      } catch (error) {
        console.error('Registration failed:', error)
        if (error.response?.data?.msg) {
          throw new Error(error.response.data.msg)
        }
        throw error
      }
    },

    logout() {
      this.token = null
      this.user = {}
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
}) 