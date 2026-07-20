<template>
  <div class="subjects">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Subjects</h2>
      <button class="btn btn-primary" @click="showAddModal">Add Subject</button>
    </div>

    <div class="row">
      <div v-for="subject in subjects" :key="subject.id" class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">{{ subject.name }}</h5>
            <p class="card-text">{{ subject.description }}</p>
          </div>
          <div class="card-footer bg-transparent border-top-0">
            <div class="btn-group w-100">
              <router-link :to="`/admin/subjects/${subject.id}/chapters`" class="btn btn-outline-primary">
                Chapters
              </router-link>
              <button class="btn btn-outline-secondary" @click="showEditModal(subject)">Edit</button>
              <button class="btn btn-outline-danger" @click="deleteSubject(subject.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal fade" id="subjectModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Edit Subject' : 'Add Subject' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSubject">
              <div class="mb-3">
                <label for="name" class="form-label">Name</label>
                <input type="text" class="form-control" id="name" v-model="form.name" required>
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" v-model="form.description" rows="3"></textarea>
              </div>
              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Save</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'

export default {
  name: 'AdminSubjects',
  setup() {
    const subjects = ref([])
    const form = ref({
      name: '',
      description: ''
    })
    const isEditing = ref(false)
    const editingId = ref(null)
    let modal = null

    const fetchSubjects = async () => {
      try {
        const response = await axios.get('/api/admin/subjects')
        subjects.value = response.data
      } catch (error) {
        console.error('Error fetching subjects:', error)
      }
    }

    const showAddModal = () => {
      isEditing.value = false
      form.value = { name: '', description: '' }
      modal.show()
    }

    const showEditModal = (subject) => {
      isEditing.value = true
      editingId.value = subject.id
      form.value = {
        name: subject.name,
        description: subject.description
      }
      modal.show()
    }

    const saveSubject = async () => {
      try {
        if (isEditing.value) {
          await axios.put(`/api/admin/subjects/${editingId.value}`, form.value)
        } else {
          await axios.post('/api/admin/subjects', form.value)
        }
        modal.hide()
        fetchSubjects()
      } catch (error) {
        console.error('Error saving subject:', error)
      }
    }

    const deleteSubject = async (id) => {
      if (!confirm('Are you sure you want to delete this subject?')) return
      try {
        await axios.delete(`/api/admin/subjects/${id}`)
        fetchSubjects()
      } catch (error) {
        console.error('Error deleting subject:', error)
      }
    }

    onMounted(() => {
      modal = new Modal(document.getElementById('subjectModal'))
      fetchSubjects()
    })

    return {
      subjects,
      form,
      isEditing,
      showAddModal,
      showEditModal,
      saveSubject,
      deleteSubject
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.btn-group {
  gap: 0.5rem;
}
</style> 