<script setup>
import { useRouter } from 'vue-router'
import { useTemaStore } from '@/stores/tema'

const router = useRouter()
const tema = useTemaStore()
</script>

<template>
  <footer class="border-t transition-colors" :style="{ background: 'var(--bg-card-solid)', borderColor: 'var(--border)' }">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 py-12">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-8">
        <div>
          <div class="flex items-center gap-2.5 mb-3">
            <img src="/logo.svg" alt="Studio Bella Mizi" class="w-8 h-8 rounded-lg" />
            <div>
              <p class="font-display text-sm font-semibold" :style="{ color: 'var(--text-bright)' }">Studio Bella Mizi</p>
            </div>
          </div>
          <p class="text-xs leading-relaxed" :style="{ color: 'var(--text-dim)' }">
            Produtos selecionados com cuidado para realçar sua beleza natural.
          </p>
        </div>

        <div>
          <p class="text-xs font-semibold uppercase tracking-wider mb-3" :style="{ color: 'var(--text-dim)' }">Links</p>
          <div class="space-y-2">
            <router-link to="/" class="block text-xs transition-all" :style="{ color: 'var(--text-dim)' }"
              @mouseenter="$event.target.style.color = 'var(--accent)'"
              @mouseleave="$event.target.style.color = ''">Catálogo</router-link>
            <router-link to="/admin/login" class="block text-xs transition-all" :style="{ color: 'var(--text-dim)' }"
              @mouseenter="$event.target.style.color = 'var(--accent)'"
              @mouseleave="$event.target.style.color = ''">Admin</router-link>
          </div>
        </div>

        <div>
          <p class="text-xs font-semibold uppercase tracking-wider mb-3" :style="{ color: 'var(--text-dim)' }">Aparência</p>
          <button @click="tema.toggle()"
            class="flex items-center gap-2 text-xs transition-all cursor-pointer" :style="{ color: 'var(--text-dim)' }"
            @mouseenter="$event.target.style.color = 'var(--accent)'"
            @mouseleave="$event.target.style.color = ''">
            <svg v-if="tema.escuro" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
            {{ tema.escuro ? 'Modo Claro' : 'Modo Escuro' }}
          </button>
        </div>
      </div>

      <div class="mt-8 pt-6 border-t text-center" :style="{ borderColor: 'var(--border)' }">
        <p class="text-[11px]" :style="{ color: 'var(--text-dim)' }">
          &copy; {{ new Date().getFullYear() }} Studio Bella Mizi. Todos os direitos reservados.
        </p>
      </div>
    </div>
  </footer>
</template>
