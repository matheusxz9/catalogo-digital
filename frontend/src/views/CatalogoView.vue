<script setup>
import { ref, onMounted, computed } from 'vue'
import { useProdutosStore } from '@/stores/produtos'
import ProdutoCard from '@/components/ProdutoCard.vue'
import AppHeader from '@/components/AppHeader.vue'

const store = useProdutosStore()
const categoriaAtiva = ref('Todos')
const busca = ref('')
const mostrarBusca = ref(false)
const favoritosVisiveis = ref(false)

const filtrados = computed(() => {
  let lista = favoritosVisiveis.value
    ? store.produtos.filter(p => favoritos.value.has(p.id))
    : store.produtos

  if (categoriaAtiva.value !== 'Todos') {
    lista = lista.filter(p => p.categoria === categoriaAtiva.value)
  }
  if (busca.value.trim()) {
    const q = busca.value.toLowerCase().trim()
    lista = lista.filter(p =>
      p.nome.toLowerCase().includes(q) ||
      p.descricao?.toLowerCase().includes(q) ||
      p.categoria.toLowerCase().includes(q)
    )
  }
  return lista
})

const favoritos = ref(new Set())

function toggleFavorito(id) {
  const f = new Set(favoritos.value)
  if (f.has(id)) f.delete(id)
  else f.add(id)
  favoritos.value = f
  localStorage.setItem('catalogo_favoritos', JSON.stringify([...f]))
}

function favoritarProduto(produto) {
  toggleFavorito(produto.id)
}

onMounted(() => {
  store.carregar()
  try {
    const saved = JSON.parse(localStorage.getItem('catalogo_favoritos') || '[]')
    favoritos.value = new Set(saved)
  } catch {}
})
</script>

<template>
  <div class="min-h-screen" :style="{ background: 'var(--bg)' }">
    <AppHeader />

    <section class="relative overflow-hidden py-16 sm:py-20"
      :style="{ background: 'linear-gradient(135deg, var(--accent-soft), transparent 60%)' }">
      <div class="absolute inset-0 opacity-[0.03]"
        style="background-image: radial-gradient(circle at 25% 25%, var(--accent) 1px, transparent 1px); background-size: 40px 40px;">
      </div>
      <div class="relative max-w-6xl mx-auto px-4 sm:px-6 text-center">
        <p class="text-xs font-semibold tracking-[0.3em] uppercase mb-4 animate-fade-up"
          :style="{ color: 'var(--text-dim)' }">Bem-vinda ao</p>
        <h1 class="font-display text-4xl sm:text-5xl lg:text-6xl font-light tracking-wide mb-3 animate-fade-up"
          :style="{ animationDelay: '0.1s' }">
          <span class="gradient-text">Studio Bella Mizi</span>
        </h1>
        <p class="text-sm sm:text-base max-w-lg mx-auto leading-relaxed animate-fade-up"
          :style="{ color: 'var(--text-dim)', animationDelay: '0.2s' }">
          Produtos selecionados com cuidado para realçar sua beleza natural
        </p>
      </div>
    </section>

    <main class="max-w-6xl mx-auto px-4 sm:px-6 py-8 pb-20">

      <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div class="flex flex-wrap items-center gap-2">
          <button v-for="cat in store.categorias" :key="cat"
            @click="categoriaAtiva = cat; favoritosVisiveis = false"
            class="px-4 py-2 rounded-full text-sm font-medium transition-all duration-200"
            :style="categoriaAtiva === cat
              ? { background: 'var(--accent-gradient)', color: 'white', boxShadow: '0 2px 8px var(--accent-glow)' }
              : { background: 'var(--bg-card-solid)', color: 'var(--text-dim)', border: '1px solid var(--border)' }">
            {{ cat }}
          </button>
          <button v-if="favoritos.size > 0" @click="favoritosVisiveis = !favoritosVisiveis"
            class="px-4 py-2 rounded-full text-sm font-medium transition-all duration-200"
            :style="favoritosVisiveis
              ? { background: 'var(--accent-gradient)', color: 'white', boxShadow: '0 2px 8px var(--accent-glow)' }
              : { background: 'var(--bg-card-solid)', color: 'var(--text-dim)', border: '1px solid var(--border)' }">
            ❤️ Favoritos ({{ favoritos.size }})
          </button>
        </div>

        <div class="flex items-center gap-2">
          <div v-if="mostrarBusca" class="animate-scale-in">
            <input v-model="busca" placeholder="Buscar produtos..." autofocus
              class="input-field w-48 sm:w-56 text-sm" />
          </div>
          <button @click="mostrarBusca = !mostrarBusca; if (!mostrarBusca) busca = ''"
            class="w-10 h-10 rounded-full flex items-center justify-center transition-all"
            :style="{ background: 'var(--accent-soft)', color: 'var(--accent)' }">
            <svg v-if="!mostrarBusca" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="store.carregando" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5">
        <div v-for="n in 8" :key="n" class="overflow-hidden rounded-2xl" :style="{ border: '1px solid var(--border)' }">
          <div class="skeleton aspect-square"></div>
          <div class="p-4 space-y-2" :style="{ background: 'var(--bg-card-solid)' }">
            <div class="skeleton h-4 w-3/4 rounded-full"></div>
            <div class="skeleton h-3 w-full rounded-full"></div>
            <div class="skeleton h-3 w-2/3 rounded-full"></div>
            <div class="flex justify-between mt-3 pt-3" :style="{ borderTop: '1px solid var(--border)' }">
              <div class="skeleton h-5 w-16 rounded-full"></div>
              <div class="skeleton h-5 w-12 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="filtrados.length > 0"
        class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5 stagger-enter">
        <ProdutoCard v-for="(produto, idx) in filtrados" :key="produto.id" :produto="produto" :index="idx"
          @favoritar="favoritarProduto(produto)" />
      </div>

      <div v-else class="flex flex-col items-center justify-center py-24 text-center animate-fade-up">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
          :style="{ background: 'var(--accent-soft)' }">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            :style="{ color: 'var(--accent)' }" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
          </svg>
        </div>
        <p class="font-display text-xl font-light" :style="{ color: 'var(--text-dim)' }">
          {{ busca ? 'Nenhum resultado para "' + busca + '"' : 'Nenhum produto encontrado' }}
        </p>
        <button v-if="busca" @click="busca = ''"
          class="btn-ghost mt-3">Limpar busca</button>
      </div>

      <div v-if="store.erro" class="text-center py-16">
        <p :style="{ color: 'var(--text-dim)' }">{{ store.erro }}</p>
        <button @click="store.carregar()" class="btn-secondary mt-4">Tentar novamente</button>
      </div>

    </main>
  </div>
</template>
