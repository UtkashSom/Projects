<template>
  <div class="users">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Users</h2>
      <div class="d-flex gap-2">
        <div class="input-group">
          <input type="text" class="form-control" placeholder="Search users..." v-model="searchQuery">
          <button class="btn btn-outline-secondary" type="button">
            <i class="bi bi-search"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead>
            <tr>
              <th>Full Name</th>
              <th>Email</th>
              <th>Qualification</th>
              <th>Date of Birth</th>
              <th>Joined On</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>{{ user.full_name }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.qualification || '-' }}</td>
              <td>{{ formatDate(user.date_of_birth) }}</td>
              <td>{{ formatDate(user.created_at) }}</td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="5" class="text-center py-4">
                <div class="text-muted">No users found</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'AdminUsers',
  setup() {
    const users = ref([])
    const searchQuery = ref('')

    const fetchUsers = async () => {
      try {
        const response = await axios.get('/api/admin/users')
        users.value = response.data
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    }

    const filteredUsers = computed(() => {
      const query = searchQuery.value.toLowerCase()
      if (!query) return users.value

      return users.value.filter(user => 
        user.full_name.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        (user.qualification && user.qualification.toLowerCase().includes(query))
      )
    })

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      fetchUsers()
    })

    return {
      users,
      searchQuery,
      filteredUsers,
      formatDate
    }
  }
}
</script>

<style scoped>
.users {
  max-width: 1200px;
  margin: 0 auto;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.table td {
  vertical-align: middle;
}

.input-group {
  width: 300px;
}
</style> 