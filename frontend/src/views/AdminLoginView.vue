<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/services/api";

const router = useRouter();
const email = ref("");
const senha = ref("");
const erro = ref(null);
const carregando = ref(false);

async function entrar() {
  erro.value = null;
  carregando.value = true;
  try {
    const { access_token } = await api.login(email.value, senha.value);
    localStorage.setItem("token", access_token);
    router.push({ name: "admin" });
  } catch (e) {
    erro.value = e.message || "Email ou senha incorretos";
  } finally {
    carregando.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blush-100 via-rose-50 to-blush-50 flex flex-col items-center justify-center px-4">

    <!-- Back link -->
    <button
      @click="router.push({ name: 'Catalogo' })"
      class="flex items-center gap-1.5 text-sm font-body text-gray-400 hover:text-rose-500 transition-colors mb-8 group"
    >
      <svg class="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
      </svg>
      Voltar ao catálogo
    </button>

    <!-- Card -->
    <div class="bg-white rounded-2xl border border-rose-100 shadow-sm w-full max-w-sm p-8">

      <!-- Logo / Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-rose-50 rounded-2xl mb-4">
          <svg class="w-7 h-7 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
          </svg>
        </div>
        <h1 class="font-display text-2xl font-semibold text-charcoal">Área Admin</h1>
        <p class="font-body text-xs text-gray-400 mt-1 tracking-wide">Studio Bella Mizi</p>
      </div>

      <!-- Erro -->
      <div
        v-if="erro"
        class="bg-red-50 border border-red-100 text-red-600 text-sm font-body px-4 py-3 rounded-xl mb-5"
      >
        {{ erro }}
      </div>

      <!-- Campos -->
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-body font-semibold text-gray-600 mb-1.5 tracking-wide">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="admin@email.com"
            class="w-full border border-rose-100 rounded-xl px-4 py-3 text-sm font-body text-charcoal placeholder-gray-300 focus:border-rose-300 focus:ring-2 focus:ring-rose-100 transition-all"
          />
        </div>

        <div>
          <label class="block text-xs font-body font-semibold text-gray-600 mb-1.5 tracking-wide">Senha</label>
          <input
            v-model="senha"
            type="password"
            placeholder="••••••••"
            @keyup.enter="entrar"
            class="w-full border border-rose-100 rounded-xl px-4 py-3 text-sm font-body text-charcoal placeholder-gray-300 focus:border-rose-300 focus:ring-2 focus:ring-rose-100 transition-all"
          />
        </div>
      </div>

      <!-- Submit -->
      <button
        :disabled="carregando"
        @click="entrar"
        class="w-full mt-6 bg-rose-500 hover:bg-rose-600 disabled:bg-rose-200 text-white font-body font-semibold py-3.5 rounded-xl transition-all duration-200 hover:-translate-y-0.5 disabled:translate-y-0 disabled:cursor-not-allowed text-sm tracking-wide"
      >
        {{ carregando ? 'Entrando...' : 'Entrar' }}
      </button>
    </div>

  </div>
</template>