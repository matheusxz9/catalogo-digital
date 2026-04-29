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
    return produto.value.imagens.map(img => img.imagem_url);
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
  <div>
    <AppHeader />
    <main class="container" style="padding-top: 2rem; padding-bottom: 3rem">
      <div v-if="carregando" class="estado-central"><div class="spinner"></div></div>

      <div v-else-if="erro" class="estado-central">
        <p>{{ erro }}</p>
        <button class="btn-primario" style="width:auto" @click="router.push('/')">Voltar ao catálogo</button>
      </div>

      <div v-else-if="produto" class="detalhe">
        <button class="btn-voltar" @click="router.back()">← Voltar ao catálogo</button>

        <div class="detalhe-card">
          <!-- Carrossel de imagens -->
          <div class="carrossel">
            <div class="carrossel-principal">
              <img
                v-if="imagens.length > 0"
                :src="imagens[imagemAtiva]"
                :alt="produto.nome"
                class="carrossel-img"
              />
              <div v-else class="carrossel-sem-img">📷</div>

              <div v-if="esgotado" class="detalhe-esgotado-overlay">
                <span>Produto esgotado</span>
              </div>

              <!-- Setas -->
              <button v-if="imagens.length > 1" class="seta seta-esq" @click="anterior">‹</button>
              <button v-if="imagens.length > 1" class="seta seta-dir" @click="proximo">›</button>
            </div>

            <!-- Miniaturas -->
            <div v-if="imagens.length > 1" class="miniaturas">
              <img
                v-for="(img, i) in imagens"
                :key="i"
                :src="img"
                :alt="`Foto ${i+1}`"
                class="miniatura"
                :class="{ 'miniatura-ativa': i === imagemAtiva }"
                @click="imagemAtiva = i"
              />
            </div>

            <!-- Indicadores de pontos -->
            <div v-if="imagens.length > 1" class="pontos">
              <button
                v-for="(_, i) in imagens"
                :key="i"
                class="ponto"
                :class="{ 'ponto-ativo': i === imagemAtiva }"
                @click="imagemAtiva = i"
              />
            </div>
          </div>

          <!-- Informações -->
          <div class="detalhe-info">
            <p class="detalhe-categoria">{{ produto.categoria }}</p>
            <h1 class="detalhe-nome">{{ produto.nome }}</h1>
            <p class="detalhe-descricao">{{ produto.descricao }}</p>

            <div class="detalhe-preco-linha">
              <span class="detalhe-preco">R$ {{ produto.preco.toFixed(2) }}</span>
              <span :class="esgotado ? 'badge-esgotado' : 'badge-disponivel'" class="badge">
                {{ esgotado ? "Esgotado" : `${produto.estoque} disponíveis` }}
              </span>
            </div>

            <a
              :href="esgotado ? undefined : WHATSAPP_LINK"
              target="_blank"
              rel="noopener noreferrer"
              :class="['btn-whatsapp', esgotado ? 'desabilitado' : '']"
              style="margin-top: 1.5rem"
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
              {{ esgotado ? "Produto indisponível" : "Comprar pelo WhatsApp" }}
            </a>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.btn-voltar {
  background: none;
  color: var(--cor-texto-suave);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  transition: var(--transicao);
  padding: 0;
}
.btn-voltar:hover { color: var(--cor-primaria); }

.detalhe-card {
  background: white;
  border-radius: var(--raio-borda);
  border: 1px solid var(--cor-borda);
  box-shadow: var(--sombra);
  overflow: hidden;
  max-width: 700px;
  margin: 0 auto;
}

/* Carrossel */
.carrossel { position: relative; }

.carrossel-principal {
  position: relative;
  height: 320px;
  overflow: hidden;
  background: var(--cor-fundo);
}

.carrossel-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: opacity 0.3s ease;
  background: white;

}

.carrossel-sem-img {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: var(--cor-borda);
}

.seta {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.85);
  border: none;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  font-size: 1.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transicao);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  line-height: 1;
}
.seta:hover { background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.seta-esq { left: 0.75rem; }
.seta-dir { right: 0.75rem; }

.miniaturas {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  overflow-x: auto;
  background: var(--cor-fundo);
}

.miniatura {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 6px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: var(--transicao);
  flex-shrink: 0;
}

.miniatura-ativa {
  border-color: var(--cor-primaria);
}

.pontos {
  display: flex;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 0;
  background: var(--cor-fundo);
}

.ponto {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cor-borda);
  border: none;
  cursor: pointer;
  transition: var(--transicao);
  padding: 0;
}

.ponto-ativo { background: var(--cor-primaria); }

.detalhe-esgotado-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.detalhe-esgotado-overlay span {
  background: white;
  font-weight: 700;
  padding: 0.5rem 1.5rem;
  border-radius: 999px;
}

.detalhe-info { padding: 1.5rem; }
.detalhe-categoria {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--cor-primaria);
  margin-bottom: 0.4rem;
}
.detalhe-nome { font-size: 1.6rem; font-weight: 700; color: var(--cor-texto); }
.detalhe-descricao { color: var(--cor-texto-suave); margin-top: 0.75rem; line-height: 1.7; }
.detalhe-preco-linha {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--cor-borda);
}
.detalhe-preco { font-size: 2rem; font-weight: 700; color: var(--cor-primaria); }
</style>