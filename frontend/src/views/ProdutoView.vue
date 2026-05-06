<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/services/api";
import AppHeader from "@/components/AppHeader.vue";

const route = useRoute();
const router = useRouter();

const produto = ref(null);
const carregando = ref(true);
const erro = ref(null);
const imagemAtiva = ref(0);

const imagens = computed(() => {
  if (!produto.value) return [];
  if (produto.value.imagens && produto.value.imagens.length > 0) {
    return produto.value.imagens.map((img) => img.imagem_url);
  }
  if (produto.value.imagem_url) return [produto.value.imagem_url];
  return [];
});

function anterior() {
  if (imagemAtiva.value > 0) imagemAtiva.value--;
  else imagemAtiva.value = imagens.value.length - 1;
}

function proximo() {
  if (imagemAtiva.value < imagens.value.length - 1) imagemAtiva.value++;
  else imagemAtiva.value = 0;
}

const WHATSAPP_LINK = computed(() => {
  if (!produto.value) return "#";
  const numero = "5584996997688";
  const mensagem = `Olá! Vi o produto no catálogo e tenho interesse:\n\n*${produto.value.nome}*\nValor: R$ ${produto.value.preco.toFixed(2)}\n\nPoderia me dar mais informações?`;
  return `https://wa.me/${numero}?text=${encodeURIComponent(mensagem)}`;
});

const esgotado = computed(() => !produto.value || produto.value.estoque === 0);

onMounted(async () => {
  const id = Number(route.params.id);
  if (isNaN(id)) { router.replace("/"); return; }
  try {
    produto.value = await api.buscarProduto(id);
  } catch {
    erro.value = "Produto não encontrado";
  } finally {
    carregando.value = false;
  }
});
</script>

<template>
  <div class="min-h-screen bg-blush-50">
    <AppHeader />

    <main class="max-w-3xl mx-auto px-4 sm:px-6 py-8 pb-16">

      <!-- Loading -->
      <div v-if="carregando" class="flex flex-col items-center justify-center py-32">
        <div class="w-10 h-10 border-2 border-rose-100 border-t-rose-400 rounded-full animate-spin"></div>
      </div>

      <!-- Erro -->
      <div v-else-if="erro" class="flex flex-col items-center justify-center py-32 text-center">
        <div class="w-16 h-16 bg-rose-50 rounded-2xl flex items-center justify-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <p class="font-display text-xl text-gray-400 font-light mb-6">{{ erro }}</p>
        <button
          @click="router.push('/')"
          class="bg-rose-500 text-white font-body font-medium px-6 py-2.5 rounded-full hover:bg-rose-600 transition-colors"
        >
          Voltar ao catálogo
        </button>
      </div>

      <!-- Produto -->
      <div v-else-if="produto">
        <!-- Voltar -->
        <button
          @click="router.back()"
          class="flex items-center gap-1.5 text-sm font-body text-gray-400 hover:text-rose-500 transition-colors mb-6 group"
        >
          <svg class="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          </svg>
          Voltar ao catálogo
        </button>

        <!-- Card principal -->
        <div class="bg-white rounded-2xl border border-rose-50 overflow-hidden" style="box-shadow: 0 4px 24px rgba(233,30,140,0.08)">

          <!-- Carrossel -->
          <div class="relative bg-blush-50" style="height: 340px">
            <img
              v-if="imagens.length > 0"
              :src="imagens[imagemAtiva]"
              :alt="produto.nome"
              class="w-full h-full object-contain transition-opacity duration-300"
              style="background: white"
            />
            <div v-else class="w-full h-full flex items-center justify-center bg-blush-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-16 h-16 text-rose-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
            </div>

            <!-- Overlay esgotado -->
            <div v-if="esgotado" class="absolute inset-0 bg-black/40 flex items-center justify-center">
              <span class="bg-white font-body font-semibold text-sm px-6 py-2 rounded-full uppercase tracking-wider">
                Produto esgotado
              </span>
            </div>

            <!-- Setas -->
            <button
              v-if="imagens.length > 1"
              @click="anterior"
              class="absolute left-3 top-1/2 -translate-y-1/2 w-9 h-9 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-md hover:bg-white transition-all hover:scale-105"
            >
              <svg class="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>
            <button
              v-if="imagens.length > 1"
              @click="proximo"
              class="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-md hover:bg-white transition-all hover:scale-105"
            >
              <svg class="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
              </svg>
            </button>
          </div>

          <!-- Miniaturas -->
          <div v-if="imagens.length > 1" class="flex gap-2 px-4 py-3 bg-blush-50 overflow-x-auto">
            <button
              v-for="(img, i) in imagens"
              :key="i"
              @click="imagemAtiva = i"
              :class="[
                'flex-shrink-0 w-14 h-14 rounded-xl overflow-hidden border-2 transition-all duration-200',
                i === imagemAtiva ? 'border-rose-400 shadow-sm' : 'border-transparent opacity-60 hover:opacity-100'
              ]"
            >
              <img :src="img" :alt="`Foto ${i + 1}`" class="w-full h-full object-cover" />
            </button>
          </div>

          <!-- Indicadores -->
          <div v-if="imagens.length > 1" class="flex justify-center gap-1.5 py-2 bg-blush-50">
            <button
              v-for="(_, i) in imagens"
              :key="i"
              @click="imagemAtiva = i"
              :class="[
                'rounded-full transition-all duration-200',
                i === imagemAtiva ? 'w-4 h-1.5 bg-rose-400' : 'w-1.5 h-1.5 bg-rose-200'
              ]"
            />
          </div>

          <!-- Info -->
          <div class="p-6 sm:p-8">
            <div class="flex items-start justify-between gap-4 mb-2">
              <span class="text-xs font-body font-semibold text-rose-400 uppercase tracking-widest">
                {{ produto.categoria }}
              </span>
              <span
                :class="esgotado
                  ? 'bg-red-50 text-red-500'
                  : 'bg-emerald-50 text-emerald-600'"
                class="text-xs font-body font-semibold px-3 py-1 rounded-full flex-shrink-0"
              >
                {{ esgotado ? 'Esgotado' : `${produto.estoque} disponíveis` }}
              </span>
            </div>

            <h1 class="font-display text-2xl sm:text-3xl font-semibold text-charcoal leading-snug mb-3">
              {{ produto.nome }}
            </h1>

            <p v-if="produto.descricao" class="font-body text-gray-500 text-sm leading-relaxed mb-6">
              {{ produto.descricao }}
            </p>

            <div class="border-t border-rose-50 pt-6">
              <div class="flex items-center justify-between mb-6">
                <div>
                  <p class="text-xs text-gray-400 font-body mb-0.5">Preço</p>
                  <span class="font-display text-3xl font-semibold text-rose-500">
                    R$&nbsp;{{ produto.preco.toFixed(2) }}
                  </span>
                </div>
              </div>

              <!-- Botão WhatsApp -->
              <a
                :href="esgotado ? undefined : WHATSAPP_LINK"
                target="_blank"
                rel="noopener noreferrer"
                :class="[
                  'flex items-center justify-center gap-3 w-full py-4 rounded-xl font-body font-semibold text-base transition-all duration-200',
                  esgotado
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-[#25d366] text-white hover:bg-[#1da851] hover:-translate-y-0.5 shadow-sm hover:shadow-md'
                ]"
              >
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                </svg>
                {{ esgotado ? 'Produto indisponível' : 'Comprar pelo WhatsApp' }}
              </a>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>