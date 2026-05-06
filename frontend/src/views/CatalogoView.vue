<script setup>
import { ref, onMounted, computed } from "vue";
import { useProdutosStore } from "@/stores/produtos";
import ProdutoCard from "@/components/ProdutoCard.vue";
import AppHeader from "@/components/AppHeader.vue";

const store = useProdutosStore();
const categoriaAtiva = ref("Todos");

const produtosFiltrados = computed(() => {
  if (categoriaAtiva.value === "Todos") return store.produtos;
  return store.produtos.filter((p) => p.categoria === categoriaAtiva.value);
});

onMounted(() => store.carregar());
</script>

<template>
  <div class="min-h-screen bg-blush-50">
    <AppHeader />

    <!-- Hero banner -->
    <div class="bg-gradient-to-br from-rose-500 via-rose-400 to-pink-400 text-white">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 py-10 sm:py-14 text-center">
        <p class="text-rose-100 font-body text-xs tracking-[0.25em] uppercase mb-3">Bem-vinda ao</p>
        <h1 class="font-display text-4xl sm:text-5xl lg:text-6xl font-light tracking-wide mb-3">
          Studio Bella Mizi
        </h1>
        <p class="font-body text-rose-100 text-sm sm:text-base max-w-md mx-auto leading-relaxed">
          Produtos de beleza selecionados com cuidado para realçar sua beleza natural
        </p>
      </div>
    </div>

    <main class="max-w-6xl mx-auto px-4 sm:px-6 py-8 pb-16">

      <!-- Filtros -->
      <div v-if="store.categorias.length > 1" class="flex flex-wrap gap-2 mb-8">
        <button
          v-for="cat in store.categorias"
          :key="cat"
          @click="categoriaAtiva = cat"
          :class="[
            'px-4 py-2 rounded-full text-sm font-body font-medium transition-all duration-200',
            categoriaAtiva === cat
              ? 'bg-rose-500 text-white shadow-sm shadow-rose-200'
              : 'bg-white text-gray-500 border border-rose-100 hover:border-rose-300 hover:text-rose-500'
          ]"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Skeletons carregando -->
      <div v-if="store.carregando" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="n in 8"
          :key="n"
          class="rounded-2xl overflow-hidden border border-rose-50"
          style="box-shadow: 0 2px 8px rgba(233,30,140,0.04)"
        >
          <div class="skeleton-shimmer" style="height: 200px"></div>
          <div class="p-4 bg-white space-y-2">
            <div class="skeleton-shimmer h-4 rounded-full w-3/4"></div>
            <div class="skeleton-shimmer h-3 rounded-full w-full"></div>
            <div class="skeleton-shimmer h-3 rounded-full w-2/3"></div>
            <div class="flex justify-between mt-3">
              <div class="skeleton-shimmer h-5 rounded-full w-16"></div>
              <div class="skeleton-shimmer h-5 rounded-full w-12"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Grade de produtos -->
      <div v-else>
        <div
          v-if="produtosFiltrados.length > 0"
          class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
        >
          <ProdutoCard
            v-for="produto in produtosFiltrados"
            :key="produto.id"
            :produto="produto"
          />
        </div>

        <div
          v-else
          class="flex flex-col items-center justify-center py-24 text-center"
        >
          <!-- Heroicon: sparkles -->
          <div class="w-16 h-16 bg-rose-50 rounded-2xl flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
            </svg>
          </div>
          <p class="font-display text-xl text-gray-400 font-light">Nenhum produto nesta categoria</p>
          <button
            @click="categoriaAtiva = 'Todos'"
            class="mt-4 text-sm text-rose-500 font-body hover:underline"
          >
            Ver todos os produtos
          </button>
        </div>
      </div>

      <!-- Erro -->
      <div v-if="store.erro" class="text-center py-16">
        <p class="text-gray-400 font-body">{{ store.erro }}</p>
      </div>

    </main>
  </div>
</template>