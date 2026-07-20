<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Parking Lot Spots (Lot ID: {{ lotId }})</h3>
      <button class="btn btn-secondary" @click="$router.back()">Back</button>
    </div>

    <div class="row mb-3">
      <div class="col-md-4 mb-2">
        <div class="card text-center">
          <div class="card-body">
            <h6 class="mb-1">Total Spots</h6>
            <h4 class="mb-0">{{ totalSpots }}</h4>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-2">
        <div class="card text-center">
          <div class="card-body">
            <h6 class="mb-1">Available</h6>
            <h4 class="mb-0">{{ availableCount }}</h4>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-2">
        <div class="card text-center">
          <div class="card-body">
            <h6 class="mb-1">Occupied</h6>
            <h4 class="mb-0">{{ occupiedCount }}</h4>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="loading" class="alert alert-info">
      Loading spots...
    </div>

    <div v-else-if="spots.length" class="table-responsive">
      <table class="table table-striped">
        <thead>
            <tr>
                <th>Spot ID</th>
                <th>Spot Number</th>
                <th>Status</th>
                <th>Since</th>
                <th>Current User</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="spot in spots" :key="spot.id">   
                <td>{{ spot.id }}</td>
                <td>{{ spot.spot_number || spot.id }}</td>
                <td>
                <span :class="statusClass(spot)">{{ statusLabel(spot) }}</span>
                </td>
                <td>
                {{ spot.start_time || '-' }}
                </td>
                <td>
                <span v-if="spot.user_name && spot.user_id">
                    {{ spot.user_name }} (ID: {{ spot.user_id }})
                </span>
                <span v-else-if="spot.user_name">
                    {{ spot.user_name }}
                </span>
                <span v-else-if="spot.user_id">
                    ID: {{ spot.user_id }}
                </span>
                <span v-else>
                    -
                </span>
                </td>
            </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="alert alert-secondary">
      No spots found for this lot.
    </div>
  </div>
</template>

<script>
export default {
  name: 'LotDetails',
  data() {
    return {
      lotId: this.$route.params.id,
      spots: [],
      loading: false,
      error: null,
      totalSpots: 0,
      occupiedCount: 0,
      availableCount: 0
    }
  },
  created() {
    this.fetchSpots()
  },
  methods: {
    async fetchSpots() {
      this.loading = true
      this.error = null
      try {
        const token = localStorage.getItem('token')
        const res = await fetch(
          `http://localhost:5000/api/admin/lots/${this.lotId}/spots`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        )
        if (!res.ok) {
          if (res.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to load spots')
        }
        const data = await res.json()
        this.spots = data.spots || []
        this.updateSummary()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    isOccupied(spot) {
      if (spot.status) {
        const s = String(spot.status).toUpperCase()
        if (s === 'OCCUPIED') return true
        if (s === 'AVAILABLE') return false
      }
      if (spot.user_email || spot.user_id) return true
      return false
    },
    statusLabel(spot) {
      return this.isOccupied(spot) ? 'Occupied' : 'Available'
    },
    statusClass(spot) {
      return this.isOccupied(spot) ? 'badge bg-danger' : 'badge bg-success'
    },
    updateSummary() {
      this.totalSpots = this.spots.length
      this.occupiedCount = this.spots.filter(s => this.isOccupied(s)).length
      this.availableCount = this.totalSpots - this.occupiedCount
    }
  }
}
</script>
