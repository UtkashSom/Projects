<template>
    <div class="container mt-4">
      <h2>Parking Lots Management</h2>
  
      <button class="btn btn-primary mb-3" @click="openCreateModal()">Add New Lot</button>
  
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Capacity</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in lots" :key="lot.id">
            <td>{{ lot.name }}</td>
            <td>{{ lot.price }}</td>
            <td>{{ lot.capacity }}</td>
            <td>
              <button class="btn btn-sm btn-warning me-2" @click="openEditModal(lot)">Edit</button>
              <button class="btn btn-sm btn-danger" @click="deleteLot(lot.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
  
      <div class="modal fade" tabindex="-1" ref="modalRef">
        <div class="modal-dialog">
          <form @submit.prevent="saveLot">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">{{ isEditing ? 'Edit Lot' : 'Add New Lot' }}</h5>
                <button type="button" class="btn-close" @click="closeModal()"></button>
              </div>
              <div class="modal-body">
                <div class="mb-3">
                  <label class="form-label">Name</label>
                  <input v-model="form.name" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Location</label>
                  <input v-model="form.prime_location" type="text" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Price</label>
                  <input v-model.number="form.price" type="number" class="form-control" min="0" required />
                </div>
                <div class="mb-3">
                  <label class="form-label">Capacity</label>
                  <input v-model.number="form.capacity" type="number" class="form-control" min="1" required />
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">{{ isEditing ? 'Update' : 'Create' }}</button>
              </div>
            </div>
          </form>
        </div>
      </div>
  
    </div>
  </template>
  
  <script>
  import * as bootstrap from 'bootstrap'
  import { ref, onMounted } from 'vue'

  export default {
    name: 'ParkingLotList',
    setup() {
      const lots = ref([])
      const form = ref({
        id: null,
        name: '',
        prime_location: '',
        price: 0,
        capacity: 1
      })
      const isEditing = ref(false)
      const modalRef = ref(null)

      const fetchLots = async () => {
        try {
          const res = await fetch('http://localhost:5000/api/admin/lots')
          if (!res.ok) throw new Error('Failed to fetch lots')
          const data = await res.json()
          lots.value = Array.isArray(data.items) ? data.items.map(item => ({
            id: item.id,
            name: item.name,
            prime_location: item.location,
            price: item.price,
            capacity: item.maximum_number_of_spots
          })) : []
        } catch (err) {
          alert(err.message)
        }
      }

      const openCreateModal = () => {
        isEditing.value = false
        form.value = { id: null, name: '', prime_location: '', price: 0, capacity: 1 }
        new bootstrap.Modal(modalRef.value).show()
      }

      const openEditModal = (lot) => {
        isEditing.value = true
        form.value = {
          id: lot.id,
          name: lot.name,
          prime_location: lot.prime_location,
          price: lot.price,
          capacity: lot.capacity
        }
        new bootstrap.Modal(modalRef.value).show()
      }

      const saveLot = async () => {
        try {
          const method = form.value.id ? 'PUT' : 'POST'
          const url = form.value.id
            ? `http://localhost:5000/api/admin/lots/${form.value.id}`
            : 'http://localhost:5000/api/admin/lots'

          const payload = {
            name: form.value.name,
            location: form.value.prime_location,
            price: form.value.price,
            capacity: form.value.capacity
          }

          const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          })

          if (!res.ok) {
            const errorData = await res.json()
            throw new Error(errorData.msg || 'Failed to save lot')
          }

          await fetchLots()
          closeModal()
        } catch (err) {
          alert(err.message)
        }
      }

      const deleteLot = async (id) => {
        if (!confirm('Are you sure you want to delete this lot?')) return
        try {
          const res = await fetch(`http://localhost:5000/api/admin/lots/${id}`, {
            method: 'DELETE'
          })
          if (!res.ok) {
            const errorData = await res.json()
            throw new Error(errorData.msg || 'Failed to delete lot')
          }
          await fetchLots()
        } catch (err) {
          alert(err.message)
        }
      }

      onMounted(() => {
        fetchLots()
      })

      return {
        lots,
        form,
        isEditing,
        modalRef,
        openCreateModal,
        openEditModal,
        closeModal,
        saveLot,
        deleteLot
      }
    }
  }

  </script>
  
  <style scoped>
  </style>
  