<template>
  <div class="container mt-4">
    <h2>Admin Dashboard</h2>
    
    <ul class="nav nav-tabs mt-4">
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'lots' }"
          @click="activeTab = 'lots'"
        >
          Parking Lots
        </button>
      </li>
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'users' }"
          @click="activeTab = 'users'"
        >
          Users
        </button>
      </li>
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          Parking History
        </button>
      </li>
      <li class="nav-item">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'analytics' }"
          @click="activeTab = 'analytics'"
        >
          Analytics
        </button>
      </li>
    </ul>

    <div v-if="activeTab === 'lots'" class="mt-3">
      <div class="d-flex justify-content-between mb-3">
        <h4>Parking Lots</h4>
        <button class="btn btn-primary" @click="openAddModal">Add New Lot</button>
      </div>

      <div class="mb-3">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Search lots..." 
          v-model="searchQuery"
          @input="fetchLots"
        >
      </div>

      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Name</th>
              <th>Location</th>
              <th>Price</th>
              <th>Capacity</th>
              <th>Available</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lot in lots" :key="lot.id">
              <td>{{ lot.name }}</td>
              <td>{{ lot.location }}</td>
              <td>AED {{ lot.price }}/hr</td>
              <td>{{ lot.maximum_number_of_spots }}</td>
              <td>{{ lot.available_spots || 0 }}</td>
              <td>
                <button 
                  class="btn btn-sm btn-outline-primary me-2"
                  @click="$router.push(`/admin/lots/${lot.id}`)"
                >
                  View Spots
                </button>
                <button 
                  class="btn btn-sm btn-outline-secondary me-2"
                  @click="openEditModal(lot)"
                >
                  Edit
                </button>
                <button 
                  class="btn btn-sm btn-danger" 
                  @click="deleteLot(lot.id)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav v-if="pageCount > 1">
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="changePage(currentPage - 1)">Previous</button>
          </li>
          <li 
            v-for="page in pageCount" 
            :key="page" 
            class="page-item" 
            :class="{ active: page === currentPage }"
          >
            <button class="page-link" @click="changePage(page)">{{ page }}</button>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === pageCount }">
            <button class="page-link" @click="changePage(currentPage + 1)">Next</button>
          </li>
        </ul>
      </nav>

      <div class="modal" :class="{ 'd-block': showAddLot }" tabindex="-1" style="background: rgba(0,0,0,0.5);">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                {{ isEditing ? 'Edit Parking Lot' : 'Add New Parking Lot' }}
              </h5>
              <button type="button" class="btn-close" @click="closeModal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Lot Name</label>
                <input v-model="newLot.name" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Location</label>
                <input v-model="newLot.location" class="form-control">
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Price per hour (AED)</label>
                  <input v-model.number="newLot.price" type="number" class="form-control" min="0" step="0.01">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Capacity</label>
                  <input v-model.number="newLot.capacity" type="number" class="form-control" min="1">
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="newLot.description" class="form-control" rows="3"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button 
                type="button" 
                class="btn btn-primary" 
                @click="submitLot" 
                :disabled="!isFormValid"
              >
                {{ isEditing ? 'Save Changes' : 'Add Lot' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'users'" class="mt-3">
      <h4>Registered Users</h4>
      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Spot Number</th>
              <th>Lot Name</th>

            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.name || '-' }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.spot_number || '-' }}</td>
              <td>{{ user.lot_name || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeTab === 'history'" class="mt-3">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>Parking History</h4>
        <div>
          <button
            class="btn btn-outline-secondary btn-sm me-2"
            @click="fetchReservations"
            :disabled="loadingReservations"
          >
            Refresh
          </button>
          <button
            class="btn btn-outline-primary btn-sm"
            @click="exportAllReservations"
            :disabled="exportingAdminCsv || loadingReservations"
          >
            <span v-if="exportingAdminCsv">Exporting...</span>
            <span v-else>Export CSV</span>
          </button>
        </div>
      </div>


      <div v-if="loadingReservations" class="alert alert-info">
        Loading reservations...
      </div>
      <div v-else-if="reservationsError" class="alert alert-danger">
        {{ reservationsError }}
      </div>
      <div v-else-if="reservations.length === 0" class="alert alert-secondary">
        No parking records found.
      </div>
      <div v-else class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Lot</th>
              <th>Spot</th>
              <th>Start</th>
              <th>End</th>
              <th>Duration</th>
              <th>Cost</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="res in reservations" :key="res.id">
              <td>{{ res.id }}</td>
              <td>
                <span v-if="res.user_name && res.user_id">
                  {{ res.user_name }} (ID: {{ res.user_id }})
                </span>
                <span v-else-if="res.user_name">
                  {{ res.user_name }}
                </span>
                <span v-else-if="res.user_email">
                  {{ res.user_email }}
                </span>
                <span v-else>
                  -
                </span>
              </td>
              <td>{{ res.user_email || '-' }}</td>
              <td>{{ res.lot_name || '-' }}</td>
              <td>{{ res.spot_id || '-' }}</td>
              <td>{{ res.parking_timestamp || '-' }}</td>
              <td>{{ res.leaving_timestamp || '-' }}</td>
              <td>{{ res.duration || '-' }}</td>
              <td>
                <span v-if="res.parking_cost !== null && res.parking_cost !== undefined">
                  AED {{ res.parking_cost }}
                </span>
                <span v-else>-</span>
              </td>
              <td>
                <span class="badge" :class="res.status === 'Active' ? 'bg-success' : 'bg-secondary'">
                  {{ res.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav v-if="reservationsPageCount > 1">
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: reservationsPage === 1 }">
            <button class="page-link" @click="changeReservationsPage(reservationsPage - 1)">Previous</button>
          </li>
          <li
            v-for="page in reservationsPageCount"
            :key="page"
            class="page-item"
            :class="{ active: page === reservationsPage }"
          >
            <button class="page-link" @click="changeReservationsPage(page)">{{ page }}</button>
          </li>
          <li class="page-item" :class="{ disabled: reservationsPage === reservationsPageCount }">
            <button class="page-link" @click="changeReservationsPage(reservationsPage + 1)">Next</button>
          </li>
        </ul>
      </nav>
    </div>

    <div v-if="activeTab === 'analytics'" class="mt-3">
      <AdminAnalytics />
    </div>
  </div>
</template>

<script>
import AdminAnalytics from './AdminAnalytics.vue'

export default {
  components: {
    AdminAnalytics
  },
  data() {
    return {
      activeTab: 'lots',
      showAddLot: false,
      isEditing: false,
      editingLotId: null,
      lots: [],
      users: [],
      searchQuery: '',
      currentPage: 1,
      perPage: 10,
      totalItems: 0,
      newLot: {
        name: '',
        location: '',
        price: 5.0,
        capacity: 10,
        description: ''
      },
      reservations: [],
      reservationsPage: 1,
      reservationsPerPage: 10,
      reservationsTotalItems: 0,
      loadingReservations: false,
      reservationsError: null,
      exportingAdminCsv: false
    }
  },

  computed: {
    pageCount() {
      return Math.ceil(this.totalItems / this.perPage)
    },
    isFormValid() {
      return (
        this.newLot.name.trim() !== '' &&
        this.newLot.location.trim() !== '' &&
        this.newLot.price > 0 &&
        this.newLot.capacity > 0
      )
    },
    reservationsPageCount() {
      return Math.ceil(this.reservationsTotalItems / this.reservationsPerPage)
    }
  },
  watch: {
    activeTab(val) {
      if (val === 'users' && this.users.length === 0) this.fetchUsers()
      if (val === 'history' && this.reservations.length === 0) this.fetchReservations()
    }
  },
  created() {
    const t = localStorage.getItem('token')
    if (!t) {
      this.$router.push('/login')
      return
    }
    this.fetchLots()
    this.fetchUsers()
  },
  methods: {
    openAddModal() {
      this.isEditing = false
      this.editingLotId = null
      this.resetForm()
      this.showAddLot = true
    },
    openEditModal(lot) {
      this.isEditing = true
      this.editingLotId = lot.id
      this.newLot = {
        name: lot.name,
        location: lot.location,
        price: lot.price,
        capacity: lot.maximum_number_of_spots,
        description: ''
      }
      this.showAddLot = true
    },
    closeModal() {
      this.showAddLot = false
      this.resetForm()
      this.isEditing = false
      this.editingLotId = null
    },
    resetForm() {
      this.newLot = {
        name: '',
        location: '',
        price: 5.0,
        capacity: 10,
        description: ''
      }
    },
    async fetchLots() {
      try {
        const t = localStorage.getItem('token')
        const r = await fetch(
          `http://localhost:5000/api/admin/lots?page=${this.currentPage}&search=${this.searchQuery}`,
          {
            headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
          }
        )
        if (!r.ok) {
          if (r.status === 401) return this.$router.push('/login')
          throw new Error()
        }
        const d = await r.json()
        this.lots = d.items || []
        this.totalItems = d.total_items || 0
      } catch (e) {
        console.error(e)
      }
    },
    async fetchUsers() {
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/admin/users', {
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        if (!r.ok) {
          if (r.status === 401) return this.$router.push('/login')
          throw new Error()
        }
        const d = await r.json()
        this.users = d.users || []
      } catch (e) {
        console.error(e)
      }
    },
    async addLot() {
      try {
        const t = localStorage.getItem('token')
        await fetch('http://localhost:5000/api/admin/lots', {
          method: 'POST',
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.newLot.name,
            capacity: parseInt(this.newLot.capacity),
            location: this.newLot.location,
            price: parseFloat(this.newLot.price)
          })
        })
        this.closeModal()
        this.fetchLots()
      } catch (e) {
        console.error(e)
      }
    },
    async updateLot() {
      try {
        const t = localStorage.getItem('token')
        await fetch(`http://localhost:5000/api/admin/lots/${this.editingLotId}`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.newLot.name,
            capacity: parseInt(this.newLot.capacity),
            location: this.newLot.location,
            price: parseFloat(this.newLot.price)
          })
        })
        this.closeModal()
        this.fetchLots()
      } catch (e) {
        console.error(e)
      }
    },
    async deleteLot(id) {
      if (!confirm('Are you sure you want to delete this parking lot?')) return
      try {
        const t = localStorage.getItem('token')
        const res = await fetch(`http://localhost:5000/api/admin/lots/${id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        if (!res.ok) {
          let msg = 'Failed to delete parking lot'
          try {
            const body = await res.json()
            if (body && body.msg) msg = body.msg
          } catch (e) {
            console.error('Failed to read error response:', e)
          }
          alert(msg)
          return
        }
        this.fetchLots()
      } catch (e) {
        console.error('Delete lot error:', e)
        alert('Error deleting parking lot')
      }
    },
    async submitLot() {
      if (!this.isFormValid) return
      if (this.isEditing) {
        await this.updateLot()
      } else {
        await this.addLot()
      }
    },
    changePage(p) {
      if (p < 1 || p > this.pageCount) return
      this.currentPage = p
      this.fetchLots()
    },
    async fetchReservations() {
      this.loadingReservations = true
      this.reservationsError = null
      try {
        const t = localStorage.getItem('token')
        const r = await fetch(
          `http://localhost:5000/api/admin/reservations?page=${this.reservationsPage}&per_page=${this.reservationsPerPage}`,
          {
            headers: {
              Authorization: `Bearer ${t}`,
              'Content-Type': 'application/json'
            }
          }
        )
        if (!r.ok) {
          if (r.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to load reservations')
        }
        const d = await r.json()
        this.reservations = d.items || []
        this.reservationsTotalItems = d.total_items || 0
      } catch (e) {
        this.reservationsError = e.message
      } finally {
        this.loadingReservations = false
      }
    },
    async exportAllReservations() {
    if (this.exportingAdminCsv) return
    this.exportingAdminCsv = true
    try {
      const t = localStorage.getItem('token')
      if (!t) {
        this.$router.push('/login')
        return
      }
      const startRes = await fetch('http://localhost:5000/api/jobs/admin/reservations/export', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${t}`
        }
      })
      if (!startRes.ok) {
        if (startRes.status === 401) {
          this.$router.push('/login')
          return
        }
        throw new Error('Failed to start export')
      }
      const startData = await startRes.json()
      const taskId = startData.task_id
      if (!taskId) throw new Error('No task id returned')
      let ready = false
      while (!ready) {
        await new Promise(r => setTimeout(r, 1500))
        const statusRes = await fetch(`http://localhost:5000/api/jobs/export/status/${taskId}`, {
          headers: {
            Authorization: `Bearer ${t}`
          }
        })
        if (!statusRes.ok) {
          throw new Error('Failed to check export status')
        }
        const statusData = await statusRes.json()
        ready = !!statusData.ready
      }
      const dlRes = await fetch(`http://localhost:5000/api/jobs/export/result/${taskId}`, {
        headers: {
          Authorization: `Bearer ${t}`
        }
      })
      if (!dlRes.ok) {
        throw new Error('Failed to download export')
      }
      const blob = await dlRes.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `reservations_${Date.now()}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Admin CSV export failed', e)
    } finally {
      this.exportingAdminCsv = false
    }
  },
    changeReservationsPage(p) {
      if (p < 1 || p > this.reservationsPageCount) return
      this.reservationsPage = p
      this.fetchReservations()
    }
  }
}
</script>

<style scoped>
.modal {
  background-color: rgba(0,0,0,0.5);
}
.table-responsive {
  overflow-x: auto;
}
</style>
