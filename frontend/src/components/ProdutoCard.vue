<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const props = defineProps({
  produto: { type: Object, required: true },
})
const emit = defineEmits(['favoritar'])
const router = useRouter()

const estoqueBaixo = computed(() => props.produto.estoque > 0 && props.produto.estoque <= 3)
const esgotado = computed(() => props.produto.estoque === 0)

function irParaProduto() {
  api.visualizarProduto(props.produto.id).catch(() => {})
  router.push({ name: 'Produto', params: { id: props.produto.id } })
}
</script>

<template>
  <div class="card-premium group cursor-pointer" @click="irParaProduto">
    <div class="relative overflow-hidden" :style="{ background: 'var(--bg)' }">
      <div class="aspect-square overflow-hidden rounded-xl">
        <img
          v-if="produto.imagem_url"
          :src="produto.imagem_url"
          :alt="produto.nome"
          class="w-full h-full object-contain p-4 transition-all duration-500 group-hover:scale-110"
          :style="{ background: 'var(--bg-card-solid)' }"
          loading="lazy"
        />
        <div v-else class="w-full h-full flex items-center justify-center" :style="{ background: 'var(--accent-soft)' }">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            :style="{ color: 'var(--accent)' }" stroke-width="1">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
          </svg>
        </div>
      </div>

      <button
        @click.stop="emit('favoritar')"
        class="absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 opacity-0 group-hover:opacity-100 hover:scale-110 glass"
        :style="{ color: 'var(--accent)' }"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
      </button>

      <div v-if="esgotado" class="absolute inset-x-0 top-0 flex justify-center pt-3">
        <span class="px-3 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider glass"
          :style="{ color: 'var(--ctp-red)' }">Esgotado</span>
      </div>
    </div>

    <div class="p-3 sm:p-4" :style="{ background: 'var(--bg-card-solid)' }">
      <p class="font-display font-semibold text-sm sm:text-base truncate" :style="{ color: 'var(--text-bright)' }">
        {{ produto.nome }}
      </p>
      <p v-if="produto.descricao" class="text-xs mt-0.5 line-clamp-2 leading-relaxed" :style="{ color: 'var(--text-dim)' }">
        {{ produto.descricao }}
      </p>

      <div class="flex items-center justify-between mt-2.5 pt-2.5" :style="{ borderTop: '1px solid var(--border)' }">
        <span class="font-display text-base sm:text-lg font-semibold gradient-text">
          R$ {{ produto.preco.toFixed(2) }}
        </span>
        <span v-if="estoqueBaixo" class="text-[10px] font-medium" :style="{ color: 'var(--ctp-yellow)' }">
          Apenas {{ produto.estoque }}
        </span>
      </div>
    </div>
  </div>
</template>
