<template>
  <div class="chapters">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>{{ subject?.name }} - Chapters</h2>
        <p class="text-muted">{{ subject?.description }}</p>
      </div>
      <div>
        <router-link to="/admin/subjects" class="btn btn-outline-secondary me-2">Back to Subjects</router-link>
        <button class="btn btn-primary" @click="showAddModal">Add Chapter</button>
      </div>
    </div>

    <div class="row">
      <div v-for="chapter in chapters" :key="chapter.id" class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">{{ chapter.name }}</h5>
            <p class="card-text">{{ chapter.description }}</p>
          </div>
          <div class="card-footer bg-transparent border-top-0">
            <div class="btn-group w-100">
              <router-link :to="`/admin/chapters/${chapter.id}/quizzes`" class="btn btn-outline-primary">
                Quizzes
              </router-link>
              <button class="btn btn-outline-secondary" @click="showEditModal(chapter)">Edit</button>
              <button class="btn btn-outline-danger" @click="deleteChapter(chapter.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal fade" id="chapterModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Edit Chapter' : 'Add Chapter' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveChapter">
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
import { useRoute } from 'vue-router'
import axios from 'axios'
import { Modal } from 'bootstrap'

export default {
  name: 'AdminChapters',
  setup() {
    const route = useRoute()
    const subjectId = route.params.subjectId
    const subject = ref(null)
    const chapters = ref([])
    const form = ref({
      name: '',
      description: ''
    })
    const isEditing = ref(false)
    const editingId = ref(null)
    let modal = null

    const fetchSubject = async () => {
      try {
        const response = await axios.get(`/api/admin/subjects/${subjectId}`)
        subject.value = response.data
      } catch (error) {
        console.error('Error fetching subject:', error)
      }
    }

    const fetchChapters = async () => {
      try {
        const response = await axios.get(`/api/admin/subjects/${subjectId}/chapters`)
        chapters.value = response.data
      } catch (error) {
        console.error('Error fetching chapters:', error)
      }
    }

    const showAddModal = () => {
      isEditing.value = false
      form.value = { name: '', description: '' }
      modal.show()
    }

    const showEditModal = (chapter) => {
      isEditing.value = true
      editingId.value = chapter.id
      form.value = {
        name: chapter.name,
        description: chapter.description
      }
      modal.show()
    }

    const saveChapter = async () => {
      try {
        if (isEditing.value) {
          await axios.put(`/api/admin/chapters/${editingId.value}`, form.value)
        } else {
          await axios.post(`/api/admin/subjects/${subjectId}/chapters`, form.value)
        }
        modal.hide()
        fetchChapters()
      } catch (error) {
        console.error('Error saving chapter:', error)
      }
    }

    const deleteChapter = async (id) => {
      if (!confirm('Are you sure you want to delete this chapter?')) return
      try {
        await axios.delete(`/api/admin/chapters/${id}`)
        fetchChapters()
      } catch (error) {
        console.error('Error deleting chapter:', error)
      }
    }

    onMounted(() => {
      modal = new Modal(document.getElementById('chapterModal'))
      fetchSubject()
      fetchChapters()
    })

    return {
      subject,
      chapters,
      form,
      isEditing,
      showAddModal,
      showEditModal,
      saveChapter,
      deleteChapter
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