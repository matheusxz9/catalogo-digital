import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useProdutosStore = defineStore('produtos', {
  state: () => ({
    produtos: [],
    carregando: false,
    erro: null,
  }),
  getters: {
    categorias(state) {
      const cats = [...new Set(state.produtos.map(p => p.categoria))]
      return ['Todos', ...cats.sort()]
    },
  },
  actions: {
    async carregar() {
      this.carregando = true
      this.erro = null
      try {
        this.produtos = await api.listarProdutos()
      } catch (e) {
        this.erro = e.message
      } finally {
        this.carregando = false
      }
    },
  },
})
