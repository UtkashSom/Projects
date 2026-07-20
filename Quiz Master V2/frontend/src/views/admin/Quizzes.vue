<template>
  <div class="quizzes">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>{{ chapter?.name }} - Quizzes</h2>
        <p class="text-muted">{{ chapter?.description }}</p>
      </div>
      <div>
        <router-link :to="`/admin/subjects/${chapter?.subject_id}/chapters`" class="btn btn-outline-secondary me-2">
          Back to Chapters
        </router-link>
        <button class="btn btn-primary" @click="showAddModal">Add Quiz</button>
      </div>
    </div>

    <div class="row">
      <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">{{ quiz.title }}</h5>
            <p class="card-text">{{ quiz.description }}</p>
            <p class="text-muted">Duration: {{ quiz.duration_minutes }} minutes</p>
          </div>
          <div class="card-footer bg-transparent border-top-0">
            <div class="btn-group w-100">
              <router-link :to="`/admin/quizzes/${quiz.id}/questions`" class="btn btn-outline-primary">
                Questions
              </router-link>
              <button class="btn btn-outline-secondary" @click="showEditModal(quiz)">Edit</button>
              <button class="btn btn-outline-danger" @click="deleteQuiz(quiz.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal fade" id="quizModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Edit Quiz' : 'Add Quiz' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuiz">
              <div class="mb-3">
                <label for="title" class="form-label">Title</label>
                <input type="text" class="form-control" id="title" v-model="form.title" required>
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" v-model="form.description" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label for="duration" class="form-label">Duration (minutes)</label>
                <input type="number" class="form-control" id="duration" v-model="form.duration_minutes" min="1" required>
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
  name: 'AdminQuizzes',
  setup() {
    const route = useRoute()
    const chapterId = route.params.chapterId
    const chapter = ref(null)
    const quizzes = ref([])
    const form = ref({
      title: '',
      description: '',
      duration_minutes: 30
    })
    const isEditing = ref(false)
    const editingId = ref(null)
    let modal = null

    const fetchChapter = async () => {
      try {
        const response = await axios.get(`/api/admin/chapters/${chapterId}`)
        chapter.value = response.data
      } catch (error) {
        console.error('Error fetching chapter:', error)
      }
    }

    const fetchQuizzes = async () => {
      try {
        const response = await axios.get(`/api/admin/chapters/${chapterId}/quizzes`)
        quizzes.value = response.data
      } catch (error) {
        console.error('Error fetching quizzes:', error)
      }
    }

    const showAddModal = () => {
      isEditing.value = false
      form.value = { title: '', description: '', duration_minutes: 30 }
      modal.show()
    }

    const showEditModal = (quiz) => {
      isEditing.value = true
      editingId.value = quiz.id
      form.value = {
        title: quiz.title,
        description: quiz.description,
        duration_minutes: quiz.duration_minutes
      }
      modal.show()
    }

    const saveQuiz = async () => {
      try {
        if (isEditing.value) {
          await axios.put(`/api/admin/quizzes/${editingId.value}`, form.value)
        } else {
          await axios.post(`/api/admin/chapters/${chapterId}/quizzes`, form.value)
        }
        modal.hide()
        fetchQuizzes()
      } catch (error) {
        console.error('Error saving quiz:', error)
      }
    }

    const deleteQuiz = async (id) => {
      if (!confirm('Are you sure you want to delete this quiz?')) return
      try {
        await axios.delete(`/api/admin/quizzes/${id}`)
        fetchQuizzes()
      } catch (error) {
        console.error('Error deleting quiz:', error)
      }
    }

    onMounted(() => {
      modal = new Modal(document.getElementById('quizModal'))
      fetchChapter()
      fetchQuizzes()
    })

    return {
      chapter,
      quizzes,
      form,
      isEditing,
      showAddModal,
      showEditModal,
      saveQuiz,
      deleteQuiz
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
 