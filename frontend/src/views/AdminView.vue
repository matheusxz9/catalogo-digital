<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/services/api";
import AppHeader from "@/components/AppHeader.vue";

const router = useRouter();
const produtos = ref([]);
const carregando = ref(false);
const erro = ref(null);
const sucesso = ref(null);
const mostrarFormulario = ref(false);
const salvando = ref(false);
const editandoId = ref(null);
const produtoEditando = ref(null);

const formInicial = { nome: "", categoria: "", descricao: "", preco: "", estoque: 0 };
const form = ref({ ...formInicial });
const imagensSelecionadas = ref([]);

function sair() {
  localStorage.removeItem("token");
  router.push({ name: "adminLogin" });
}

function irParaCatalogo() {
  router.push({ name: "Catalogo" });
}

async function carregarProdutos() {
  carregando.value = true;
  erro.value = null;
  try {
    produtos.value = await api.listarProdutos();
  } catch (e) {
    erro.value = "Não foi possível carregar os produtos.";
  } finally {
    carregando.value = false;
  }
}

onMounted(() => carregarProdutos());

function abrirNovo() {
  editandoId.value = null;
  produtoEditando.value = null;
  form.value = { ...formInicial };
  imagensSelecionadas.value = [];
  mostrarFormulario.value = true;
}

function abrirEdicao(produto) {
  editandoId.value = produto.id;
  produtoEditando.value = produto;
  form.value = {
    nome: produto.nome,
    categoria: produto.categoria,
    descricao: produto.descricao || "",
    preco: produto.preco,
    estoque: produto.estoque,
  };
  imagensSelecionadas.value = [];
  mostrarFormulario.value = true;
}

function fecharFormulario() {
  mostrarFormulario.value = false;
  editandoId.value = null;
  produtoEditando.value = null;
  form.value = { ...formInicial };
  imagensSelecionadas.value = [];
  erro.value = null;
}

function onImagensSelecionadas(e) {
  const arquivos = Array.from(e.target.files);
  const restantes = 4 - imagensSelecionadas.value.length;
  arquivos.slice(0, restantes).forEach((arquivo) => {
    imagensSelecionadas.value.push({ file: arquivo, preview: URL.createObjectURL(arquivo) });
  });
  e.target.value = "";
}

function removerImagem(index) {
  imagensSelecionadas.value.splice(index, 1);
}

function mostrarSucesso(msg) {
  sucesso.value = msg;
  setTimeout(() => (sucesso.value = null), 3000);
}

async function salvar() {
  salvando.value = true;
  erro.value = null;
  try {
    if (editandoId.value) {
      await api.atualizarProduto(editandoId.value, {
        nome: form.value.nome,
        categoria: form.value.categoria,
        descricao: form.value.descricao,
        preco: parseFloat(form.value.preco),
        estoque: parseInt(form.value.estoque),
      });
      if (imagensSelecionadas.value.length > 0) {
        const fd = new FormData();
        imagensSelecionadas.value.forEach((img) => fd.append("imagens", img.file));
        await api.adicionarImagens(editandoId.value, fd);
      }
      mostrarSucesso("Produto atualizado com sucesso!");
    } else {
      const fd = new FormData();
      fd.append("nome", form.value.nome);
      fd.append("categoria", form.value.categoria);
      fd.append("descricao", form.value.descricao || "");
      fd.append("preco", parseFloat(form.value.preco));
      fd.append("estoque", parseInt(form.value.estoque));
      imagensSelecionadas.value.forEach((img) => fd.append("imagens", img.file));
      await api.criarProduto(fd);
      mostrarSucesso("Produto criado com sucesso!");
    }
    fecharFormulario();
    await carregarProdutos();
  } catch (e) {
    erro.value = e.message || "Erro ao salvar produto.";
  } finally {
    salvando.value = false;
  }
}

async function deletarImagemExistente(produto, imagemId) {
  if (!confirm("Deletar esta imagem?")) return;
  try {
    await api.deletarImagem(produto.id, imagemId);
    mostrarSucesso("Imagem removida!");
    await carregarProdutos();
    if (produtoEditando.value) {
      produtoEditando.value = produtos.value.find((p) => p.id === produto.id) || null;
    }
  } catch (e) {
    erro.value = e.message || "Erro ao deletar imagem.";
  }
}

async function deletar(produto) {
  if (!confirm(`Deletar "${produto.nome}"?`)) return;
  try {
    await api.deletarProduto(produto.id);
    mostrarSucesso("Produto removido!");
    await carregarProdutos();
  } catch (e) {
    erro.value = e.message || "Erro ao deletar produto.";
  }
}
</script>

<template>
  <div class="min-h-screen bg-blush-50">
    <AppHeader />

    <main class="max-w-6xl mx-auto px-4 sm:px-6 py-8 pb-16">

      <!-- Header do painel -->
      <div class="flex items-center justify-between mb-8 flex-wrap gap-3">
        <div>
          <h1 class="font-display text-3xl font-semibold text-charcoal">Painel Admin</h1>
          <p class="text-sm font-body text-gray-400 mt-0.5">Gerencie os produtos do catálogo</p>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <button
            @click="irParaCatalogo"
            class="flex items-center gap-1.5 text-sm font-body font-medium text-gray-500 border border-rose-100 hover:border-rose-300 hover:text-rose-500 px-4 py-2 rounded-full transition-all"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
            </svg>
            Catálogo
          </button>
          <button
            @click="abrirNovo"
            class="flex items-center gap-1.5 text-sm font-body font-semibold bg-rose-500 hover:bg-rose-600 text-white px-5 py-2 rounded-full transition-all hover:-translate-y-0.5"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            Novo produto
          </button>
          <button
            @click="sair"
            class="text-sm font-body text-gray-400 border border-gray-200 hover:border-red-200 hover:text-red-500 px-4 py-2 rounded-full transition-all"
          >
            Sair
          </button>
        </div>
      </div>

      <!-- Alertas -->
      <transition name="fade">
        <div
          v-if="sucesso"
          class="flex items-center gap-2 bg-emerald-50 border border-emerald-100 text-emerald-700 text-sm font-body font-medium px-4 py-3 rounded-xl mb-6"
        >
          <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          {{ sucesso }}
        </div>
      </transition>

      <div v-if="erro && !mostrarFormulario" class="bg-red-50 border border-red-100 text-red-600 text-sm font-body px-4 py-3 rounded-xl mb-6">
        {{ erro }}
      </div>

      <!-- Loading -->
      <div v-if="carregando" class="flex justify-center py-24">
        <div class="w-10 h-10 border-2 border-rose-100 border-t-rose-400 rounded-full animate-spin"></div>
      </div>

      <!-- Tabela desktop -->
      <div v-else-if="produtos.length > 0">
        <div class="hidden sm:block bg-white rounded-2xl border border-rose-50 overflow-hidden" style="box-shadow: 0 2px 12px rgba(233,30,140,0.05)">
          <table class="w-full">
            <thead>
              <tr class="bg-rose-50 border-b border-rose-100">
                <th class="text-left text-xs font-body font-semibold text-rose-400 uppercase tracking-widest px-5 py-3.5">Foto</th>
                <th class="text-left text-xs font-body font-semibold text-rose-400 uppercase tracking-widest px-5 py-3.5">Produto</th>
                <th class="text-left text-xs font-body font-semibold text-rose-400 uppercase tracking-widest px-5 py-3.5 hidden md:table-cell">Categoria</th>
                <th class="text-left text-xs font-body font-semibold text-rose-400 uppercase tracking-widest px-5 py-3.5">Preço</th>
                <th class="text-left text-xs font-body font-semibold text-rose-400 uppercase tracking-widest px-5 py-3.5 hidden lg:table-cell">Estoque</th>
                <th class="text-left text-xs font-body font-semibold text-rose-400 uppercase tracking-widest px-5 py-3.5">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="p in produtos"
                :key="p.id"
                class="border-b border-rose-50 last:border-0 hover:bg-blush-50 transition-colors"
              >
                <td class="px-5 py-3">
                  <div class="flex gap-1">
                    <template v-if="p.imagens && p.imagens.length > 0">
                      <img
                        v-for="img in p.imagens.slice(0, 3)"
                        :key="img.id"
                        :src="img.imagem_url"
                        :alt="p.nome"
                        class="w-10 h-10 object-cover rounded-lg border border-rose-50"
                      />
                    </template>
                    <img v-else-if="p.imagem_url" :src="p.imagem_url" :alt="p.nome" class="w-10 h-10 object-cover rounded-lg border border-rose-50" />
                    <div v-else class="w-10 h-10 bg-blush-100 rounded-lg flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                      </svg>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-3">
                  <span class="font-body font-semibold text-charcoal text-sm">{{ p.nome }}</span>
                </td>
                <td class="px-5 py-3 hidden md:table-cell">
                  <span class="text-xs font-body text-rose-400 bg-rose-50 px-2.5 py-1 rounded-full">{{ p.categoria }}</span>
                </td>
                <td class="px-5 py-3">
                  <span class="font-display font-semibold text-rose-500">R$ {{ p.preco.toFixed(2) }}</span>
                </td>
                <td class="px-5 py-3 hidden lg:table-cell">
                  <span
                    :class="p.estoque > 0 ? 'text-emerald-600 bg-emerald-50' : 'text-red-500 bg-red-50'"
                    class="text-xs font-body font-semibold px-2.5 py-1 rounded-full"
                  >
                    {{ p.estoque }} un.
                  </span>
                </td>
                <td class="px-5 py-3">
                  <div class="flex gap-2">
                    <button
                      @click="abrirEdicao(p)"
                      class="text-xs font-body font-semibold text-rose-500 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-full transition-colors"
                    >
                      Editar
                    </button>
                    <button
                      @click="deletar(p)"
                      class="text-xs font-body font-semibold text-red-500 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-full transition-colors"
                    >
                      Deletar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Cards mobile -->
        <div class="sm:hidden space-y-3">
          <div
            v-for="p in produtos"
            :key="p.id"
            class="bg-white rounded-2xl border border-rose-50 overflow-hidden"
            style="box-shadow: 0 2px 8px rgba(233,30,140,0.05)"
          >
            <div class="flex gap-3 p-4">
              <img
                v-if="p.imagem_url || (p.imagens && p.imagens.length > 0)"
                :src="p.imagens && p.imagens.length > 0 ? p.imagens[0].imagem_url : p.imagem_url"
                :alt="p.nome"
                class="w-20 h-20 object-cover rounded-xl border border-rose-50 flex-shrink-0"
              />
              <div v-else class="w-20 h-20 bg-blush-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-body text-rose-400 uppercase tracking-wider mb-0.5">{{ p.categoria }}</p>
                <p class="font-body font-semibold text-charcoal text-sm leading-snug truncate">{{ p.nome }}</p>
                <p class="font-display text-rose-500 font-semibold text-base mt-1">R$ {{ p.preco.toFixed(2) }}</p>
                <p class="text-xs text-gray-400 font-body">{{ p.estoque }} em estoque</p>
              </div>
            </div>
            <div class="flex gap-2 px-4 pb-4">
              <button @click="abrirEdicao(p)" class="flex-1 flex items-center justify-center gap-1.5 text-sm font-body font-semibold text-rose-500 bg-rose-50 hover:bg-rose-100 py-2 rounded-full transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                </svg>
                Editar
              </button>
              <button @click="deletar(p)" class="flex-1 flex items-center justify-center gap-1.5 text-sm font-body font-semibold text-red-500 bg-red-50 hover:bg-red-100 py-2 rounded-full transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
                Deletar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="flex flex-col items-center justify-center py-24 text-center">
        <div class="w-16 h-16 bg-rose-50 rounded-2xl flex items-center justify-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-rose-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
          </svg>
        </div>
        <p class="font-display text-xl text-gray-400 font-light mb-6">Nenhum produto cadastrado</p>
        <button
          @click="abrirNovo"
          class="bg-rose-500 hover:bg-rose-600 text-white font-body font-semibold px-6 py-2.5 rounded-full transition-all hover:-translate-y-0.5"
        >
          + Criar primeiro produto
        </button>
      </div>

    </main>

    <!-- MODAL -->
    <transition name="modal">
      <div
        v-if="mostrarFormulario"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
        @click.self="fecharFormulario"
      >
        <div class="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-2xl max-h-[92vh] flex flex-col" style="box-shadow: 0 24px 64px rgba(0,0,0,0.18)">

          <!-- Modal header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-rose-50 flex-shrink-0">
            <h2 class="font-display text-xl font-semibold text-charcoal">
              {{ editandoId ? 'Editar produto' : 'Novo produto' }}
            </h2>
            <button
              @click="fecharFormulario"
              class="w-8 h-8 flex items-center justify-center rounded-full text-gray-400 hover:bg-rose-50 hover:text-rose-500 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Modal body -->
          <div class="overflow-y-auto flex-1 px-6 py-5 space-y-5">

            <div v-if="erro" class="bg-red-50 border border-red-100 text-red-600 text-sm font-body px-4 py-3 rounded-xl">
              {{ erro }}
            </div>

            <!-- Imagens existentes -->
            <div v-if="editandoId && produtoEditando && produtoEditando.imagens && produtoEditando.imagens.length > 0">
              <label class="block text-xs font-body font-semibold text-gray-600 mb-2 tracking-wide">Imagens atuais</label>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="img in produtoEditando.imagens"
                  :key="img.id"
                  class="relative"
                >
                  <img :src="img.imagem_url" class="w-20 h-20 object-cover rounded-xl border border-rose-100" />
                  <button
                    @click="deletarImagemExistente(produtoEditando, img.id)"
                    class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Upload de imagens -->
            <div>
              <label class="block text-xs font-body font-semibold text-gray-600 mb-2 tracking-wide">
                {{ editandoId ? 'Adicionar imagens' : 'Imagens' }}
                <span class="text-gray-400 font-normal">(até {{ 4 - imagensSelecionadas.length }} foto{{ 4 - imagensSelecionadas.length !== 1 ? 's' : '' }})</span>
              </label>

              <!-- Previews -->
              <div v-if="imagensSelecionadas.length > 0" class="flex flex-wrap gap-2 mb-3">
                <div v-for="(img, i) in imagensSelecionadas" :key="i" class="relative">
                  <img :src="img.preview" class="w-20 h-20 object-cover rounded-xl border-2 border-rose-300" />
                  <button
                    @click="removerImagem(i)"
                    class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                  <span
                    v-if="i === 0"
                    class="absolute bottom-1 left-1 text-xs bg-rose-500 text-white px-1.5 py-0.5 rounded font-body font-semibold leading-none"
                  >
                    Principal
                  </span>
                </div>
              </div>

              <label
                v-if="imagensSelecionadas.length < 4"
                class="flex items-center gap-2 cursor-pointer bg-blush-50 border-2 border-dashed border-rose-200 hover:border-rose-400 hover:bg-rose-50 rounded-xl px-4 py-3 transition-all w-fit"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
                </svg>
                <span class="text-sm font-body font-medium text-gray-500">Selecionar fotos</span>
                <input type="file" accept="image/*" multiple @change="onImagensSelecionadas" class="hidden" />
              </label>
            </div>

            <!-- Nome -->
            <div>
              <label class="block text-xs font-body font-semibold text-gray-600 mb-1.5 tracking-wide">
                Nome <span class="text-red-400">*</span>
              </label>
              <input
                v-model="form.nome"
                type="text"
                placeholder="Nome do produto"
                class="w-full border border-rose-100 rounded-xl px-4 py-2.5 text-sm font-body text-charcoal placeholder-gray-300 focus:border-rose-300 focus:ring-2 focus:ring-rose-100 transition-all"
              />
            </div>

            <!-- Categoria -->
            <div>
              <label class="block text-xs font-body font-semibold text-gray-600 mb-1.5 tracking-wide">
                Categoria <span class="text-red-400">*</span>
              </label>
              <input
                v-model="form.categoria"
                type="text"
                placeholder="Ex: Tratamento Capilar"
                class="w-full border border-rose-100 rounded-xl px-4 py-2.5 text-sm font-body text-charcoal placeholder-gray-300 focus:border-rose-300 focus:ring-2 focus:ring-rose-100 transition-all"
              />
            </div>

            <!-- Descrição -->
            <div>
              <label class="block text-xs font-body font-semibold text-gray-600 mb-1.5 tracking-wide">Descrição</label>
              <textarea
                v-model="form.descricao"
                rows="3"
                placeholder="Descreva o produto..."
                class="w-full border border-rose-100 rounded-xl px-4 py-2.5 text-sm font-body text-charcoal placeholder-gray-300 focus:border-rose-300 focus:ring-2 focus:ring-rose-100 transition-all resize-none"
              ></textarea>
            </div>

            <!-- Preço + Estoque -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-body font-semibold text-gray-600 mb-1.5 tracking-wide">
                  Preço (R$) <span class="text-red-400">*</span>
                </label>
                <input
                  v-model="form.preco"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0,00"
                  class="w-full border border-rose-100 rounded-xl px-4 py-2.5 text-sm font-body text-charcoal placeholder-gray-300 focus:border-rose-300 focus:ring-2 focus:ring-rose-100 transition-all"
                />
              </div>
              <div>
                <label class="block text-xs font-body font-semibold text-gray-600 mb-1.5 tracking-wide">
                  Estoque <span class="text-red-400">*</span>
                </label>
                <input
                  v-model="form.estoque"
                  type="number"
                  min="0"
                  placeholder="0"
                  class="w-full border border-rose-100 rounded-xl px-4 py-2.5 text-sm font-body text-charcoal placeholder-gray-300 focus:border-rose-300 focus:ring-2 focus:ring-rose-100 transition-all"
                />
              </div>
            </div>

          </div>

          <!-- Modal footer -->
          <div class="flex gap-3 px-6 py-4 border-t border-rose-50 flex-shrink-0">
            <button
              @click="fecharFormulario"
              class="flex-1 text-sm font-body font-medium text-gray-500 border border-gray-200 hover:border-gray-300 py-3 rounded-xl transition-all"
            >
              Cancelar
            </button>
            <button
              :disabled="salvando"
              @click="salvar"
              class="flex-1 text-sm font-body font-semibold bg-rose-500 hover:bg-rose-600 disabled:bg-rose-200 text-white py-3 rounded-xl transition-all disabled:cursor-not-allowed"
            >
              {{ salvando ? 'Salvando...' : editandoId ? 'Salvar alterações' : 'Criar produto' }}
            </button>
          </div>

        </div>
      </div>
    </transition>

  </div>
</template>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .bg-white, .modal-leave-active .bg-white { transition: transform 0.3s ease; }
.modal-enter-from .bg-white { transform: translateY(20px); }
.modal-leave-to .bg-white { transform: translateY(20px); }
</style>