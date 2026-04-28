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

const formInicial = { nome: "", categoria: "", descricao: "", preco: "", estoque: 0 };
const form = ref({ ...formInicial });

// Múltiplas imagens — até 4
const imagensSelecionadas = ref([]); // { file, preview }

function sair() {
  localStorage.removeItem("token");
  router.push({ name: "adminLogin" });
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
  form.value = { ...formInicial };
  imagensSelecionadas.value = [];
  mostrarFormulario.value = true;
}

function abrirEdicao(produto) {
  editandoId.value = produto.id;
  form.value = {
    nome: produto.nome,
    categoria: produto.categoria,
    descricao: produto.descricao || "",
    preco: produto.preco,
    estoque: produto.estoque,
  };
  // Imagens existentes vêm do produto
  imagensSelecionadas.value = [];
  mostrarFormulario.value = true;
}

function fecharFormulario() {
  mostrarFormulario.value = false;
  editandoId.value = null;
  form.value = { ...formInicial };
  imagensSelecionadas.value = [];
  erro.value = null;
}

function onImagensSelecionadas(e) {
  const arquivos = Array.from(e.target.files);
  const restantes = 4 - imagensSelecionadas.value.length;
  arquivos.slice(0, restantes).forEach(arquivo => {
    imagensSelecionadas.value.push({
      file: arquivo,
      preview: URL.createObjectURL(arquivo),
    });
  });
  // Reset input para permitir selecionar de novo
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
      // Se há novas imagens selecionadas, enviar
      if (imagensSelecionadas.value.length > 0) {
        const fd = new FormData();
        imagensSelecionadas.value.forEach(img => fd.append("imagens", img.file));
        await api.adicionarImagens(editandoId.value, fd);
      }
      mostrarSucesso("Produto atualizado!");
    } else {
      const fd = new FormData();
      fd.append("nome", form.value.nome);
      fd.append("categoria", form.value.categoria);
      fd.append("descricao", form.value.descricao || "");
      fd.append("preco", parseFloat(form.value.preco));
      fd.append("estoque", parseInt(form.value.estoque));
      imagensSelecionadas.value.forEach(img => fd.append("imagens", img.file));
      await api.criarProduto(fd);
      mostrarSucesso("Produto criado!");
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
    mostrarSucesso("Imagem deletada!");
    await carregarProdutos();
  } catch (e) {
    erro.value = e.message || "Erro ao deletar imagem.";
  }
}

async function deletar(produto) {
  if (!confirm(`Deletar "${produto.nome}"?`)) return;
  try {
    await api.deletarProduto(produto.id);
    mostrarSucesso("Produto deletado!");
    await carregarProdutos();
  } catch (e) {
    erro.value = e.message || "Erro ao deletar produto.";
  }
}

// Produto sendo editado (para mostrar imagens existentes no modal)
const produtoEditando = ref(null);
function abrirEdicaoCompleta(produto) {
  produtoEditando.value = produto;
  abrirEdicao(produto);
}
</script>

<template>
  <div>
    <AppHeader />
    <main class="container" style="padding-top: 2rem; padding-bottom: 3rem">

      <div class="painel-header">
        <h1 class="painel-titulo">Produtos</h1>
        <div style="display:flex; gap:0.75rem;">
          <button class="btn-novo" @click="abrirNovo">+ Novo produto</button>
          <button class="btn-sair" @click="sair">Sair</button>
        </div>
      </div>

      <div v-if="sucesso" class="alerta-sucesso">{{ sucesso }}</div>
      <div v-if="erro && !mostrarFormulario" class="alerta-erro">{{ erro }}</div>

      <div v-if="carregando" class="estado-central"><div class="spinner"></div></div>

      <div v-else-if="produtos.length > 0" class="tabela-wrapper">
        <table class="tabela">
          <thead>
            <tr>
              <th>Imagens</th>
              <th>Nome</th>
              <th>Categoria</th>
              <th>Preço</th>
              <th>Estoque</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in produtos" :key="p.id">
              <td>
                <div class="thumb-lista">
                  <template v-if="p.imagens && p.imagens.length > 0">
                    <img
                      v-for="img in p.imagens.slice(0,4)"
                      :key="img.id"
                      :src="img.imagem_url"
                      :alt="p.nome"
                      class="tabela-img"
                    />
                  </template>
                  <div v-else-if="p.imagem_url">
                    <img :src="p.imagem_url" :alt="p.nome" class="tabela-img" />
                  </div>
                  <div v-else class="tabela-img-placeholder">📷</div>
                </div>
              </td>
              <td class="tabela-nome">{{ p.nome }}</td>
              <td>{{ p.categoria }}</td>
              <td>R$ {{ p.preco.toFixed(2) }}</td>
              <td>{{ p.estoque }}</td>
              <td>
                <div style="display:flex; gap:0.5rem;">
                  <button class="btn-editar" @click="abrirEdicaoCompleta(p)">Editar</button>
                  <button class="btn-deletar" @click="deletar(p)">Deletar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="estado-central">
        <p>Nenhum produto cadastrado ainda.</p>
        <button class="btn-novo" style="margin-top:0.5rem" @click="abrirNovo">+ Criar primeiro produto</button>
      </div>

    </main>

    <!-- MODAL -->
    <div v-if="mostrarFormulario" class="modal-overlay" @click.self="fecharFormulario">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editandoId ? "Editar produto" : "Novo produto" }}</h2>
          <button class="modal-fechar" @click="fecharFormulario">✕</button>
        </div>

        <div class="modal-corpo">
          <div v-if="erro" class="alerta-erro">{{ erro }}</div>

          <!-- Imagens existentes (apenas na edição) -->
          <div v-if="editandoId && produtoEditando && produtoEditando.imagens && produtoEditando.imagens.length > 0" class="campo">
            <label>Imagens atuais</label>
            <div class="imagens-existentes">
              <div
                v-for="img in produtoEditando.imagens"
                :key="img.id"
                class="img-existente-wrapper"
              >
                <img :src="img.imagem_url" class="img-existente" />
                <button class="img-deletar-btn" @click="deletarImagemExistente(produtoEditando, img.id)" title="Remover">✕</button>
              </div>
            </div>
          </div>

          <!-- Upload de novas imagens -->
          <div class="campo">
            <label>
              {{ editandoId ? "Adicionar novas imagens" : "Imagens" }}
              <span class="texto-suave"> (até {{ 4 - imagensSelecionadas.length }} foto{{ 4 - imagensSelecionadas.length !== 1 ? 's' : '' }})</span>
            </label>

            <!-- Previews das imagens selecionadas -->
            <div v-if="imagensSelecionadas.length > 0" class="previews">
              <div v-for="(img, i) in imagensSelecionadas" :key="i" class="preview-wrapper">
                <img :src="img.preview" class="preview-img" />
                <button class="img-deletar-btn" @click="removerImagem(i)" title="Remover">✕</button>
                <span v-if="i === 0" class="badge-principal">Principal</span>
              </div>
            </div>

            <!-- Botão de adicionar -->
            <label v-if="imagensSelecionadas.length < 4" class="upload-btn">
              📷 Selecionar fotos
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                multiple
                @change="onImagensSelecionadas"
                style="display:none"
              />
            </label>
            <p v-if="imagensSelecionadas.length === 0" class="texto-suave" style="font-size:0.8rem; margin-top:0.25rem;">
              Selecione até 4 fotos de uma vez
            </p>
          </div>

          <!-- Nome -->
          <div class="campo">
            <label>Nome <span class="obrigatorio">*</span></label>
            <input v-model="form.nome" type="text" placeholder="Nome do produto" />
          </div>

          <!-- Categoria -->
          <div class="campo">
            <label>Categoria <span class="obrigatorio">*</span></label>
            <input v-model="form.categoria" type="text" placeholder="Ex: Tratamento Capilar" />
          </div>

          <!-- Descrição -->
          <div class="campo">
            <label>Descrição</label>
            <textarea v-model="form.descricao" rows="3" placeholder="Descreva o produto..."></textarea>
          </div>

          <!-- Preço e Estoque -->
          <div class="campo-duplo">
            <div class="campo">
              <label>Preço (R$) <span class="obrigatorio">*</span></label>
              <input v-model="form.preco" type="number" min="0" step="0.01" placeholder="0,00" />
            </div>
            <div class="campo">
              <label>Estoque <span class="obrigatorio">*</span></label>
              <input v-model="form.estoque" type="number" min="0" placeholder="0" />
            </div>
          </div>
        </div>

        <div class="modal-rodape">
          <button class="btn-cancelar" @click="fecharFormulario">Cancelar</button>
          <button class="btn-primario" style="width:auto" :disabled="salvando" @click="salvar">
            {{ salvando ? "Salvando..." : editandoId ? "Salvar alterações" : "Criar produto" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.painel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:1.5rem; }
.painel-titulo { font-size:1.5rem; font-weight:700; }

.btn-novo { background:var(--cor-primaria); color:white; border:none; border-radius:var(--raio-borda); padding:0.6rem 1.2rem; font-weight:600; cursor:pointer; transition:var(--transicao); }
.btn-novo:hover { background:var(--cor-primaria-escura); }
.btn-sair { background:white; color:var(--cor-texto-suave); border:1px solid var(--cor-borda); border-radius:var(--raio-borda); padding:0.6rem 1.2rem; font-weight:600; cursor:pointer; transition:var(--transicao); }
.btn-sair:hover { border-color:var(--cor-erro); color:var(--cor-erro); }

.alerta-sucesso { background:var(--cor-sucesso-fundo); color:var(--cor-sucesso); padding:0.75rem 1rem; border-radius:8px; margin-bottom:1rem; font-weight:600; }
.alerta-erro { background:var(--cor-erro-fundo); color:var(--cor-erro); padding:0.75rem 1rem; border-radius:8px; margin-bottom:1rem; }

.tabela-wrapper { background:white; border:1px solid var(--cor-borda); border-radius:var(--raio-borda); box-shadow:var(--sombra); overflow:hidden; }
.tabela { width:100%; border-collapse:collapse; }
.tabela th { background:var(--cor-primaria-clara); color:var(--cor-primaria); font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; padding:0.85rem 1rem; text-align:left; }
.tabela td { padding:0.75rem 1rem; border-top:1px solid var(--cor-borda); color:var(--cor-texto); font-size:0.92rem; vertical-align:middle; }
.tabela tr:hover td { background:#fafafa; }

.thumb-lista { display:flex; gap:4px; flex-wrap:wrap; }
.tabela-img { width:44px; height:44px; object-fit:cover; border-radius:6px; border:1px solid var(--cor-borda); }
.tabela-img-placeholder { width:44px; height:44px; background:var(--cor-fundo); border:1px solid var(--cor-borda); border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:1.1rem; }
.tabela-nome { font-weight:600; }

.btn-editar { background:var(--cor-primaria); color:white; border:none; border-radius:6px; padding:0.35rem 0.85rem; font-size:0.82rem; font-weight:600; cursor:pointer; transition:var(--transicao); }
.btn-editar:hover { background:var(--cor-primaria-escura); }
.btn-deletar { background:var(--cor-erro-fundo); color:var(--cor-erro); border:none; border-radius:6px; padding:0.35rem 0.85rem; font-size:0.82rem; font-weight:600; cursor:pointer; transition:var(--transicao); }
.btn-deletar:hover { background:var(--cor-erro); color:white; }

.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.45); display:flex; align-items:center; justify-content:center; z-index:200; padding:1rem; }
.modal { background:white; border-radius:var(--raio-borda); box-shadow:0 20px 60px rgba(0,0,0,0.2); width:100%; max-width:540px; max-height:90vh; display:flex; flex-direction:column; }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding:1.25rem 1.5rem; border-bottom:1px solid var(--cor-borda); flex-shrink:0; }
.modal-header h2 { font-size:1.1rem; font-weight:700; }
.modal-fechar { background:none; border:none; font-size:1.1rem; color:var(--cor-texto-suave); cursor:pointer; padding:0.25rem 0.5rem; border-radius:6px; transition:var(--transicao); }
.modal-fechar:hover { background:var(--cor-fundo); }
.modal-corpo { padding:1.5rem; overflow-y:auto; display:flex; flex-direction:column; gap:1rem; flex:1; }
.modal-rodape { padding:1rem 1.5rem; border-top:1px solid var(--cor-borda); display:flex; justify-content:flex-end; gap:0.75rem; flex-shrink:0; }

.campo { display:flex; flex-direction:column; gap:0.35rem; }
.campo label { font-size:0.85rem; font-weight:600; color:var(--cor-texto); }
.campo input, .campo textarea { border:1px solid var(--cor-borda); border-radius:8px; padding:0.65rem 0.9rem; font-size:0.95rem; font-family:inherit; transition:var(--transicao); outline:none; color:var(--cor-texto); }
.campo input:focus, .campo textarea:focus { border-color:var(--cor-primaria); box-shadow:0 0 0 3px var(--cor-primaria-clara); }
.campo textarea { resize:vertical; }
.campo-duplo { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
.obrigatorio { color:var(--cor-erro); }
.texto-suave { color:var(--cor-texto-suave); font-weight:400; }

.btn-cancelar { background:white; color:var(--cor-texto-suave); border:1px solid var(--cor-borda); border-radius:var(--raio-borda); padding:0.65rem 1.2rem; font-weight:600; cursor:pointer; transition:var(--transicao); }
.btn-cancelar:hover { border-color:var(--cor-texto-suave); }

/* Imagens existentes */
.imagens-existentes { display:flex; gap:0.5rem; flex-wrap:wrap; }
.img-existente-wrapper { position:relative; }
.img-existente { width:80px; height:80px; object-fit:cover; border-radius:8px; border:1px solid var(--cor-borda); display:block; }

/* Previews novas imagens */
.previews { display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.5rem; }
.preview-wrapper { position:relative; }
.preview-img { width:80px; height:80px; object-fit:cover; border-radius:8px; border:2px solid var(--cor-primaria); display:block; }

.img-deletar-btn {
  position:absolute; top:-6px; right:-6px;
  width:20px; height:20px;
  background:var(--cor-erro); color:white;
  border:none; border-radius:50%;
  font-size:0.7rem; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  line-height:1;
}

.badge-principal {
  position:absolute; bottom:4px; left:4px;
  background:var(--cor-primaria); color:white;
  font-size:0.6rem; font-weight:700;
  padding:1px 5px; border-radius:4px;
}

.upload-btn {
  display:inline-flex; align-items:center; gap:0.5rem;
  background:var(--cor-fundo); border:2px dashed var(--cor-borda);
  border-radius:10px; padding:0.75rem 1.25rem;
  cursor:pointer; font-size:0.9rem; font-weight:600;
  color:var(--cor-texto-suave); transition:var(--transicao);
  width:fit-content;
}
.upload-btn:hover { border-color:var(--cor-primaria); color:var(--cor-primaria); background:var(--cor-primaria-clara); }
</style>