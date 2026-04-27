import { ref, computed } from 'vue';
import { api } from '@/services/api';
import { defineStore } from 'pinia';

export const useProdutosStore = defineStore('produtos', () => {
    const produtos = ref([]);
    const carregando = ref(false);
    const erro = ref(null);

    const categorias = computed(() => {
        const unicas = new Set(produtos.value.map(p => p.categoria));
        return ['Todos', ...Array.from(unicas).sort()];
    });

    async function carregar() {
        if (produtos.value.length > 0) return;

        carregando.value = true;
        erro.value = null;

        try {
            produtos.value = await api.listarProdutos();
        } catch (e) {
            erro.value = 'Não foi possível carregar os produtos';
            console.error(e);
        } finally {
            carregando.value = false;
        }
    }

    async function recarregar() {
        produtos.value = [];
        await carregar();
    }

    return { produtos, carregando, erro, categorias, carregar, recarregar };
});
