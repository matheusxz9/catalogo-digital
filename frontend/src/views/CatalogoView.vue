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
  <div>
    <AppHeader />

    <main class="container" style="padding-top: 2rem; padding-bottom: 3rem">
      <!-- Filtros -->
      <div v-if="store.categorias.length > 1" class="filtros">
        <button
          v-for="cat in store.categorias"
          :key="cat"
          @click="categoriaAtiva = cat"
          :class="['filtro-btn', categoriaAtiva === cat ? 'filtro-ativo' : '']"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Carregando -->
      <div v-if="store.carregando" class="grid">
        <div
          v-for="n in 8"
          :key="n"
          class="skeleton"
          style="height: 280px"
        ></div>
      </div>

      <!-- Produtos -->
      <div v-else class="grid">
        <ProdutoCard
          v-for="produto in produtosFiltrados"
          :key="produto.id"
          :produto="produto"
        />
        <div
          v-if="produtosFiltrados.length === 0"
          class="estado-central"
          style="grid-column: 1/-1"
        >
          <p>Nenhum produto encontrado nesta categoria.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.filtro-btn {
  padding: 0.4rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--cor-borda);
  background: white;
  color: var(--cor-texto-suave);
  font-size: 0.85rem;
  transition: var(--transicao);
}

.filtro-btn:hover {
  border-color: var(--cor-primaria);
  color: var(--cor-primaria);
}

.filtro-ativo {
  background: var(--cor-primaria);
  border-color: var(--cor-primaria);
  color: white !important;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

@media (min-width: 640px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 900px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
