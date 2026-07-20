<template>
  <div class="container mt-4">
    <h2>User Dashboard</h2>

    <div v-if="message" class="alert alert-success mt-3">
      {{ message }}
    </div>
    <div v-if="errorMessage" class="alert alert-danger mt-3">
      {{ errorMessage }}
    </div>

    <div class="row mt-4">
      <div class="col-md-7 mb-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4>Available Parking Lots</h4>
          <button class="btn btn-outline-secondary btn-sm" @click="fetchLots" :disabled="loadingLots">
            Refresh
          </button>
        </div>

        <div v-if="loadingLots" class="alert alert-info">
          Loading lots...
        </div>
        <div v-else-if="lotsError" class="alert alert-danger">
          {{ lotsError }}
        </div>
        <div v-else-if="lots.length === 0" class="alert alert-secondary">
          No parking lots available.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Lot</th>
                <th>Location</th>
                <th>Price/hr</th>
                <th>Available</th>
                <th>Capacity</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lot in lots" :key="lot.id">
                <td>{{ lot.name }}</td>
                <td>{{ lot.location }}</td>
                <td>AED {{ lot.price }}</td>
                <td>{{ lot.available_spots }}</td>
                <td>{{ lot.capacity }}</td>
                <td class="text-end">
                  <button
                    class="btn btn-sm btn-primary"
                    :disabled="lot.available_spots === 0 || isReserving || hasActiveReservation"
                    @click="reserveSpot(lot)"
                  >
                    Reserve Spot
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="col-md-5 mb-4">
        <h4>Your Current Parking</h4>
        <div class="card">
          <div class="card-body">
            <div v-if="hasActiveReservation">
              <p class="mb-1"><strong>Spot ID:</strong> {{ activeReservation.spot_id }}</p>
              <p v-if="activeReservation.lot_name" class="mb-1">
                <strong>Lot:</strong> {{ activeReservation.lot_name }}
              </p>
              <p v-if="activeReservation.start_time" class="mb-3">
                <strong>Since:</strong> {{ activeReservation.start_time }}
              </p>
              <button
                class="btn btn-danger"
                :disabled="isReleasing"
                @click="releaseSpot"
              >
                Release Spot
              </button>
            </div>
            <div v-else>
              <p class="mb-0 text-muted">You do not have any active parking reservation.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <hr>

    <UserAnalytics />

    <div class="mt-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>Parking History</h4>
        <div>
          <button class="btn btn-outline-secondary btn-sm me-2" @click="fetchHistory" :disabled="loadingHistory">
            Refresh
          </button>
          <button
            class="btn btn-outline-primary btn-sm"
            @click="exportUserHistory"
            :disabled="exportingUserCsv || loadingHistory"
          >
            <span v-if="exportingUserCsv">Exporting...</span>
            <span v-else>Export CSV</span>
          </button>
        </div>
      </div>

      <div v-if="loadingHistory" class="alert alert-info">
        Loading history...
      </div>
      <div v-else-if="historyError" class="alert alert-danger">
        {{ historyError }}
      </div>
      <div v-else-if="history.length === 0" class="alert alert-secondary">
        No parking history found.
      </div>
      <div v-else class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Spot ID</th>
              <th>Lot</th>
              <th>Start Time</th>
              <th>End Time</th>
              <th>Cost</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in history" :key="item.id">
              <td>{{ item.spot_id }}</td>
              <td>{{ item.lot_name || '-' }}</td>
              <td>{{ item.parking_timestamp || '-' }}</td>
              <td>{{ item.leaving_timestamp || '-' }}</td>
              <td>
                <span v-if="item.parking_cost !== null && item.parking_cost !== undefined">
                  AED {{ item.parking_cost }}
                </span>
                <span v-else>-</span>
              </td>
              <td>
                <span
                  class="badge"
                  :class="item.leaving_timestamp ? 'bg-secondary' : 'bg-success'"
                >
                  {{ item.leaving_timestamp ? 'Completed' : 'Active' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import UserAnalytics from './UserAnalytics.vue'

export default {
  name: 'UserDashboard',
  components: {
    UserAnalytics
  },
  data() {
    return {
      lots: [],
      loadingLots: false,
      lotsError: null,
      activeReservation: null,
      isReserving: false,
      isReleasing: false,
      history: [],
      loadingHistory: false,
      historyError: null,
      message: '',
      errorMessage: '',
      exportingUserCsv: false
    }
  },
  computed: {
    hasActiveReservation() {
      return !!this.activeReservation
    }
  },
  created() {
    const t = localStorage.getItem('token')
    if (!t) {
      this.$router.push('/login')
      return
    }
    this.fetchLots()
    this.fetchHistory()
  },
  methods: {
    async fetchLots() {
      this.loadingLots = true
      this.lotsError = null
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/user/lots', {
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        if (!r.ok) {
          if (r.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to load lots')
        }
        const d = await r.json()
        this.lots = d.lots || []
      } catch (e) {
        this.lotsError = e.message
      } finally {
        this.loadingLots = false
      }
    },
    async fetchHistory() {
      this.loadingHistory = true
      this.historyError = null
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/user/history', {
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        if (!r.ok) {
          if (r.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to load history')
        }
        const d = await r.json()
        const items = d.history || []
        this.history = items.map((item, index) => ({
          id: index + 1,
          spot_id: item.spot_id,
          lot_id: item.lot_id,
          lot_name: item.lot_name,
          parking_timestamp: item.parking_timestamp,
          leaving_timestamp: item.leaving_timestamp,
          parking_cost: item.parking_cost
        }))
        this.detectActiveReservationFromHistory()
      } catch (e) {
        this.historyError = e.message
      } finally {
        this.loadingHistory = false
      }
    },
    async exportUserHistory() {
      if (this.exportingUserCsv) return
      this.exportingUserCsv = true
      this.errorMessage = ''
      this.message = ''
      try {
        const t = localStorage.getItem('token')
        if (!t) {
          this.$router.push('/login')
          return
        }
        const r = await fetch('http://localhost:5000/api/user/export-history', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${t}`,
            'Content-Type': 'application/json'
          }
        })
        if (!r.ok) {
          if (r.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to start export')
        }
        const d = await r.json()
        this.message = d.message || 'Export started. Check your email for the CSV file.'
      } catch (e) {
        this.errorMessage = 'Could not start export. Please try again.'
      } finally {
        this.exportingUserCsv = false
      }
    },
    detectActiveReservationFromHistory() {
      const active = this.history.find(h => !h.leaving_timestamp)
      if (active) {
        let lotName = null
        for (const lot of this.lots) {
          if (active.lot_id && active.lot_id === lot.id) {
            lotName = lot.name
            break
          }
        }
        this.activeReservation = {
          spot_id: active.spot_id,
          lot_name: lotName,
          start_time: active.parking_timestamp
        }
      } else {
        this.activeReservation = null
      }
    },
    async reserveSpot(lot) {
      if (this.hasActiveReservation) {
        this.errorMessage = 'You already have an active reservation.'
        this.message = ''
        return
      }
      this.isReserving = true
      this.errorMessage = ''
      this.message = ''
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/user/reserve', {
          method: 'POST',
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ lot_id: lot.id })
        })
        const d = await r.json()
        if (!r.ok) {
          this.errorMessage = d.msg || 'Failed to reserve spot'
          this.message = ''
          return
        }
        this.message = d.msg || 'Spot reserved successfully'
        this.errorMessage = ''
        this.activeReservation = {
          spot_id: d.spot_id,
          lot_name: lot.name,
          start_time: null
        }
        this.fetchLots()
        this.fetchHistory()
      } catch (e) {
        this.errorMessage = 'Error reserving spot'
        this.message = ''
      } finally {
        this.isReserving = false
      }
    },
    async releaseSpot() {
      if (!this.hasActiveReservation) return
      this.isReleasing = true
      this.errorMessage = ''
      this.message = ''
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/user/release', {
          method: 'POST',
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        const d = await r.json()
        if (!r.ok) {
          this.errorMessage = d.msg || 'Failed to release spot'
          this.message = ''
          return
        }
        this.message = d.msg || 'Spot released successfully'
        this.errorMessage = ''
        this.activeReservation = null
        this.fetchLots()
        this.fetchHistory()
      } catch (e) {
        this.errorMessage = 'Error releasing spot'
        this.message = ''
      } finally {
        this.isReleasing = false
      }
    }
  }
}
</script>
