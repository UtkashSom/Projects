import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'

// Mock axios
vi.mock('axios')

// Import components
import Dashboard from '@/views/admin/Dashboard.vue'
import Subjects from '@/views/admin/Subjects.vue'
import Chapters from '@/views/admin/Chapters.vue'
import Quizzes from '@/views/admin/Quizzes.vue'
import Questions from '@/views/admin/Questions.vue'
import Users from '@/views/admin/Users.vue'

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/admin',
      component: Dashboard,
      children: [
        {
          path: 'subjects',
          component: Subjects
        },
        {
          path: 'subjects/:subjectId/chapters',
          component: Chapters
        },
        {
          path: 'chapters/:chapterId/quizzes',
          component: Quizzes
        },
        {
          path: 'quizzes/:quizId/questions',
          component: Questions
        },
        {
          path: 'users',
          component: Users
        }
      ]
    }
  ]
})

// Mock data
const mockSubjects = [
  { id: 1, name: 'Test Subject', description: 'Test Description' }
]

const mockChapters = [
  { id: 1, name: 'Test Chapter', description: 'Test Description', subject_id: 1 }
]

const mockQuizzes = [
  { id: 1, title: 'Test Quiz', description: 'Test Description', duration_minutes: 30, chapter_id: 1 }
]

const mockQuestions = [
  {
    id: 1,
    text: 'Test Question',
    option_a: 'Option A',
    option_b: 'Option B',
    option_c: 'Option C',
    option_d: 'Option D',
    correct_answer: 'A',
    quiz_id: 1
  }
]

const mockUsers = [
  {
    id: 1,
    full_name: 'Test User',
    email: 'test@example.com',
    qualification: 'Test Qualification',
    date_of_birth: '1990-01-01',
    created_at: '2024-01-01'
  }
]

describe('Admin Components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Dashboard.vue', () => {
    it('renders properly', () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [createTestingPinia()]
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.navbar-brand').text()).toBe('Quiz Master Admin')
    })
  })

  describe('Subjects.vue', () => {
    it('renders subjects list', async () => {
      axios.get.mockResolvedValueOnce({ data: mockSubjects })
      
      const wrapper = mount(Subjects, {
        global: {
          plugins: [createTestingPinia()]
        }
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.findAll('.card').length).toBe(mockSubjects.length)
      expect(wrapper.find('.card-title').text()).toBe(mockSubjects[0].name)
    })

    it('creates new subject', async () => {
      const newSubject = { name: 'New Subject', description: 'New Description' }
      axios.post.mockResolvedValueOnce({ data: { id: 2, ...newSubject } })
      
      const wrapper = mount(Subjects, {
        global: {
          plugins: [createTestingPinia()]
        }
      })
      
      await wrapper.vm.showAddModal()
      wrapper.vm.form = newSubject
      await wrapper.vm.saveSubject()
      
      expect(axios.post).toHaveBeenCalledWith('/api/admin/subjects', newSubject)
    })
  })

  describe('Chapters.vue', () => {
    it('renders chapters list', async () => {
      axios.get.mockResolvedValueOnce({ data: mockChapters })
      
      const wrapper = mount(Chapters, {
        global: {
          plugins: [createTestingPinia()]
        },
        props: {
          subjectId: 1
        }
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.findAll('.card').length).toBe(mockChapters.length)
      expect(wrapper.find('.card-title').text()).toBe(mockChapters[0].name)
    })
  })

  describe('Quizzes.vue', () => {
    it('renders quizzes list', async () => {
      axios.get.mockResolvedValueOnce({ data: mockQuizzes })
      
      const wrapper = mount(Quizzes, {
        global: {
          plugins: [createTestingPinia()]
        },
        props: {
          chapterId: 1
        }
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.findAll('.card').length).toBe(mockQuizzes.length)
      expect(wrapper.find('.card-title').text()).toBe(mockQuizzes[0].title)
    })
  })

  describe('Questions.vue', () => {
    it('renders questions list', async () => {
      axios.get.mockResolvedValueOnce({ data: mockQuestions })
      
      const wrapper = mount(Questions, {
        global: {
          plugins: [createTestingPinia()]
        },
        props: {
          quizId: 1
        }
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.findAll('.card').length).toBe(mockQuestions.length)
      expect(wrapper.find('.card-title').text()).toBe(mockQuestions[0].text)
    })
  })

  describe('Users.vue', () => {
    it('renders users list', async () => {
      axios.get.mockResolvedValueOnce({ data: mockUsers })
      
      const wrapper = mount(Users, {
        global: {
          plugins: [createTestingPinia()]
        }
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.findAll('tr').length).toBe(mockUsers.length + 1) // +1 for header row
      expect(wrapper.find('td').text()).toBe(mockUsers[0].full_name)
    })

    it('filters users based on search query', async () => {
      axios.get.mockResolvedValueOnce({ data: mockUsers })
      
      const wrapper = mount(Users, {
        global: {
          plugins: [createTestingPinia()]
        }
      })
      
      await wrapper.vm.$nextTick()
      await wrapper.setData({ searchQuery: 'Test' })
      
      expect(wrapper.vm.filteredUsers.length).toBe(1)
      expect(wrapper.vm.filteredUsers[0].full_name).toBe('Test User')
    })
  })
}) 