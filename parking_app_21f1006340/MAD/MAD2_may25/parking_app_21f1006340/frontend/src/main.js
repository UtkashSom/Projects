import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { api } from './services/api'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App)
const pinia = createPinia()

// Add global properties
app.config.globalProperties.$api = api

app.use(router)
   .use(pinia)
   .mount('#app')
