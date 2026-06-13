<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'
import { useTemaStore } from '@/stores/tema'

const router = useRouter()
const tema = useTemaStore()

const aba = ref('dashboard')

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
  }, 3500)
}

const editandoId = ref(null)
const mostrandoForm = ref(false)
const form = ref({
  nome: '', descricao: '', preco: '', estoque: '', categoria: '',
  purchasePrice: '', profitMargin: '',
  promocional: false, preco_promocional: '',
})
const arquivos = ref(null)
const enviando = ref(false)

const mostrarDeleteDialog = ref(false)
const deletandoId = ref(null)

const sidebarAberta = ref(false)

const buscaAdmin = ref('')
const filtroCategoria = ref('')
const filtroAtivo = ref('todos')

const categoriasAdmin = computed(() => {
  const cats = [...new Set(produtos.value.map(p => p.categoria))]
  return cats.sort()
})

const produtosFiltrados = computed(() => {
  let lista = produtos.value
  if (filtroAtivo.value === 'ativos') {
    lista = lista.filter(p => p.ativo)
  } else if (filtroAtivo.value === 'inativos') {
    lista = lista.filter(p => !p.ativo)
  }
  if (filtroCategoria.value) {
    lista = lista.filter(p => p.categoria === filtroCategoria.value)
  }
  if (buscaAdmin.value.trim()) {
    const q = buscaAdmin.value.toLowerCase().trim()
    lista = lista.filter(p =>
      p.nome.toLowerCase().includes(q) ||
      p.descricao?.toLowerCase().includes(q) ||
      p.categoria.toLowerCase().includes(q)
    )
  }
  return lista
})

const stats = computed(() => {
  if (!produtos.value.length) return []
  const ativos = produtos.value.filter(p => p.ativo)
  const total = ativos.length
  const valorTotal = ativos.reduce((s, p) => s + p.preco * p.estoque, 0)
  const custoTotal = ativos.reduce((s, p) => s + (p.purchasePrice || 0) * p.estoque, 0)
  const margemMedia = ativos.reduce((s, p) => {
    if (p.purchasePrice && p.preco > p.purchasePrice) {
      return s + ((p.preco - p.purchasePrice) / p.preco * 100)
    }
    return s
  }, 0) / ativos.filter(p => p.purchasePrice).length || 0
  const totalViews = produtos.value.reduce((s, p) => s + (p.visualizacoes || 0), 0)
  return [
    { label: 'Produtos Ativos', valor: total, icone: 'package', cor: 'mauve' },
    { label: 'Valor em Estoque', valor: `R$ ${valorTotal.toFixed(2)}`, icone: 'currency-dollar', cor: 'green' },
    { label: 'Visualizações', valor: totalViews, icone: 'eye', cor: 'sky' },
    { label: 'Margem Média', valor: `${margemMedia.toFixed(1)}%`, icone: 'chart-bar', cor: 'peach' },
  ]
})

const produtosPorCategoria = computed(() => {
  const ativos = produtos.value.filter(p => p.ativo)
  const map = {}
  ativos.forEach(p => { map[p.categoria] = (map[p.categoria] || 0) + 1 })
  return Object.entries(map).sort((a, b) => b[1] - a[1])
})

const produtosFinanceiro = computed(() => {
  return produtos.value
    .filter(p => p.ativo && p.purchasePrice)
    .map(p => ({
      ...p,
      lucroUni: p.preco - p.purchasePrice,
      margemReal: ((p.preco - p.purchasePrice) / p.preco * 100).toFixed(1),
    }))
    .sort((a, b) => b.lucroUni - a.lucroUni)
})

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
      promocional: produto.promocional || false,
      preco_promocional: produto.preco_promocional ?? '',
    }
  } else {
    editandoId.value = null
    form.value = { nome: '', descricao: '', preco: '', estoque: '', categoria: '', purchasePrice: '', profitMargin: '', promocional: false, preco_promocional: '' }
    arquivos.value = null
  }
  mostrandoForm.value = true
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
      promocional: form.value.promocional,
      preco_promocional: form.value.preco_promocional ? Number(form.value.preco_promocional) : null,
    }
    if (editandoId.value) {
      await api.atualizarProduto(editandoId.value, dados)
      if (arquivos.value?.length) {
        const fd = new FormData()
        for (const f of arquivos.value) fd.append('imagens', f)
        await api.adicionarImagens(editandoId.value, fd)
      }
      notificar('Produto atualizado')
    } else {
      const fd = new FormData()
      Object.entries(dados).forEach(([k, v]) => {
        if (v === null || v === undefined) return
        if (k === 'promocional' && v === false) return
        fd.append(k, v)
      })
      if (arquivos.value?.length) {
        for (const f of arquivos.value) fd.append('imagens', f)
      }
      await api.criarProduto(fd)
      notificar('Produto criado')
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

async function duplicar(id) {
  try {
    await api.duplicarProduto(id)
    notificar('Produto duplicado')
    await carregar()
  } catch (e) {
    notificar(e.message || 'Erro ao duplicar', 'erro')
  }
}

async function toggleAtivo(id) {
  try {
    const p = await api.toggleAtivo(id)
    notificar(p.ativo ? 'Produto ativado' : 'Produto desativado')
    await carregar()
  } catch (e) {
    notificar(e.message || 'Erro ao alterar status', 'erro')
  }
}

async function togglePromocional(id) {
  try {
    const p = await api.togglePromocional(id)
    notificar(p.promocional ? 'Produto marcado como promocional' : 'Promoção removida')
    await carregar()
  } catch (e) {
    notificar(e.message || 'Erro ao alterar promoção', 'erro')
  }
}

function logout() {
  localStorage.removeItem('token')
  router.push('/')
}

async function carregar() {
  try {
    produtos.value = await api.listarProdutosAdmin()
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
  <div class="min-h-screen flex" :style="{ background: 'var(--bg)' }">
    <Teleport to="body">
      <div v-if="sidebarAberta" class="fixed inset-0 z-40 lg:hidden"
        style="background: rgba(0,0,0,0.3);" @click="sidebarAberta = false"></div>
    </Teleport>

    <aside class="fixed lg:sticky top-0 left-0 z-50 h-full w-64 flex-shrink-0 transition-transform duration-300 lg:translate-x-0"
      :class="sidebarAberta ? 'translate-x-0' : '-translate-x-full'"
      :style="{ background: 'var(--bg-card-solid)', borderRight: '1px solid var(--border)' }">
      <div class="flex flex-col h-full">
        <div class="p-5 border-b flex items-center justify-between" :style="{ borderColor: 'var(--border)' }">
          <div class="flex items-center gap-2.5">
            <img src="/logo.svg" alt="Studio Bella Mizi" class="w-8 h-8 rounded-lg" />
            <div>
              <p class="font-display text-sm font-semibold leading-tight" :style="{ color: 'var(--text-bright)' }">Admin</p>
              <p class="text-[10px] leading-tight" :style="{ color: 'var(--text-dim)' }">Studio Bella Mizi</p>
            </div>
          </div>
          <button @click="sidebarAberta = false" class="lg:hidden w-7 h-7 rounded-lg flex items-center justify-center"
            :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav class="flex-1 p-3 space-y-1 overflow-y-auto">
          <button v-for="item in [
            { id: 'dashboard', label: 'Dashboard', icone: 'home' },
            { id: 'produtos', label: 'Produtos', icone: 'package' },
            { id: 'financeiro', label: 'Financeiro', icone: 'currency-dollar' },
          ]" :key="item.id" @click="aba = item.id; sidebarAberta = false"
            class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200"
            :style="aba === item.id
              ? { background: 'var(--accent-soft)', color: 'var(--accent)' }
              : { color: 'var(--text-dim)' }"
            @mouseenter="aba !== item.id ? $event.target.style.background = 'var(--surface0)' : null"
            @mouseleave="$event.target.style.background = ''">
            <svg v-if="item.icone === 'home'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>
            <svg v-else-if="item.icone === 'package'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
            </svg>
            <svg v-else-if="item.icone === 'currency-dollar'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ item.label }}
          </button>
        </nav>

        <div class="p-3 border-t" :style="{ borderColor: 'var(--border)' }">
          <div class="px-3.5 py-2 flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
              :style="{ background: 'var(--accent-gradient)' }">
              {{ administrador?.email?.charAt(0).toUpperCase() || 'A' }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium truncate" :style="{ color: 'var(--text-bright)' }">{{ administrador?.email || 'Admin' }}</p>
            </div>
          </div>
          <button @click="logout"
            class="w-full flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all"
            :style="{ color: 'var(--text-dim)' }"
            @mouseenter="$event.target.style.background = 'var(--surface0)'"
            @mouseleave="$event.target.style.background = ''">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
            </svg>
            Sair
          </button>
        </div>
      </div>
    </aside>

    <div class="flex-1 min-w-0 flex flex-col">
      <header class="sticky top-0 z-30 flex items-center justify-between h-14 px-4 sm:px-6"
        :style="{ background: 'var(--bg-card)', backdropFilter: 'blur(16px)', borderBottom: '1px solid var(--border)' }">
        <div class="flex items-center gap-3">
          <button @click="sidebarAberta = true" class="lg:hidden w-9 h-9 rounded-xl flex items-center justify-center"
            :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
          <div>
            <h1 class="font-display text-lg font-semibold leading-tight" :style="{ color: 'var(--text-bright)' }">
              {{ aba === 'dashboard' ? 'Dashboard' : aba === 'produtos' ? 'Produtos' : 'Financeiro' }}
            </h1>
            <p class="text-[11px]" :style="{ color: 'var(--text-dim)' }">
              {{ produtos.filter(p => p.ativo).length }} ativos · {{ produtos.length }} total
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button @click="tema.toggle()"
            class="w-9 h-9 rounded-xl flex items-center justify-center transition-all"
            :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }">
            <svg v-if="tema.escuro" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
          </button>
          <router-link to="/"
            class="w-9 h-9 rounded-xl flex items-center justify-center transition-all"
            :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }" title="Ver catálogo">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>
          </router-link>
        </div>
      </header>

      <main class="flex-1 p-4 sm:p-6 pb-24 lg:pb-6">
        <div v-if="notificacoes.length" class="fixed top-6 right-6 z-[100] flex flex-col gap-3 max-w-sm w-full pointer-events-none px-4 sm:px-0">
          <div v-for="n in notificacoes" :key="n.id"
            class="pointer-events-auto flex items-start gap-3 rounded-xl p-4 shadow-lg border animate-fade-in-up"
            :style="n.tipo === 'sucesso'
              ? { background: 'var(--bg-card-solid)', borderColor: 'rgba(var(--ctp-green), 0.25)' }
              : { background: 'var(--bg-card-solid)', borderColor: 'rgba(var(--ctp-red), 0.25)' }">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium" :style="{ color: 'var(--text)' }">{{ n.mensagem }}</p>
            </div>
          </div>
        </div>

        <div v-if="carregando" class="flex items-center justify-center py-32">
          <div class="flex flex-col items-center gap-4">
            <div class="w-10 h-10 rounded-full border-2 animate-spin" :style="{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }"></div>
            <p class="text-sm" :style="{ color: 'var(--text-dim)' }">Carregando...</p>
          </div>
        </div>

        <div v-else-if="erro" class="flex flex-col items-center justify-center py-32">
          <p :style="{ color: 'var(--text-dim)' }">{{ erro }}</p>
          <button @click="carregar()" class="btn-outline mt-4">Tentar novamente</button>
        </div>

        <template v-else>
          <div v-if="aba === 'dashboard'" class="space-y-6 animate-fade-in-up">
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div v-for="(stat, i) in stats" :key="i" class="card-premium p-4 sm:p-5">
                <div class="flex items-center gap-3 mb-3">
                  <div class="w-10 h-10 rounded-xl flex items-center justify-center"
                    :style="{ background: `rgba(var(--ctp-${stat.cor}), 0.15)`, color: `rgb(var(--ctp-${stat.cor}))` }">
                    <svg v-if="stat.icone === 'package'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                    </svg>
                    <svg v-else-if="stat.icone === 'currency-dollar'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <svg v-else-if="stat.icone === 'trending-down'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 6L9 12.75l4.286-4.286a11.948 11.948 0 014.306 6.43l.776 2.898m0 0l3.182-5.511m-3.182 5.51l-5.511-3.181" />
                    </svg>
                    <svg v-else-if="stat.icone === 'chart-bar'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                    </svg>
                    <svg v-else-if="stat.icone === 'eye'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                </div>
                <p class="text-2xl font-display font-bold" :style="{ color: 'var(--text-bright)' }">{{ stat.valor }}</p>
                <p class="text-xs mt-1" :style="{ color: 'var(--text-dim)' }">{{ stat.label }}</p>
              </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div class="card-premium p-5">
                <h3 class="font-display text-base font-semibold mb-4" :style="{ color: 'var(--text-bright)' }">Produtos por Categoria</h3>
                <div class="space-y-3">
                  <div v-for="[cat, qtd] in produtosPorCategoria" :key="cat">
                    <div class="flex items-center justify-between text-sm mb-1">
                      <span :style="{ color: 'var(--text)' }">{{ cat }}</span>
                      <span class="font-semibold" :style="{ color: 'var(--text-dim)' }">{{ qtd }}</span>
                    </div>
                    <div class="h-2 rounded-full overflow-hidden" :style="{ background: 'var(--surface0)' }">
                      <div class="h-full rounded-full transition-all duration-500" :style="{
                        width: `${(qtd / Math.max(...Object.values(produtosPorCategoria.map(([,q]) => q)))) * 100}%`,
                        background: 'var(--accent-gradient)',
                      }"></div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="card-premium p-5">
                <h3 class="font-display text-base font-semibold mb-4" :style="{ color: 'var(--text-bright)' }">Resumo do Estoque</h3>
                <div class="space-y-3">
                  <div class="flex items-center justify-between text-sm" :style="{ color: 'var(--text-dim)' }">
                    <span>Total em estoque</span>
                    <span class="font-semibold" :style="{ color: 'var(--text-bright)' }">
                      {{ produtos.filter(p => p.ativo).reduce((s, p) => s + p.estoque, 0) }} unidades
                    </span>
                  </div>
                  <div class="flex items-center justify-between text-sm" :style="{ color: 'var(--text-dim)' }">
                    <span>Valor total</span>
                    <span class="font-display font-semibold gradient-text">
                      R$ {{ produtos.filter(p => p.ativo).reduce((s, p) => s + p.preco * p.estoque, 0).toFixed(2) }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between text-sm" :style="{ color: 'var(--text-dim)' }">
                    <span>Custo total</span>
                    <span class="font-semibold" :style="{ color: 'var(--text-bright)' }">
                      R$ {{ produtos.filter(p => p.ativo).reduce((s, p) => s + (p.purchasePrice || 0) * p.estoque, 0).toFixed(2) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="aba === 'produtos'" class="animate-fade-in-up">
            <div class="flex flex-wrap items-center justify-between gap-3 mb-5">
              <div class="flex flex-wrap items-center gap-2">
                <div class="relative">
                  <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" :style="{ color: 'var(--text-dim)' }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                  </svg>
                  <input v-model="buscaAdmin" placeholder="Buscar..." class="input-field pl-9 w-40 sm:w-56 text-sm" />
                </div>
                <select v-model="filtroCategoria" class="input-field w-auto text-sm">
                  <option value="">Todas categorias</option>
                  <option v-for="cat in categoriasAdmin" :key="cat" :value="cat">{{ cat }}</option>
                </select>
                <select v-model="filtroAtivo" class="input-field w-auto text-sm">
                  <option value="todos">Todos</option>
                  <option value="ativos">Ativos</option>
                  <option value="inativos">Inativos</option>
                </select>
              </div>
              <button @click="abrirForm()" class="btn-primary text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                Novo Produto
              </button>
            </div>

            <transition name="scale-fade">
              <div v-if="mostrandoForm" class="card-premium p-5 sm:p-6 mb-6">
                <div class="flex items-center justify-between mb-5">
                  <h2 class="font-display text-lg font-semibold" :style="{ color: 'var(--text-bright)' }">
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
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Nome</label>
                    <input v-model="form.nome" required class="input-field" />
                  </div>
                  <div class="sm:col-span-2">
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Descrição</label>
                    <textarea v-model="form.descricao" rows="3" class="input-field resize-none" />
                  </div>
                  <div>
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Preço (R$)</label>
                    <input v-model="form.preco" type="number" step="0.01" min="0.01" required class="input-field" />
                  </div>
                  <div>
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Estoque</label>
                    <input v-model="form.estoque" type="number" min="0" class="input-field" />
                  </div>
                  <div>
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Categoria</label>
                    <input v-model="form.categoria" required class="input-field" placeholder="Ex: Skincare" list="categorias-suggest" />
                    <datalist id="categorias-suggest">
                      <option v-for="cat in categoriasAdmin" :key="cat" :value="cat" />
                    </datalist>
                  </div>
                  <div>
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Preço de Custo (R$)</label>
                    <input v-model="form.purchasePrice" type="number" step="0.01" min="0" class="input-field" />
                  </div>
                  <div>
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">Margem (%)</label>
                    <input v-model="form.profitMargin" type="number" step="0.1" min="0" class="input-field" />
                  </div>
                  <div class="flex items-center gap-3">
                    <label class="flex items-center gap-2 cursor-pointer select-none">
                      <input v-model="form.promocional" type="checkbox" class="w-4 h-4 rounded"
                        :style="{ accentColor: 'var(--ctp-red)' }" />
                      <span class="text-xs font-medium" :style="{ color: 'var(--text-dim)' }">Promocional</span>
                    </label>
                    <input v-if="form.promocional" v-model="form.preco_promocional" type="number" step="0.01" min="0"
                      placeholder="Preço promocional" class="input-field text-sm flex-1" />
                  </div>
                  <div>
                    <label class="block text-xs font-medium mb-1.5" :style="{ color: 'var(--text-dim)' }">
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

            <div v-if="!produtos.length" class="flex flex-col items-center justify-center py-24 text-center">
              <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-4" :style="{ background: 'var(--accent-soft)' }">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  :style="{ color: 'var(--accent)' }" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                </svg>
              </div>
              <p class="font-display text-xl font-light" :style="{ color: 'var(--text-dim)' }">Nenhum produto ainda</p>
              <button @click="abrirForm()" class="btn-primary mt-6 text-sm">Criar primeiro produto</button>
            </div>

            <div v-else-if="!produtosFiltrados.length" class="flex flex-col items-center justify-center py-24 text-center">
              <p class="font-display text-xl font-light" :style="{ color: 'var(--text-dim)' }">Nenhum resultado para os filtros</p>
              <button @click="buscaAdmin = ''; filtroCategoria = ''; filtroAtivo = 'todos'" class="btn-ghost mt-3 text-sm">Limpar filtros</button>
            </div>

            <div v-else class="space-y-2">
              <div v-for="p in produtosFiltrados" :key="p.id"
                class="card-premium overflow-hidden transition-all"
                :class="p.ativo ? '' : 'opacity-60 hover:opacity-100'">
                <div class="flex items-center gap-4 p-4">
                  <div class="w-14 h-14 rounded-xl overflow-hidden flex-shrink-0 relative" :style="{ background: 'var(--surface0)' }">
                    <img v-if="p.imagem_url" :src="p.imagem_url" :alt="p.nome" class="w-full h-full object-cover" />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                        :style="{ color: 'var(--text-dim)' }" stroke-width="1">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5z" />
                      </svg>
                    </div>
                    <div v-if="!p.ativo" class="absolute inset-0 flex items-center justify-center rounded-xl"
                      :style="{ background: 'rgba(0,0,0,0.4)' }">
                      <span class="text-[8px] font-bold uppercase tracking-wider text-white">Inativo</span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-display font-semibold text-sm sm:text-base truncate" :style="{ color: 'var(--text-bright)' }">{{ p.nome }}</p>
                    <div class="flex flex-wrap items-center gap-x-2.5 gap-y-1 mt-1">
                      <span class="text-[10px] px-2 py-0.5 rounded-full" :style="{ background: 'var(--accent-soft)', color: 'var(--accent)' }">{{ p.categoria }}</span>
                      <span class="font-display text-sm font-semibold gradient-text">R$ {{ p.preco.toFixed(2) }}</span>
                      <span class="text-[10px]" :style="{ color: p.estoque > 0 ? 'rgb(var(--ctp-green))' : 'rgb(var(--ctp-red))' }">
                        {{ p.estoque }} un.
                      </span>
                      <span v-if="p.purchasePrice" class="text-[10px]" :style="{ color: 'var(--text-dim)' }">
                        Custo: R$ {{ p.purchasePrice.toFixed(2) }}
                      </span>
                      <span v-if="p.profitMargin" class="text-[10px]" :style="{ color: 'var(--text-dim)' }">
                        Margem: {{ p.profitMargin }}%
                      </span>
                      <span class="text-[10px] flex items-center gap-0.5" :style="{ color: 'var(--text-dim)' }">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-3 h-3">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {{ p.visualizacoes || 0 }}
                      </span>
                    </div>
                  </div>
                  <div v-if="p.promocional" class="flex-shrink-0 self-center">
                    <span class="px-2 py-0.5 rounded text-[10px] font-extrabold"
                      :style="{ background: 'var(--ctp-red)', color: 'white' }">
                      -{{ Math.round((1 - p.preco_promocional / p.preco) * 100) }}%
                    </span>
                  </div>
                  <div class="flex gap-1 flex-shrink-0">
                    <button @click="togglePromocional(p.id)"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:scale-105"
                      :style="{ background: p.promocional ? 'rgba(var(--ctp-red), 0.15)' : 'var(--surface0)', color: p.promocional ? 'var(--ctp-red)' : 'var(--text-dim)' }"
                      :title="p.promocional ? 'Remover promoção' : 'Tornar promocional'">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                      </svg>
                    </button>
                    <button @click="toggleAtivo(p.id)"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:scale-105"
                      :style="{ background: 'var(--surface0)', color: p.ativo ? 'rgb(var(--ctp-green))' : 'var(--text-dim)' }"
                      :title="p.ativo ? 'Desativar' : 'Ativar'">
                      <svg v-if="p.ativo" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>
                    <button @click="duplicar(p.id)"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:scale-105"
                      :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }" title="Duplicar">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 013.75.808m1.5-2.933V3.375c0-.621.504-1.125 1.125-1.125h9.75c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-1.5a9.06 9.06 0 01-3.75-.808" />
                      </svg>
                    </button>
                    <button @click="abrirForm(p)"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:scale-105"
                      :style="{ background: 'var(--surface0)', color: 'var(--text-dim)' }" title="Editar">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                      </svg>
                    </button>
                    <button @click="confirmarDelete(p.id)"
                      class="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:scale-105"
                      :style="{ background: 'rgba(var(--ctp-red), 0.1)', color: 'var(--ctp-red)' }" title="Excluir">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="aba === 'financeiro' && !carregando" class="space-y-6 animate-fade-in-up">
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="card-premium p-5">
                <p class="text-xs mb-1" :style="{ color: 'var(--text-dim)' }">Receita Potencial</p>
                <p class="text-2xl font-display font-bold gradient-text">
                  R$ {{ produtos.filter(p => p.ativo).reduce((s, p) => s + p.preco * p.estoque, 0).toFixed(2) }}
                </p>
              </div>
              <div class="card-premium p-5">
                <p class="text-xs mb-1" :style="{ color: 'var(--text-dim)' }">Custo Total</p>
                <p class="text-2xl font-display font-bold" :style="{ color: 'var(--text-bright)' }">
                  R$ {{ produtos.filter(p => p.ativo).reduce((s, p) => s + (p.purchasePrice || 0) * p.estoque, 0).toFixed(2) }}
                </p>
              </div>
              <div class="card-premium p-5">
                <p class="text-xs mb-1" :style="{ color: 'var(--text-dim)' }">Lucro Potencial</p>
                <p class="text-2xl font-display font-bold" :style="{ color: 'rgb(var(--ctp-green))' }">
                  R$ {{ (produtos.filter(p => p.ativo).reduce((s, p) => s + p.preco * p.estoque, 0) - produtos.filter(p => p.ativo).reduce((s, p) => s + (p.purchasePrice || 0) * p.estoque, 0)).toFixed(2) }}
                </p>
              </div>
              <div class="card-premium p-5">
                <p class="text-xs mb-1" :style="{ color: 'var(--text-dim)' }">Produtos com Custo</p>
                <p class="text-2xl font-display font-bold" :style="{ color: 'var(--text-bright)' }">
                  {{ produtos.filter(p => p.ativo && p.purchasePrice).length }} / {{ produtos.filter(p => p.ativo).length }}
                </p>
              </div>
            </div>

            <div class="card-premium p-5">
              <h3 class="font-display text-base font-semibold mb-4" :style="{ color: 'var(--text-bright)' }">Lucratividade por Produto</h3>
              <div v-if="!produtosFinanceiro.length" class="text-center py-8">
                <p class="text-sm" :style="{ color: 'var(--text-dim)' }">Nenhum produto ativo com preço de custo.</p>
                <p class="text-xs mt-1" :style="{ color: 'var(--text-dim)' }">Edite um produto e adicione custo para ver a lucratividade.</p>
              </div>
              <div v-else class="space-y-2">
                <div v-for="p in produtosFinanceiro" :key="p.id" class="flex items-center gap-4 p-3 rounded-xl"
                  :style="{ background: 'var(--surface0)' }">
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium truncate" :style="{ color: 'var(--text-bright)' }">{{ p.nome }}</p>
                    <p class="text-xs" :style="{ color: 'var(--text-dim)' }">{{ p.categoria }}</p>
                  </div>
                  <div class="text-right text-xs leading-relaxed" :style="{ color: 'var(--text-dim)' }">
                    <div>Venda: <span class="font-semibold" :style="{ color: 'var(--text-bright)' }">R$ {{ p.preco.toFixed(2) }}</span></div>
                    <div>Custo: R$ {{ p.purchasePrice.toFixed(2) }}</div>
                  </div>
                  <div class="text-right min-w-[110px]">
                    <p class="text-sm font-semibold" :style="{ color: 'rgb(var(--ctp-green))' }">+R$ {{ p.lucroUni.toFixed(2) }}</p>
                    <div class="flex items-center gap-1.5 mt-0.5">
                      <div class="flex-1 h-1.5 rounded-full overflow-hidden" :style="{ background: 'var(--surface-2)' }">
                        <div class="h-full rounded-full" :style="{
                          width: `${Math.min(Number(p.margemReal), 100)}%`,
                          background: Number(p.margemReal) > 40 ? 'rgb(var(--ctp-green))' : Number(p.margemReal) > 20 ? 'rgb(var(--ctp-yellow))' : 'rgb(var(--ctp-peach))',
                        }"></div>
                      </div>
                      <span class="text-[10px] font-semibold" :style="{ color: 'var(--text-dim)' }">{{ p.margemReal }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </main>

      <Teleport to="body">
        <div v-if="mostrarDeleteDialog" class="fixed inset-0 z-[200] flex items-center justify-center px-4"
          style="background: rgba(0,0,0,0.4); backdrop-filter: blur(4px);"
          @click.self="mostrarDeleteDialog = false">
          <div class="card-premium p-6 max-w-sm w-full animate-scale-in text-center">
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
</style>
