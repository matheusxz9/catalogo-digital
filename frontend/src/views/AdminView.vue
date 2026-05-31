<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const produtos = ref([])
const carregando = ref(true)
const erro = ref(null)
const administrador = ref(null)

const notificacoes = ref([])
function notificar(mensagem, tipo = 'sucesso') {
  const id = Date.now()
  notificacoes.value.push({ id, mensagem, tipo })
  setTimeout(() => {
    notificacoes.value = notificacoes.value.filter(n => n.id !== id)
  }, 3000)
}

const editando = ref(null)
const mostrandoForm = ref(false)
const form = ref({
  nome: '', descricao: '', preco: '', estoque: '', categoria: '',
  purchasePrice: '', profitMargin: '',
})
const editandoId = ref(null)
const arquivos = ref(null)
const enviando = ref(false)
const mobileOpen = ref(false)

const mostrarDeleteDialog = ref(false)
const deletandoId = ref(null)

const imagensAbertas = ref({})

function abrirForm(produto = null) {
  if (produto) {
    editandoId.value = produto.id
    form.value = {
      nome: produto.nome,
      descricao: produto.descricao || '',
      preco: produto.preco,
      estoque: produto.estoque,
      categoria: produto.categoria,
      purchasePrice: produto.purchasePrice ?? '',
      profitMargin: produto.profitMargin ?? '',
    }
  } else {
    editandoId.value = null
    form.value = { nome: '', descricao: '', preco: '', estoque: '', categoria: '', purchasePrice: '', profitMargin: '' }
    arquivos.value = null
  }
  mostrandoForm.value = true
  mobileOpen.value = false
}

async function salvar() {
  enviando.value = true
  try {
    const dados = {
      nome: form.value.nome,
      descricao: form.value.descricao || null,
      preco: Number(form.value.preco),
      estoque: Number(form.value.estoque) || 0,
      categoria: form.value.categoria,
      purchasePrice: form.value.purchasePrice ? Number(form.value.purchasePrice) : null,
      profitMargin: form.value.profitMargin ? Number(form.value.profitMargin) : null,
    }

    if (editandoId.value) {
      await api.atualizarProduto(editandoId.value, dados)
      if (arquivos.value?.length) {
        const fd = new FormData()
        for (const f of arquivos.value) fd.append('imagens', f)
        await api.adicionarImagens(editandoId.value, fd)
      }
      notificar('Produto atualizado com sucesso')
    } else {
      const fd = new FormData()
      Object.entries(dados).forEach(([k, v]) => fd.append(k, v))
      if (arquivos.value?.length) {
        for (const f of arquivos.value) fd.append('imagens', f)
      }
      await api.criarProduto(fd)
      notificar('Produto criado com sucesso')
    }
    mostrandoForm.value = false
    arquivos.value = null
    await carregar()
  } catch (e) {
    notificar(e.message || 'Erro ao salvar', 'erro')
  } finally {
    enviando.value = false
  }
}

function confirmarDelete(id) {
  deletandoId.value = id
  mostrarDeleteDialog.value = true
}

async function deletar() {
  try {
    await api.deletarProduto(deletandoId.value)
    notificar('Produto removido')
    await carregar()
  } catch (e) {
    notificar(e.message || 'Erro ao remover', 'erro')
  } finally {
    mostrarDeleteDialog.value = false
    deletandoId.value = null
  }
}

async function removerImagem(produtoId, imagemId) {
  try {
    await api.deletarImagem(produtoId, imagemId)
    await carregar()
    notificar('Imagem removida')
  } catch (e) {
    notificar(e.message || 'Erro ao remover imagem', 'erro')
  }
}

function logout() {
  localStorage.removeItem('token')
  router.push('/')
}

async function carregar() {
  try {
    produtos.value = await api.listarProdutos()
  } catch (e) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
}

onMounted(async () => {
  try {
    administrador.value = await api.me()
  } catch {
    logout()
    return
  }
  await carregar()
})
</script>

<template>
  <div class="min-h-screen" :style="{ background: 'var(--bg)' }">
    <AppHeader />

    <div class="max-w-6xl mx-auto px-4 sm:px-6 py-8 pb-20">

      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="font-display text-2xl font-semibold" :style="{ color: 'var(--text-bright)' }">Admin</h1>
          <p v-if="administrador" class="text-xs mt-0.5" :style="{ color: 'var(--text-dim)' }">
            {{ administrador.email }}
          </p>
        </div>
        <div class="flex gap-2">
          <button @click="abrirForm()" class="btn-primary text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 mr-1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Novo Produto
          </button>
          <button @click="logout"
            class="w-9 h-9 rounded-xl flex items-center justify-center transition-all"
            :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }"
            title="Sair">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="notificacoes.length" class="fixed top-6 right-6 z-[100] flex flex-col gap-3 max-w-sm w-full pointer-events-none px-4 sm:px-0">
        <div v-for="n in notificacoes" :key="n.id"
          class="pointer-events-auto flex items-start gap-3 rounded-xl p-4 shadow-lg border animate-fade-up"
          :style="n.tipo === 'sucesso'
            ? { background: 'var(--bg-card-solid)', borderColor: 'rgba(var(--ctp-green), 0.2)' }
            : { background: 'var(--bg-card-solid)', borderColor: 'rgba(var(--ctp-red), 0.2)' }">
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium" :style="{ color: 'var(--text)' }">{{ n.mensagem }}</p>
          </div>
        </div>
      </div>

      <transition name="scale-fade">
        <div v-if="mostrandoForm" class="glass-strong rounded-2xl p-6 sm:p-8 mb-8">
          <div class="flex items-center justify-between mb-6">
            <h2 class="font-display text-xl font-semibold" :style="{ color: 'var(--text-bright)' }">
              {{ editandoId ? 'Editar Produto' : 'Novo Produto' }}
            </h2>
            <button @click="mostrandoForm = false" class="w-8 h-8 rounded-lg flex items-center justify-center"
              :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="salvar" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Nome</label>
              <input v-model="form.nome" required class="input-field w-full" />
            </div>
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Descrição</label>
              <textarea v-model="form.descricao" rows="3" class="input-field w-full resize-none" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Preço (R$)</label>
              <input v-model="form.preco" type="number" step="0.01" min="0.01" required class="input-field w-full" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Estoque</label>
              <input v-model="form.estoque" type="number" min="0" class="input-field w-full" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Categoria</label>
              <input v-model="form.categoria" required class="input-field w-full" placeholder="Ex: Skincare" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Preço de Custo (R$)</label>
              <input v-model="form.purchasePrice" type="number" step="0.01" min="0" class="input-field w-full" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">Margem (%)</label>
              <input v-model="form.profitMargin" type="number" step="0.1" min="0" class="input-field w-full" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-dim)' }">
                {{ editandoId ? 'Adicionar Imagens' : 'Imagens' }}
              </label>
              <input type="file" multiple accept="image/*" @change="e => arquivos = e.target.files"
                class="text-xs" :style="{ color: 'var(--text-dim)' }" />
            </div>
            <div class="sm:col-span-2 flex gap-3 pt-2">
              <button type="submit" :disabled="enviando" class="btn-primary text-sm">
                {{ enviando ? 'Salvando...' : (editandoId ? 'Atualizar' : 'Criar Produto') }}
              </button>
              <button type="button" @click="mostrandoForm = false" class="btn-ghost text-sm">Cancelar</button>
            </div>
          </form>
        </div>
      </transition>

      <div v-if="carregando" class="flex justify-center py-24">
        <div class="w-10 h-10 rounded-full border-2 animate-spin-slow"
          :style="{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }"></div>
      </div>

      <div v-else-if="erro" class="text-center py-16">
        <p :style="{ color: 'var(--text-dim)' }">{{ erro }}</p>
        <button @click="carregar" class="btn-secondary mt-4">Tentar novamente</button>
      </div>

      <template v-else>

        <div class="hidden sm:block glass-strong rounded-2xl overflow-hidden">
          <table class="w-full">
            <thead>
              <tr :style="{ background: 'var(--surface0)' }">
                <th class="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider"
                  :style="{ color: 'var(--text-dim)' }">Produto</th>
                <th class="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider"
                  :style="{ color: 'var(--text-dim)' }">Categoria</th>
                <th class="px-5 py-3 text-right text-[11px] font-semibold uppercase tracking-wider"
                  :style="{ color: 'var(--text-dim)' }">Preço</th>
                <th class="px-5 py-3 text-right text-[11px] font-semibold uppercase tracking-wider"
                  :style="{ color: 'var(--text-dim)' }">Estoque</th>
                <th class="px-5 py-3 text-right text-[11px] font-semibold uppercase tracking-wider"
                  :style="{ color: 'var(--text-dim)' }">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in produtos" :key="p.id" class="border-t transition-all"
                :style="{ borderColor: 'var(--border)' }"
                @mouseenter="$event.target.style.background = 'var(--surface0)'"
                @mouseleave="$event.target.style.background = ''">
                <td class="px-5 py-3">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl overflow-hidden flex-shrink-0" :style="{ background: 'var(--surface0)' }">
                      <img v-if="p.imagem_url" :src="p.imagem_url" :alt="p.nome" class="w-full h-full object-cover" />
                      <div v-else class="w-full h-full flex items-center justify-center">
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                          :style="{ color: 'var(--text-dim)' }" stroke-width="1">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                        </svg>
                      </div>
                    </div>
                    <div>
                      <p class="text-sm font-medium" :style="{ color: 'var(--text-bright)' }">{{ p.nome }}</p>
                      <p v-if="p.descricao" class="text-xs mt-0.5 line-clamp-1" :style="{ color: 'var(--text-dim)' }">{{ p.descricao }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-3">
                  <span class="text-xs px-2.5 py-1 rounded-full"
                    :style="{ background: 'var(--accent-soft)', color: 'var(--accent)' }">{{ p.categoria }}</span>
                </td>
                <td class="px-5 py-3 text-right">
                  <span class="font-display font-semibold" :style="{ color: 'var(--text-bright)' }">R$ {{ p.preco.toFixed(2) }}</span>
                  <span v-if="p.purchasePrice" class="block text-[10px]" :style="{ color: 'var(--text-dim)' }">
                    Custo: R$ {{ p.purchasePrice.toFixed(2) }}
                  </span>
                </td>
                <td class="px-5 py-3 text-right">
                  <span class="text-sm" :style="{ color: p.estoque > 0 ? 'var(--ctp-green)' : 'var(--ctp-red)' }">{{ p.estoque }}</span>
                </td>
                <td class="px-5 py-3 text-right">
                  <div class="flex gap-2 justify-end">
                    <button @click="imagensAbertas[p.id] = !imagensAbertas[p.id]" v-if="p.imagens?.length"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all"
                      :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }"
                      title="Gerenciar imagens">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5z" />
                      </svg>
                    </button>
                    <button @click="abrirForm(p)"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all"
                      :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }"
                      title="Editar">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                      </svg>
                    </button>
                    <button @click="confirmarDelete(p.id)"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all"
                      :style="{ background: 'rgba(var(--ctp-red), 0.1)', color: 'var(--ctp-red)' }"
                      title="Excluir">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-for="p in produtos" :key="'imgs-' + p.id" v-if="imagensAbertas[p.id]">
                <td colspan="5" class="px-5 py-3" :style="{ background: 'var(--surface0)' }">
                  <div class="flex flex-wrap gap-3">
                    <div v-for="img in p.imagens" :key="img.id" class="relative group">
                      <img :src="img.imagem_url" class="w-20 h-20 object-cover rounded-xl" />
                      <button @click="removerImagem(p.id, img.id)"
                        class="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
                        :style="{ background: 'rgba(var(--ctp-red), 0.9)', color: 'white' }">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="sm:hidden space-y-3">
          <div v-for="p in produtos" :key="p.id"
            class="glass-strong rounded-2xl overflow-hidden animate-fade-up"
            :style="{ animationDelay: `${produtos.indexOf(p) * 0.05}s` }">
            <div class="flex gap-3 p-4">
              <div class="w-20 h-20 rounded-xl overflow-hidden flex-shrink-0" :style="{ background: 'var(--surface0)' }">
                <img v-if="p.imagem_url" :src="p.imagem_url" :alt="p.nome" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    :style="{ color: 'var(--text-dim)' }" stroke-width="1">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5z" />
                  </svg>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-display font-semibold text-base truncate" :style="{ color: 'var(--text-bright)' }">{{ p.nome }}</p>
                <span class="inline-block text-[10px] px-2 py-0.5 rounded-full mt-1"
                  :style="{ background: 'var(--accent-soft)', color: 'var(--accent)' }">{{ p.categoria }}</span>
                <p class="font-display text-base font-semibold mt-1 gradient-text">R$ {{ p.preco.toFixed(2) }}</p>
                <div class="flex gap-2 mt-2">
                  <button @click="abrirForm(p)" class="text-xs px-3 py-1.5 rounded-lg"
                    :style="{ background: 'var(--surface0)', color: 'var(--text)' }">Editar</button>
                  <button @click="confirmarDelete(p.id)" class="text-xs px-3 py-1.5 rounded-lg"
                    :style="{ background: 'rgba(var(--ctp-red), 0.1)', color: 'var(--ctp-red)' }">Excluir</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <Teleport to="body">
      <div v-if="mostrarDeleteDialog" class="fixed inset-0 z-[200] flex items-center justify-center px-4"
        style="background: rgba(0,0,0,0.4); backdrop-filter: blur(4px);"
        @click.self="mostrarDeleteDialog = false">
        <div class="glass-strong rounded-2xl p-6 max-w-sm w-full animate-fade-up text-center">
          <div class="w-12 h-12 rounded-2xl mx-auto mb-4 flex items-center justify-center"
            :style="{ background: 'rgba(var(--ctp-red), 0.1)' }">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"
              :style="{ color: 'var(--ctp-red)' }" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
          </div>
          <h3 class="font-display text-lg font-semibold mb-2" :style="{ color: 'var(--text-bright)' }">Excluir produto?</h3>
          <p class="text-sm mb-6" :style="{ color: 'var(--text-dim)' }">Esta ação não pode ser desfeita.</p>
          <div class="flex gap-3 justify-center">
            <button @click="mostrarDeleteDialog = false" class="btn-ghost text-sm">Cancelar</button>
            <button @click="deletar" class="px-5 py-2.5 rounded-xl text-sm font-semibold transition-all"
              :style="{ background: 'var(--ctp-red)', color: 'white' }">Excluir</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.scale-fade-enter-active,
.scale-fade-leave-active {
  transition: all 0.25s ease;
}
.scale-fade-enter-from,
.scale-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-8px);
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
