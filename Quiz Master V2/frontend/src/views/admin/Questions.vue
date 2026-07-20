<template>
  <div class="questions">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>{{ quiz?.title }} - Questions</h2>
        <p class="text-muted">{{ quiz?.description }}</p>
      </div>
      <div>
        <router-link :to="`/admin/chapters/${quiz?.chapter_id}/quizzes`" class="btn btn-outline-secondary me-2">
          Back to Quizzes
        </router-link>
        <button class="btn btn-primary" @click="showAddModal">Add Question</button>
      </div>
    </div>

    <div class="row">
      <div v-for="question in questions" :key="question.id" class="col-12 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{{ question.text }}</h5>
            <div class="options mt-3">
              <div class="option" :class="{ 'correct': question.correct_answer === 'A' }">
                A. {{ question.option_a }}
              </div>
              <div class="option" :class="{ 'correct': question.correct_answer === 'B' }">
                B. {{ question.option_b }}
              </div>
              <div class="option" :class="{ 'correct': question.correct_answer === 'C' }">
                C. {{ question.option_c }}
              </div>
              <div class="option" :class="{ 'correct': question.correct_answer === 'D' }">
                D. {{ question.option_d }}
              </div>
            </div>
            <div class="mt-3">
              <button class="btn btn-outline-secondary me-2" @click="showEditModal(question)">Edit</button>
              <button class="btn btn-outline-danger" @click="deleteQuestion(question.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal fade" id="questionModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Edit Question' : 'Add Question' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuestion">
              <div class="mb-3">
                <label for="text" class="form-label">Question Text</label>
                <textarea class="form-control" id="text" v-model="form.text" rows="3" required></textarea>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="option_a" class="form-label">Option A</label>
                  <input type="text" class="form-control" id="option_a" v-model="form.option_a" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="option_b" class="form-label">Option B</label>
                  <input type="text" class="form-control" id="option_b" v-model="form.option_b" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="option_c" class="form-label">Option C</label>
                  <input type="text" class="form-control" id="option_c" v-model="form.option_c" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="option_d" class="form-label">Option D</label>
                  <input type="text" class="form-control" id="option_d" v-model="form.option_d" required>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Correct Answer</label>
                <div class="btn-group w-100">
                  <input type="radio" class="btn-check" name="correct_answer" id="option_a_correct" value="A" v-model="form.correct_answer">
                  <label class="btn btn-outline-primary" for="option_a_correct">A</label>
                  
                  <input type="radio" class="btn-check" name="correct_answer" id="option_b_correct" value="B" v-model="form.correct_answer">
                  <label class="btn btn-outline-primary" for="option_b_correct">B</label>
                  
                  <input type="radio" class="btn-check" name="correct_answer" id="option_c_correct" value="C" v-model="form.correct_answer">
                  <label class="btn btn-outline-primary" for="option_c_correct">C</label>
                  
                  <input type="radio" class="btn-check" name="correct_answer" id="option_d_correct" value="D" v-model="form.correct_answer">
                  <label class="btn btn-outline-primary" for="option_d_correct">D</label>
                </div>
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
  name: 'AdminQuestions',
  setup() {
    const route = useRoute()
    const quizId = route.params.quizId
    const quiz = ref(null)
    const questions = ref([])
    const form = ref({
      text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_answer: 'A'
    })
    const isEditing = ref(false)
    const editingId = ref(null)
    let modal = null

    const fetchQuiz = async () => {
      try {
        const response = await axios.get(`/api/admin/quizzes/${quizId}`)
        quiz.value = response.data
      } catch (error) {
        console.error('Error fetching quiz:', error)
      }
    }

    const fetchQuestions = async () => {
      try {
        const response = await axios.get(`/api/admin/quizzes/${quizId}/questions`)
        questions.value = response.data
      } catch (error) {
        console.error('Error fetching questions:', error)
      }
    }

    const showAddModal = () => {
      isEditing.value = false
      form.value = {
        text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_answer: 'A'
      }
      modal.show()
    }

    const showEditModal = (question) => {
      isEditing.value = true
      editingId.value = question.id
      form.value = {
        text: question.text,
        option_a: question.option_a,
        option_b: question.option_b,
        option_c: question.option_c,
        option_d: question.option_d,
        correct_answer: question.correct_answer
      }
      modal.show()
    }

    const saveQuestion = async () => {
      try {
        if (isEditing.value) {
          await axios.put(`/api/admin/questions/${editingId.value}`, form.value)
        } else {
          await axios.post(`/api/admin/quizzes/${quizId}/questions`, form.value)
        }
        modal.hide()
        fetchQuestions()
      } catch (error) {
        console.error('Error saving question:', error)
      }
    }

    const deleteQuestion = async (id) => {
      if (!confirm('Are you sure you want to delete this question?')) return
      try {
        await axios.delete(`/api/admin/questions/${id}`)
        fetchQuestions()
      } catch (error) {
        console.error('Error deleting question:', error)
      }
    }

    onMounted(() => {
      modal = new Modal(document.getElementById('questionModal'))
      fetchQuiz()
      fetchQuestions()
    })

    return {
      quiz,
      questions,
      form,
      isEditing,
      showAddModal,
      showEditModal,
      saveQuestion,
      deleteQuestion
    }
  }
}
</script>

<style scoped>
.options {
  display: grid;
  gap: 1rem;
}

.option {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  background-color: #f8f9fa;
}

.option.correct {
  border-color: #198754;
  background-color: #d1e7dd;
  color: #0f5132;
}

.btn-group {
  gap: 0.5rem;
}

.btn-check:checked + .btn-outline-primary {
  background-color: #0d6efd;
  color: white;
}
</style> 