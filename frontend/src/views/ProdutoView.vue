<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'

const route = useRoute()
const router = useRouter()

const produto = ref(null)
const carregando = ref(true)
const erro = ref(null)
const imagemAtiva = ref(0)

const imagens = computed(() => {
  if (!produto.value) return []
  if (produto.value.imagens?.length) {
    return produto.value.imagens.map(i => i.imagem_url)
  }
  if (produto.value.imagem_url) return [produto.value.imagem_url]
  return []
})

const esgotado = computed(() => !produto.value || produto.value.estoque === 0)

const WHATSAPP_LINK = computed(() => {
  if (!produto.value) return '#'
  const numero = '5584996997688'
  const mensagem = `Olá! Tenho interesse no produto:\n\n*${produto.value.nome}*\nValor: R$ ${produto.value.preco.toFixed(2)}\n\nPoderia me dar mais informações?`
  return `https://wa.me/${numero}?text=${encodeURIComponent(mensagem)}`
})

function anterior() {
  imagemAtiva.value = imagemAtiva.value > 0
    ? imagemAtiva.value - 1
    : imagens.value.length - 1
}

function proximo() {
  imagemAtiva.value = imagemAtiva.value < imagens.value.length - 1
    ? imagemAtiva.value + 1
    : 0
}

onMounted(async () => {
  const id = Number(route.params.id)
  if (isNaN(id)) { router.replace('/'); return }
  try {
    produto.value = await api.buscarProduto(id)
  } catch {
    erro.value = 'Produto não encontrado'
  } finally {
    carregando.value = false
  }
})
</script>

<template>
  <div class="min-h-screen" :style="{ background: 'var(--bg)' }">
    <AppHeader />

    <main class="max-w-5xl mx-auto px-4 sm:px-6 py-8 pb-20">
      <div v-if="carregando" class="flex items-center justify-center py-32">
        <div class="flex flex-col items-center gap-3">
          <div class="w-10 h-10 rounded-full border-2 animate-spin" :style="{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }"></div>
          <p class="text-sm" :style="{ color: 'var(--text-dim)' }">Carregando...</p>
        </div>
      </div>

      <div v-else-if="erro" class="flex flex-col items-center justify-center py-32 text-center animate-fade-in-up">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
          :style="{ background: 'var(--accent-soft)' }">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            :style="{ color: 'var(--accent)' }" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <p class="font-display text-xl font-light mb-6" :style="{ color: 'var(--text-dim)' }">{{ erro }}</p>
        <button @click="router.push('/')" class="btn-primary">Voltar ao catálogo</button>
      </div>

      <div v-else-if="produto" class="animate-fade-in-up">
        <button @click="router.back()"
          class="flex items-center gap-1.5 text-sm font-medium mb-6 transition-all duration-200 group"
          :style="{ color: 'var(--text-dim)' }">
          <svg class="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          </svg>
          Voltar
        </button>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-10">
          <div class="card-premium overflow-hidden">
            <div class="relative aspect-square" :style="{ background: 'var(--bg)' }">
              <img v-if="imagens.length > 0"
                :src="imagens[imagemAtiva]"
                :alt="produto.nome"
                class="w-full h-full object-contain p-6 sm:p-8 transition-all duration-500"
                :style="{ background: 'var(--bg-card-solid)' }" />
              <div v-else class="w-full h-full flex items-center justify-center"
                :style="{ background: 'var(--accent-soft)' }">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  :style="{ color: 'var(--accent)' }" stroke-width="1">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                </svg>
              </div>

              <div v-if="esgotado" class="absolute inset-0 flex items-center justify-center"
                :style="{ background: 'rgba(0,0,0,0.45)' }">
                <span class="px-6 py-2 rounded-full text-sm font-semibold uppercase tracking-wider"
                  :style="{ background: 'var(--bg-card-solid)', color: 'var(--text)' }">Produto esgotado</span>
              </div>

              <button v-if="imagens.length > 1" @click="anterior"
                class="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full flex items-center justify-center glass hover:scale-110 transition-all"
                :style="{ color: 'var(--text)' }">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
                </svg>
              </button>
              <button v-if="imagens.length > 1" @click="proximo"
                class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full flex items-center justify-center glass hover:scale-110 transition-all"
                :style="{ color: 'var(--text)' }">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
            </div>

            <div v-if="imagens.length > 1" class="flex gap-2 px-4 py-3 overflow-x-auto"
              :style="{ background: 'var(--surface0)' }">
              <button v-for="(img, i) in imagens" :key="i" @click="imagemAtiva = i"
                class="flex-shrink-0 w-14 h-14 rounded-xl overflow-hidden border-2 transition-all duration-200"
                :style="i === imagemAtiva
                  ? { borderColor: 'var(--accent)', opacity: 1 }
                  : { borderColor: 'transparent', opacity: 0.5 }">
                <img :src="img" :alt="`Foto ${i + 1}`" class="w-full h-full object-cover" />
              </button>
            </div>
          </div>

          <div class="card-premium p-6 sm:p-8" style="animation: fadeInUp 0.4s ease 0.15s both">
            <span class="text-[11px] font-semibold uppercase tracking-[0.2em]" :style="{ color: 'var(--accent)' }">
              {{ produto.categoria }}
            </span>

            <h1 class="font-display text-2xl sm:text-3xl font-semibold leading-snug mt-2 mb-4"
              :style="{ color: 'var(--text-bright)' }">
              {{ produto.nome }}
            </h1>

            <p v-if="produto.descricao" class="text-sm leading-relaxed mb-6" :style="{ color: 'var(--text-dim)' }">
              {{ produto.descricao }}
            </p>

            <div class="flex items-center gap-3 mb-6">
              <span v-if="!esgotado" class="text-xs font-medium px-3 py-1 rounded-full"
                :style="{ background: 'var(--accent-soft)', color: 'var(--accent)' }">
                {{ produto.estoque }} disponíveis
              </span>
              <span v-else class="text-xs font-medium px-3 py-1 rounded-full"
                :style="{ background: 'rgba(var(--ctp-red), 0.1)', color: 'var(--ctp-red)' }">Esgotado</span>
            </div>

            <div class="border-t pt-6" :style="{ borderColor: 'var(--border)' }">
              <p class="text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Preço</p>
              <div class="flex items-baseline gap-3">
                <span v-if="produto.promocional && produto.preco_promocional"
                  class="font-display text-3xl sm:text-4xl font-bold"
                  :style="{ color: 'var(--ctp-red)' }">
                  R$ {{ produto.preco_promocional.toFixed(2) }}
                </span>
                <span :class="produto.promocional && produto.preco_promocional ? 'font-display text-lg line-through' : 'font-display text-3xl sm:text-4xl font-semibold gradient-text'"
                  :style="produto.promocional && produto.preco_promocional ? { color: 'var(--text-dim)' } : {}">
                  R$ {{ produto.preco.toFixed(2) }}
                </span>
                <span v-if="produto.promocional && produto.preco_promocional"
                  class="px-2 py-0.5 rounded-lg text-xs font-extrabold"
                  :style="{ background: 'var(--ctp-red)', color: 'white' }">
                  -{{ Math.round((1 - produto.preco_promocional / produto.preco) * 100) }}%
                </span>
              </div>
            </div>

            <div class="mt-6 space-y-3">
              <a :href="esgotado ? undefined : WHATSAPP_LINK" target="_blank" rel="noopener noreferrer"
                :class="esgotado ? 'opacity-50 pointer-events-none' : ''"
                class="flex items-center justify-center gap-3 w-full py-4 rounded-xl font-semibold text-base transition-all duration-200 hover:scale-[1.02]"
                :style="esgotado
                  ? { background: 'var(--surface0)', color: 'var(--text-dim)' }
                  : { background: '#25d366', color: 'white', boxShadow: '0 4px 16px rgba(37, 211, 102, 0.3)' }">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
                {{ esgotado ? 'Produto indisponível' : 'Comprar pelo WhatsApp' }}
              </a>

              <button @click="router.push('/')"
                class="btn-ghost w-full justify-center text-sm">Ver todos os produtos</button>
            </div>
          </div>
        </div>
      </div>
    </main>
    <AppFooter />
  </div>
</template>
