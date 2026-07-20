<template>
    <div class="container mt-4">
      <h2>Manage Parking Lots</h2>
  
      <div class="mb-3 d-flex justify-content-between align-items-center">
        <button class="btn btn-primary" @click="showAddForm = true">Add New Lot</button>
      </div>
  
      <div v-if="showAddForm" class="card mb-4 p-3">
  <form @submit.prevent="addLot">
    <div class="mb-3">
      <label class="form-label">Max Capacity</label>
      <input v-model.number="newLot.max_capacity" type="number" min="1" class="form-control" required />
    </div>
    <button type="submit" class="btn btn-success me-2">Save</button>
    <button type="button" class="btn btn-secondary" @click="resetForm">Cancel</button>
  </form>
</div>

  
      <table class="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Max Capacity</th>
            <th>Spots Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in lots" :key="lot.id">
            <td>{{ lot.id }}</td>
            <td>{{ lot.max_capacity }}</td>
            <td>{{ lot.spots_count }}</td>
            <td>
              <button class="btn btn-sm btn-danger" @click="deleteLot(lot.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
  
      <div v-if="loading" class="text-center mt-3">
        <div class="spinner-border" role="status"></div>
      </div>
  
      <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  
  export default {
    name: 'AdminParking',
  
    setup() {
      const lots = ref([]);
      const loading = ref(false);
      const error = ref('');
      const showAddForm = ref(false);
      const newLot = ref({
        max_capacity: null,
      });
  
      const fetchLots = async () => {
        loading.value = true;
        error.value = '';
        try {
          const res = await axios.get('http://localhost:5000/api/admin/lots');
          lots.value = res.data;
        } catch (e) {
          error.value = 'Failed to fetch lots.';
        } finally {
          loading.value = false;
        }
      };
  
      const addLot = async () => {
        if (!newLot.value.max_capacity) return;
        loading.value = true;
        error.value = '';
        try {
          await axios.post('http://localhost:5000/api/admin/lots', newLot.value);
          resetForm();
          await fetchLots();
        } catch (e) {
          error.value = 'Failed to add lot.';
        } finally {
          loading.value = false;
        }
      };
  
      const deleteLot = async (id) => {
        if (!confirm('Are you sure you want to delete this lot?')) return;
        loading.value = true;
        error.value = '';
        try {
          await axios.delete(`http://localhost:5000/api/admin/lots/${id}`);
          await fetchLots();
        } catch (e) {
          error.value = 'Failed to delete lot.';
        } finally {
          loading.value = false;
        }
      };
  
      const resetForm = () => {
        showAddForm.value = false;
        newLot.value = {
          max_capacity: null,
        };
        error.value = '';
      };
  
      onMounted(fetchLots);
  
      return {
        lots,
        loading,
        error,
        showAddForm,
        newLot,
        fetchLots,
        addLot,
        deleteLot,
        resetForm,
      };
    },
  };
  </script>
  
  <style scoped>
  .container {
    max-width: 900px;
  }
  </style>
  