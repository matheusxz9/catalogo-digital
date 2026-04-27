<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/services/api";
import AppHeader from "@/components/AppHeader.vue";
 
const router = useRouter();
 
// Estado
const produtos = ref([]);
const carregando = ref(false);
const erro = ref(null);
const sucesso = ref(null);
 
// Modal / formulário
const mostrarFormulario = ref(false);
const salvando = ref(false);
const editandoId = ref(null);
 
const formInicial = {
  nome: "",
  categoria: "",
  descricao: "",
  preco: "",
  estoque: 0,
  imagem: null,
};
const form = ref({ ...formInicial });
const imagemPreview = ref(null);
const imagemArquivo = ref(null);
 
// ─── Autenticação ────────────────────────────────────────────
const token = ref(localStorage.getItem("token") || null);
const loginEmail = ref("");
const loginSenha = ref("");
const loginErro = ref(null);
const loginCarregando = ref(false);
 
async function fazerLogin() {
  loginErro.value = null;
  loginCarregando.value = true;
  try {
    const res = await api.login(loginEmail.value, loginSenha.value);
    token.value = res.access_token;
    localStorage.setItem("token", res.access_token);
    await carregarProdutos();
  } catch (e) {
    loginErro.value = e.message || "Email ou senha incorretos";
  } finally {
    loginCarregando.value = false;
  }
}
 
function sair() {
  token.value = null;
  localStorage.removeItem("token");
}
 
// ─── Produtos ────────────────────────────────────────────────
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
 
onMounted(() => {
  if (token.value) carregarProdutos();
});
 
// ─── Formulário ──────────────────────────────────────────────
function abrirNovo() {
  editandoId.value = null;
  form.value = { ...formInicial };
  imagemPreview.value = null;
  imagemArquivo.value = null;
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
    imagem: null,
  };
  imagemPreview.value = produto.imagem_url || null;
  imagemArquivo.value = null;
  mostrarFormulario.value = true;
}
 
function fecharFormulario() {
  mostrarFormulario.value = false;
  editandoId.value = null;
  form.value = { ...formInicial };
  imagemPreview.value = null;
  imagemArquivo.value = null;
}
 
function onImagemSelecionada(e) {
  const arquivo = e.target.files[0];
  if (!arquivo) return;
  imagemArquivo.value = arquivo;
  imagemPreview.value = URL.createObjectURL(arquivo);
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
      // Atualiza dados textuais
      await api.atualizarProduto(editandoId.value, {
        nome: form.value.nome,
        categoria: form.value.categoria,
        descricao: form.value.descricao,
        preco: parseFloat(form.value.preco),
        estoque: parseInt(form.value.estoque),
      });
      // Atualiza imagem separadamente se houver nova
      if (imagemArquivo.value) {
        const fd = new FormData();
        fd.append("imagem", imagemArquivo.value);
        await api.atualizarImagemProduto(editandoId.value, fd);
      }
      mostrarSucesso("Produto atualizado!");
    } else {
      const fd = new FormData();
      fd.append("nome", form.value.nome);
      fd.append("categoria", form.value.categoria);
      fd.append("descricao", form.value.descricao || "");
      fd.append("preco", parseFloat(form.value.preco));
      fd.append("estoque", parseInt(form.value.estoque));
      if (imagemArquivo.value) fd.append("imagem", imagemArquivo.value);
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
</script>
 
<template>
  <div>
    <AppHeader />
 
    <main class="container" style="padding-top: 2rem; padding-bottom: 3rem">
 
      <!-- ── LOGIN ── -->
      <div v-if="!token" class="login-wrapper">
        <div class="login-card">
          <h1 class="login-titulo">Área Administrativa</h1>
          <p class="login-sub">Studio Bella Mizi</p>
 
          <div v-if="loginErro" class="alerta-erro">{{ loginErro }}</div>
 
          <div class="campo">
            <label>Email</label>
            <input v-model="loginEmail" type="email" placeholder="admin@email.com" />
          </div>
          <div class="campo">
            <label>Senha</label>
            <input
              v-model="loginSenha"
              type="password"
              placeholder="••••••••"
              @keyup.enter="fazerLogin"
            />
          </div>
          <button class="btn-primario" :disabled="loginCarregando" @click="fazerLogin">
            {{ loginCarregando ? "Entrando..." : "Entrar" }}
          </button>
        </div>
      </div>
 
      <!-- ── PAINEL ── -->
      <div v-else>
 
        <!-- Cabeçalho -->
        <div class="painel-header">
          <h1 class="painel-titulo">Produtos</h1>
          <div style="display:flex; gap: 0.75rem;">
            <button class="btn-novo" @click="abrirNovo">+ Novo produto</button>
            <button class="btn-sair" @click="sair">Sair</button>
          </div>
        </div>
 
        <!-- Alertas -->
        <div v-if="sucesso" class="alerta-sucesso">{{ sucesso }}</div>
        <div v-if="erro" class="alerta-erro">{{ erro }}</div>
 
        <!-- Carregando -->
        <div v-if="carregando" class="estado-central">
          <div class="spinner"></div>
        </div>
 
        <!-- Tabela -->
        <div v-else-if="produtos.length > 0" class="tabela-wrapper">
          <table class="tabela">
            <thead>
              <tr>
                <th>Imagem</th>
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
                  <img
                    v-if="p.imagem_url"
                    :src="p.imagem_url"
                    :alt="p.nome"
                    class="tabela-img"
                  />
                  <div v-else class="tabela-img-placeholder">📷</div>
                </td>
                <td class="tabela-nome">{{ p.nome }}</td>
                <td>{{ p.categoria }}</td>
                <td>R$ {{ p.preco.toFixed(2) }}</td>
                <td>{{ p.estoque }}</td>
                <td>
                  <div style="display:flex; gap:0.5rem;">
                    <button class="btn-editar" @click="abrirEdicao(p)">Editar</button>
                    <button class="btn-deletar" @click="deletar(p)">Deletar</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
 
        <!-- Vazio -->
        <div v-else class="estado-central">
          <p>Nenhum produto cadastrado ainda.</p>
          <button class="btn-novo" @click="abrirNovo">+ Criar primeiro produto</button>
        </div>
 
      </div>
    </main>
 
    <!-- ── MODAL DE FORMULÁRIO ── -->
    <div v-if="mostrarFormulario" class="modal-overlay" @click.self="fecharFormulario">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editandoId ? "Editar produto" : "Novo produto" }}</h2>
          <button class="modal-fechar" @click="fecharFormulario">✕</button>
        </div>
 
        <div v-if="erro" class="alerta-erro" style="margin-bottom:1rem;">{{ erro }}</div>
 
        <div class="modal-corpo">
          <!-- Imagem -->
          <div class="campo">
            <label>Imagem</label>
            <div class="upload-area">
              <img v-if="imagemPreview" :src="imagemPreview" class="upload-preview" />
              <div v-else class="upload-placeholder">📷 Clique para selecionar</div>
              <input type="file" accept="image/jpeg,image/png,image/webp" @change="onImagemSelecionada" class="upload-input" />
            </div>
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
          <button class="btn-primario" style="width:auto;" :disabled="salvando" @click="salvar">
            {{ salvando ? "Salvando..." : editandoId ? "Salvar alterações" : "Criar produto" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
 
<style scoped>
/* ── Login ── */
.login-wrapper {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
 
.login-card {
  background: white;
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-borda);
  box-shadow: var(--sombra);
  padding: 2rem;
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
 
.login-titulo {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--cor-texto);
}
 
.login-sub {
  font-size: 0.85rem;
  color: var(--cor-texto-suave);
  margin-top: -0.5rem;
}
 
/* ── Painel ── */
.painel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
 
.painel-titulo {
  font-size: 1.5rem;
  font-weight: 700;
}
 
.btn-novo {
  background: var(--cor-primaria);
  color: white;
  border: none;
  border-radius: var(--raio-borda);
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transicao);
}
 
.btn-novo:hover {
  background: var(--cor-primaria-escura);
}
 
.btn-sair {
  background: white;
  color: var(--cor-texto-suave);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-borda);
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transicao);
}
 
.btn-sair:hover {
  border-color: var(--cor-erro);
  color: var(--cor-erro);
}
 
/* ── Alertas ── */
.alerta-sucesso {
  background: var(--cor-sucesso-fundo);
  color: var(--cor-sucesso);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 600;
}
 
.alerta-erro {
  background: var(--cor-erro-fundo);
  color: var(--cor-erro);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}
 
/* ── Tabela ── */
.tabela-wrapper {
  background: white;
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-borda);
  box-shadow: var(--sombra);
  overflow: hidden;
}
 
.tabela {
  width: 100%;
  border-collapse: collapse;
}
 
.tabela th {
  background: var(--cor-primaria-clara);
  color: var(--cor-primaria);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.85rem 1rem;
  text-align: left;
}
 
.tabela td {
  padding: 0.85rem 1rem;
  border-top: 1px solid var(--cor-borda);
  color: var(--cor-texto);
  font-size: 0.92rem;
  vertical-align: middle;
}
 
.tabela tr:hover td {
  background: #fafafa;
}
 
.tabela-img {
  width: 52px;
  height: 52px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--cor-borda);
}
 
.tabela-img-placeholder {
  width: 52px;
  height: 52px;
  background: var(--cor-fundo);
  border: 1px solid var(--cor-borda);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}
 
.tabela-nome {
  font-weight: 600;
}
 
.btn-editar {
  background: var(--cor-primaria);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transicao);
}
 
.btn-editar:hover {
  background: var(--cor-primaria-escura);
}
 
.btn-deletar {
  background: var(--cor-erro-fundo);
  color: var(--cor-erro);
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transicao);
}
 
.btn-deletar:hover {
  background: var(--cor-erro);
  color: white;
}
 
/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}
 
.modal {
  background: white;
  border-radius: var(--raio-borda);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}
 
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--cor-borda);
}
 
.modal-header h2 {
  font-size: 1.1rem;
  font-weight: 700;
}
 
.modal-fechar {
  background: none;
  border: none;
  font-size: 1.1rem;
  color: var(--cor-texto-suave);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: var(--transicao);
}
 
.modal-fechar:hover {
  background: var(--cor-fundo);
  color: var(--cor-texto);
}
 
.modal-corpo {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
 
.modal-rodape {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--cor-borda);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
 
/* ── Campos ── */
.campo {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
 
.campo label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--cor-texto);
}
 
.campo input,
.campo textarea {
  border: 1px solid var(--cor-borda);
  border-radius: 8px;
  padding: 0.65rem 0.9rem;
  font-size: 0.95rem;
  font-family: inherit;
  transition: var(--transicao);
  outline: none;
  color: var(--cor-texto);
}
 
.campo input:focus,
.campo textarea:focus {
  border-color: var(--cor-primaria);
  box-shadow: 0 0 0 3px var(--cor-primaria-clara);
}
 
.campo textarea {
  resize: vertical;
}
 
.campo-duplo {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
 
.obrigatorio {
  color: var(--cor-erro);
}
 
.btn-cancelar {
  background: white;
  color: var(--cor-texto-suave);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-borda);
  padding: 0.65rem 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transicao);
}
 
.btn-cancelar:hover {
  border-color: var(--cor-texto-suave);
  color: var(--cor-texto);
}
 
/* ── Upload ── */
.upload-area {
  position: relative;
  border: 2px dashed var(--cor-borda);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: var(--transicao);
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}
 
.upload-area:hover {
  border-color: var(--cor-primaria);
  background: var(--cor-primaria-clara);
}
 
.upload-preview {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
}
 
.upload-placeholder {
  color: var(--cor-texto-suave);
  font-size: 0.9rem;
  text-align: center;
  padding: 1rem;
}
 
.upload-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}
</style>
 
