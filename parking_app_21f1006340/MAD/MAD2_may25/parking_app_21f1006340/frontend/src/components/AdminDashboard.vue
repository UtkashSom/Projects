<template>
  <div class="container mt-5">
    <h2>Admin Dashboard</h2>
    <p>Manage lots, view users, monitor parking spots.</p>

    <ul class="nav nav-tabs mb-3" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{ active: activeTab === 'lots' }" @click="activeTab = 'lots'" type="button">Parking Lots</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'" type="button">Users</button>
      </li>
    </ul>

    <div v-if="activeTab === 'lots'">
      <ParkingLotList />
    </div>

    <div v-if="activeTab === 'users'">
      <h4>Registered Users</h4>
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>Email</th>
            <th>Spot Number</th>
            <th>Lot Name</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.email }}</td>
            <td>{{ user.spot_number || '-' }}</td>
            <td>{{ user.lot_name || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import ParkingLotList from './ParkingLotList.vue'

export default {
  name: 'AdminDashboard',
  components: { ParkingLotList },
  data() {
    return {
      activeTab: 'lots',
      users: []
    }
  },
  methods: {
    async fetchUsers() {
      try {
        const users = await this.$api.get('/admin/users');
        this.users = users || [];
      } catch (err) {
        console.error('Fetch users error:', err);
        alert(err.message || 'Failed to fetch users');
      }
    }
  },
  mounted() {
    this.fetchUsers()
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'users') {
        this.fetchUsers()
      }
    }
  }
}
</script>

<style scoped>
.nav-link {
  cursor: pointer;
}
</style>
