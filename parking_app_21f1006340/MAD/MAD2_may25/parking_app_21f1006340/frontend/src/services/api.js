import { useAuthStore } from '@/stores/auth';

const API_BASE_URL = 'http://localhost:5000/api';

async function request(endpoint, options = {}) {
  const authStore = useAuthStore();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add auth token if available
  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    // Handle unauthorized responses
    if (response.status === 401) {
      authStore.logout();
      throw new Error('Session expired. Please log in again.');
    }

    // Handle other error responses
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'An error occurred');
    }

    // For DELETE requests that don't return content
    if (response.status === 204) {
      return;
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

export const api = {
  get: (endpoint) => request(endpoint, { method: 'GET' }),
  post: (endpoint, data) => 
    request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  put: (endpoint, data) =>
    request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (endpoint) =>
    request(endpoint, {
      method: 'DELETE',
    }),
};
