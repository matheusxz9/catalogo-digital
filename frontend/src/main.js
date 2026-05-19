import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// Initialize theme from localStorage or prefers-color-scheme
const savedTheme = localStorage.getItem('theme')
if (savedTheme === 'dark' || savedTheme === 'light') {
	document.documentElement.setAttribute('data-theme', savedTheme)
} else {
	const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
	document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
