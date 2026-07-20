<template>
  <div class="container mt-4">
    <h3>Analytics</h3>

    <ul class="nav nav-tabs mt-3">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'overview' }" @click="tab = 'overview'">
          Overview
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'revenue' }" @click="tab = 'revenue'">
          Revenue
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: tab === 'trends' }" @click="tab = 'trends'">
          Parking Trends
        </button>
      </li>
    </ul>

    <!-- OVERVIEW -->
    <div v-if="tab === 'overview'" class="mt-4">
    <h5>Parking Occupancy</h5>
    <div v-if="overviewError" class="alert alert-danger mt-2">{{ overviewError }}</div>
    <div v-else-if="overviewNoData" class="alert alert-secondary mt-2">
        No parking spots found in the system yet.
    </div>
    <div v-else class="d-flex justify-content-center">
        <div style="width: 550px; height: 550px;">
        <canvas ref="overviewChart"></canvas>
        </div>
    </div>
    </div>


    <!-- REVENUE -->
    <div v-if="tab === 'revenue'" class="mt-4">
      <h5>Daily Revenue (AED)</h5>
      <div v-if="revenueError" class="alert alert-danger mt-2">{{ revenueError }}</div>
      <div v-else-if="revenueNoData" class="alert alert-secondary mt-2">
        No completed parking reservations with cost yet, so there is no revenue data to show.
      </div>
      <canvas v-else ref="revenueChart" height="120"></canvas>
    </div>

    <!-- TRENDS -->
    <div v-if="tab === 'trends'" class="mt-4">
      <h5>Daily Parking Volume</h5>
      <div v-if="trendsError" class="alert alert-danger mt-2">{{ trendsError }}</div>
      <div v-else-if="trendsNoData" class="alert alert-secondary mt-2">
        No parking reservations found yet to show trends.
      </div>
      <canvas v-else ref="trendsChart" height="120"></canvas>
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
  ArcElement,
  Tooltip,
  Legend,
  PieController
} from 'chart.js'

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, ArcElement, Tooltip, Legend, PieController)

export default {
  name: 'AdminAnalytics',
  data() {
    return {
      tab: 'overview',
      overviewChartInstance: null,
      revenueChartInstance: null,
      trendsChartInstance: null,
      overviewError: '',
      revenueError: '',
      trendsError: '',
      overviewNoData: false,
      revenueNoData: false,
      trendsNoData: false
    }
  },
  watch: {
    tab(val) {
      if (val === 'overview') this.loadOverview()
      if (val === 'revenue') this.loadRevenue()
      if (val === 'trends') this.loadTrends()
    }
  },
  mounted() {
    const t = localStorage.getItem('token')
    if (!t) {
      this.$router.push('/login')
      return
    }
    this.loadOverview()
  },
  beforeUnmount() {
    if (this.overviewChartInstance) this.overviewChartInstance.destroy()
    if (this.revenueChartInstance) this.revenueChartInstance.destroy()
    if (this.trendsChartInstance) this.trendsChartInstance.destroy()
  },
  methods: {
    async loadOverview() {
      this.overviewError = ''
      this.overviewNoData = false
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/admin/analytics/overview', {
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        if (!r.ok) {
          if (r.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to load overview analytics')
        }
        const d = await r.json()
        const total = d.total_spots || 0
        const occupied = d.occupied_spots || 0
        const available = d.available_spots || 0

        if (total === 0) {
          this.overviewNoData = true
          if (this.overviewChartInstance) this.overviewChartInstance.destroy()
          return
        }

        if (this.overviewChartInstance) this.overviewChartInstance.destroy()

        this.overviewChartInstance = new Chart(this.$refs.overviewChart, {
          type: 'pie',
          data: {
            labels: ['Occupied', 'Available'],
            datasets: [
              {
                data: [occupied, available],
                backgroundColor: ['#ff6384', '#36a2eb']
              }
            ]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'bottom'
              }
            }
          }
        })
      } catch (e) {
        console.error('Overview analytics error:', e)
        this.overviewError = e.message || 'Error loading overview analytics'
      }
    },
    async loadRevenue() {
      this.revenueError = ''
      this.revenueNoData = false
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/admin/analytics/revenue', {
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        if (!r.ok) {
          if (r.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to load revenue analytics')
        }
        const data = await r.json()
        const labels = data.map(x => x.date)
        const values = data.map(x => x.revenue || 0)

        if (!labels.length) {
          this.revenueNoData = true
          if (this.revenueChartInstance) this.revenueChartInstance.destroy()
          return
        }

        if (this.revenueChartInstance) this.revenueChartInstance.destroy()

        this.revenueChartInstance = new Chart(this.$refs.revenueChart, {
          type: 'line',
          data: {
            labels,
            datasets: [
              {
                label: 'Revenue (AED)',
                data: values,
                borderColor: '#36a2eb',
                backgroundColor: 'rgba(54,162,235,0.1)',
                fill: true,
                tension: 0.2,
                pointRadius: 3
              }
            ]
          },
          options: {
            responsive: true,
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              },
              y: {
                title: {
                  display: true,
                  text: 'Revenue (AED)'
                },
                beginAtZero: true
              }
            },
            plugins: {
              legend: {
                display: true,
                position: 'bottom'
              },
              tooltip: {
                enabled: true
              }
            }
          }
        })
      } catch (e) {
        console.error('Revenue analytics error:', e)
        this.revenueError = e.message || 'Error loading revenue analytics'
      }
    },
    async loadTrends() {
      this.trendsError = ''
      this.trendsNoData = false
      try {
        const t = localStorage.getItem('token')
        const r = await fetch('http://localhost:5000/api/admin/analytics/parking-trends', {
          headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        })
        if (!r.ok) {
          if (r.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error('Failed to load parking trends')
        }
        const data = await r.json()
        const labels = data.map(x => x.date)
        const values = data.map(x => x.count || 0)

        if (!labels.length) {
          this.trendsNoData = true
          if (this.trendsChartInstance) this.trendsChartInstance.destroy()
          return
        }

        if (this.trendsChartInstance) this.trendsChartInstance.destroy()

        this.trendsChartInstance = new Chart(this.$refs.trendsChart, {
          type: 'line',
          data: {
            labels,
            datasets: [
              {
                label: 'Parking Count',
                data: values,
                borderColor: '#ff6384',
                backgroundColor: 'rgba(255,99,132,0.1)',
                fill: true,
                tension: 0.2,
                pointRadius: 3
              }
            ]
          },
          options: {
            responsive: true,
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              },
              y: {
                title: {
                  display: true,
                  text: 'Number of Parkings'
                },
                beginAtZero: true
              }
            },
            plugins: {
              legend: {
                display: true,
                position: 'bottom'
              },
              tooltip: {
                enabled: true
              }
            }
          }
        })
      } catch (e) {
        console.error('Trends analytics error:', e)
        this.trendsError = e.message || 'Error loading parking trends'
      }
    }
  }
}
</script>
