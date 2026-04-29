<script setup>
import { useRouter } from "vue-router";

const props = defineProps({
  produto: { type: Object, required: true },
});

const router = useRouter();

function abrirDetalhe() {
  router.push({ name: "produto", params: { id: props.produto.id } });
}
</script>

<template>
  <article class="card" @click="abrirDetalhe">
    <div class="card-imagem-wrapper">
      <img :src="produto.imagem_url" :alt="produto.nome" class="card-imagem" />
      <div v-if="produto.estoque === 0" class="card-esgotado-overlay">
        <span>Esgotado</span>
      </div>
    </div>
    <div class="card-corpo">
      <p class="card-categoria">{{ produto.categoria }}</p>
      <h3 class="card-nome">{{ produto.nome }}</h3>
      <p class="card-descricao">{{ produto.descricao }}</p>

      <div class="card-rodape">
        <span class="card-preco">R$ {{ produto.preco.toFixed(2) }}</span>
        <span
          :class="produto.estoque > 0 ? 'badge-disponivel' : 'badge-esgotado'"
          class="badge"
        >
          
          {{ produto.estoque > 0 ? `${produto.estoque} un.` : "Esgotado" }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  background: white;
  border-radius: var(--raio-borda);
  border: 1px solid var(--cor-borda);
  box-shadow: var(--sombra);
  cursor: pointer;
  transition: var(--transicao);
  overflow: hidden;
}

.card:hover {
  box-shadow: var(--sombra-hover);
  transform: translateY(-4px);
}

.card-imagem-wrapper {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-imagem {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
  background: white;
}

.card:hover .card-imagem {
  transform: scale(1.05);
}

.card-esgotado-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-esgotado-overlay span {
  background: white;
  color: var(--cor-texto);
  font-weight: 600;
  padding: 0.4rem 1rem;
  border-radius: 999px;
  font-size: 0.85rem;
}

.card-corpo {
  padding: 1rem;
}

.card-categoria {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--cor-primaria);
  margin-bottom: 0.3rem;
}

.card-nome {
  font-size: 1rem;
  font-weight: 600;
  color: var(--cor-texto);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-descricao {
  font-size: 0.85rem;
  color: var(--cor-texto-suave);
  margin-top: 0.3rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-rodape {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.75rem;
}

.card-preco {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--cor-primaria);
}
</style>
