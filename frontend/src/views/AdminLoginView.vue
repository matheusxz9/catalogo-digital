<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()
const email = ref('')
const senha = ref('')
const erro = ref(null)
const carregando = ref(false)

async function entrar() {
  erro.value = null
  carregando.value = true
  try {
    const { access_token } = await api.login(email.value, senha.value)
    localStorage.setItem('token', access_token)
    router.push({ name: 'Admin' })
  } catch (e) {
    erro.value = e.message || 'Email ou senha incorretos'
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4"
    :style="{ background: 'linear-gradient(135deg, var(--bg), var(--accent-soft))' }">
    <div class="w-full max-w-sm animate-fade-in-up">
      <button @click="router.push('/')"
        class="flex items-center gap-1.5 text-sm font-medium mb-6 transition-all duration-200 group"
        :style="{ color: 'var(--text-dim)' }">
        <svg class="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
        </svg>
        Voltar ao catálogo
      </button>

      <div class="glass-premium rounded-2xl p-8">
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4"
            :style="{ background: 'var(--accent-soft)' }">
            <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"
              :style="{ color: 'var(--accent)' }">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </div>
          <h1 class="font-display text-2xl font-semibold" :style="{ color: 'var(--text-bright)' }">Área Admin</h1>
          <p class="text-xs mt-1 tracking-wide" :style="{ color: 'var(--text-dim)' }">Studio Bella Mizi</p>
        </div>

        <div v-if="erro" class="px-4 py-3 rounded-xl text-sm mb-5 animate-fade-in-up"
          :style="{ background: 'rgba(var(--ctp-red), 0.1)', color: 'var(--ctp-red)', border: '1px solid rgba(var(--ctp-red), 0.15)' }">
          {{ erro }}
        </div>

        <form @submit.prevent="entrar" class="space-y-4">
          <div>
            <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Email</label>
            <input v-model="email" type="email" required autocomplete="email"
              class="input-field" placeholder="seu@email.com" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Senha</label>
            <input v-model="senha" type="password" required autocomplete="current-password"
              class="input-field" placeholder="••••••••" />
          </div>
          <button type="submit" :disabled="carregando"
            class="btn-primary w-full justify-center text-base py-3.5"
            :style="carregando ? { opacity: 0.6 } : {}">
            <span v-if="carregando" class="flex items-center gap-2">
              <span class="w-4 h-4 rounded-full border-2 animate-spin"
                :style="{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: 'white' }"></span>
              Entrando...
            </span>
            <span v-else>Entrar</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
