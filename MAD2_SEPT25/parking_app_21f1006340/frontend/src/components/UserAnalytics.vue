<template>
  <div class="mt-4">
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h4 class="mb-0">My Parking Activity</h4>
      <button
        class="btn btn-outline-secondary btn-sm"
        @click="loadHistory"
        :disabled="loading"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="loading" class="alert alert-info mt-2">
      Loading analytics...
    </div>

    <div v-else-if="error" class="alert alert-danger mt-2">
      {{ error }}
    </div>

    <div v-else-if="noData" class="alert alert-secondary mt-2">
      You have no parking history yet.
    </div>

    <div v-else class="d-flex justify-content-center mt-2">
      <div style="width: 1000px; max-width: 100%;">
        <canvas ref="userChart" height="120"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend
} from 'chart.js'

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend
)

export default {
  name: 'UserAnalytics',
  data() {
    return {
      chartInstance: null,
      error: '',
      noData: false,
      loading: false
    }
  },
  mounted() {
    this.loadHistory()
  },
  beforeUnmount() {
    if (this.chartInstance) this.chartInstance.destroy()
  },
  methods: {
    async loadHistory() {
      this.error = ''
      this.noData = false
      this.loading = true

      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/user/analytics/history', {
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
          throw new Error('Failed to load user analytics')
        }

        const data = await r.json()
        const labels = data.map(x => x.date)
        const values = data.map(x => x.count)

        if (!labels.length) {
          this.noData = true
          this.loading = false
          if (this.chartInstance) {
            this.chartInstance.destroy()
            this.chartInstance = null
          }
          return
        }

        this.noData = false
        this.loading = false

        if (this.chartInstance) {
          this.chartInstance.destroy()
          this.chartInstance = null
        }

        await this.$nextTick()

        const canvas = this.$refs.userChart
        if (!canvas) {
          console.error('Chart canvas not found after nextTick')
          return
        }

        const ctx = canvas.getContext('2d')
        if (!ctx) {
          console.error('Could not get 2D context')
          return
        }

        this.chartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels,
            datasets: [
              {
                label: 'Reservations',
                data: values,
                borderColor: '#36a2eb',
                backgroundColor: 'rgba(54,162,235,0.1)',
                pointRadius: 3,
                tension: 0.2,
                fill: true
              }
            ]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'bottom'
              },
              tooltip: {
                enabled: true
              }
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              },
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Times Parked'
                },
                ticks: {
                  precision: 0
                }
              }
            }
          }
        })
      } catch (e) {
        console.error('User analytics error:', e)
        this.error = e.message || 'Error loading analytics'
        this.loading = false
      }
    }
  }
}
</script>
