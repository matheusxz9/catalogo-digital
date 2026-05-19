<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const menuOpen = ref(false);

const isDark = ref(false);

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
  isDark.value = theme === 'dark'
}

function toggleTheme() {
  const next = isDark.value ? 'light' : 'dark'
  applyTheme(next)
}

onMounted(() => {
  const t = document.documentElement.getAttribute('data-theme') || localStorage.getItem('theme')
  isDark.value = t === 'dark'
})
</script>

<template>
  <header class="bg-white border-b border-rose-100 sticky top-0 z-50" style="box-shadow: 0 1px 16px rgba(233,30,140,0.07)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-16 sm:h-20">

        <!-- Logo -->
        <a href="/" class="flex items-center gap-3 group">
          <div class="relative">
            <img
              src="/logo.jpeg"
              alt="Studio Bella Mizi"
              class="w-10 h-10 sm:w-12 sm:h-12 rounded-full object-cover ring-2 ring-rose-200 group-hover:ring-rose-400 transition-all duration-300"
            />
            <div class="absolute inset-0 rounded-full bg-rose-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </div>
          <div>
            <span class="block font-display font-semibold text-lg sm:text-xl text-charcoal leading-tight tracking-wide">
              Studio Bella Mizi
            </span>
            <span class="block text-xs text-rose-400 font-body tracking-widest uppercase">
              Beleza &amp; Cuidados
            </span>
          </div>
        </a>

        <!-- Nav desktop -->
        <nav class="hidden sm:flex items-center gap-6">
          <a
            href="/"
            class="text-sm font-body font-medium text-gray-500 hover:text-rose-500 transition-colors duration-200 tracking-wide"
          >
            Catálogo
          </a>
          <a
            href="/admin"
            class="text-sm font-body font-medium text-gray-400 hover:text-rose-400 transition-colors duration-200 border border-rose-100 hover:border-rose-300 px-4 py-1.5 rounded-full"
          >
            Admin
          </a>
          <!-- Theme toggle -->
          <button
            @click="toggleTheme"
            :aria-pressed="isDark.toString()"
            class="ml-2 p-2.5 rounded-full bg-rose-50 hover:bg-rose-100 text-rose-500 transition-colors"
            title="Alternar tema claro/escuro"
          >
            <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 transition-transform hover:rotate-45 duration-300">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 transition-transform hover:-rotate-12 duration-300">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
            </svg>
          </button>
        </nav>

        <!-- Mobile admin link -->
        <a
          href="/admin"
          class="sm:hidden text-xs font-body text-gray-400 hover:text-rose-400 transition-colors border border-rose-100 px-3 py-1.5 rounded-full"
        >
          Admin
        </a>

      </div>
    </div>
  </header>
</template>