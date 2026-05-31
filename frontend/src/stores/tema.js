import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useTemaStore = defineStore('tema', () => {
  const escuro = ref(false)

  function init() {
    const saved = localStorage.getItem('catalogo_theme')
    if (saved === 'dark') {
      escuro.value = true
    } else if (saved === 'light') {
      escuro.value = false
    } else {
      escuro.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    aplicar()
  }

  function toggle() {
    escuro.value = !escuro.value
  }

  function aplicar() {
    document.documentElement.classList.toggle('dark', escuro.value)
    localStorage.setItem('catalogo_theme', escuro.value ? 'dark' : 'light')
  }

  watch(escuro, aplicar)

  return { escuro, init, toggle }
})
