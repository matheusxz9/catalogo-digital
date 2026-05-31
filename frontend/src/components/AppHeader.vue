<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const darkMode = ref(false)

function toggleTema() {
  darkMode.value = !darkMode.value
  document.documentElement.classList.toggle('dark', darkMode.value)
  localStorage.setItem('catalogo_theme', darkMode.value ? 'dark' : 'light')
}

function isAdminRoute() {
  return route.path.startsWith('/admin')
}

onMounted(() => {
  const saved = localStorage.getItem('catalogo_theme')
  if (saved === 'dark') {
    darkMode.value = true
    document.documentElement.classList.add('dark')
  } else if (saved === 'light') {
    document.documentElement.classList.remove('dark')
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    darkMode.value = true
    document.documentElement.classList.add('dark')
  }
})
</script>

<template>
  <header class="sticky top-0 z-50" :style="{ background: 'var(--bg-card)', backdropFilter: 'blur(16px)', borderBottom: '1px solid var(--border)' }">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14 sm:h-16">

        <router-link to="/" class="flex items-center gap-2.5 group">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold transition-all duration-200 group-hover:scale-105"
            :style="{ background: 'var(--accent-gradient)' }">SBM</div>
          <div class="hidden sm:block">
            <p class="font-display text-sm font-semibold leading-tight" :style="{ color: 'var(--text-bright)' }">Studio Bella Mizi</p>
            <p class="text-[10px] leading-tight" :style="{ color: 'var(--text-dim)' }">Catálogo Digital</p>
          </div>
        </router-link>

        <div class="flex items-center gap-2">
          <router-link v-if="!isAdminRoute()" to="/admin/login"
            class="w-9 h-9 rounded-xl flex items-center justify-center transition-all"
            :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }"
            title="Admin">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </router-link>

          <button @click="toggleTema"
            class="w-9 h-9 rounded-xl flex items-center justify-center transition-all"
            :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }"
            :title="darkMode ? 'Modo claro' : 'Modo escuro'">
            <svg v-if="darkMode" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
