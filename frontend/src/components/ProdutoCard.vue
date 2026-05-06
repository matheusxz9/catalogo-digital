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
  <article
    class="bg-white rounded-2xl border border-rose-50 card-hover cursor-pointer overflow-hidden group"
    style="box-shadow: 0 2px 12px rgba(233,30,140,0.06), 0 1px 3px rgba(0,0,0,0.05)"
    @click="abrirDetalhe"
  >
    <!-- Image wrapper -->
    <div class="relative overflow-hidden bg-blush-50" style="height: 200px">
      <img
        v-if="produto.imagem_url"
        :src="produto.imagem_url"
        :alt="produto.nome"
        class="w-full h-full object-contain img-zoom"
        style="background: white"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center bg-blush-100"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 text-rose-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
        </svg>
      </div>

      <!-- Esgotado overlay -->
      <div
        v-if="produto.estoque === 0"
        class="absolute inset-0 bg-black/40 flex items-center justify-center"
      >
        <span class="bg-white text-charcoal font-body font-semibold text-xs px-4 py-1.5 rounded-full tracking-wider uppercase">
          Esgotado
        </span>
      </div>

      <!-- Category badge -->
      <div class="absolute top-3 left-3">
        <span class="bg-white/90 backdrop-blur-sm text-rose-500 text-xs font-body font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider shadow-sm">
          {{ produto.categoria }}
        </span>
      </div>
    </div>

    <!-- Body -->
    <div class="p-4">
      <h3 class="font-display font-semibold text-charcoal text-base leading-snug line-clamp-2 mb-1">
        {{ produto.nome }}
      </h3>
      <p
        v-if="produto.descricao"
        class="text-xs text-gray-400 font-body line-clamp-2 mb-3 leading-relaxed"
      >
        {{ produto.descricao }}
      </p>

      <!-- Footer -->
      <div class="flex items-center justify-between mt-auto pt-2 border-t border-rose-50">
        <span class="font-display text-rose-500 font-semibold text-lg">
          R$&nbsp;{{ produto.preco.toFixed(2) }}
        </span>
        <span
          :class="produto.estoque > 0
            ? 'bg-emerald-50 text-emerald-600'
            : 'bg-red-50 text-red-500'"
          class="text-xs font-body font-semibold px-2.5 py-1 rounded-full"
        >
          {{ produto.estoque > 0 ? `${produto.estoque} un.` : 'Esgotado' }}
        </span>
      </div>
    </div>
  </article>
</template>