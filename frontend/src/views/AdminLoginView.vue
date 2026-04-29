<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/services/api";

const router = useRouter();
const email = ref("");
const senha = ref("");
const erro = ref(null);
const carregando = ref(false);

async function entrar() {
  erro.value = null;
  carregando.value = true;
  try {
    const { access_token } = await api.login(email.value, senha.value);
    localStorage.setItem("token", access_token);
    router.push({ name: "admin" });
  } catch (e) {
    erro.value = e.message || "Email ou senha incorretos";
  } finally {
    carregando.value = false;
  }
}
</script>

<template>
  <div class="login-wrapper">
    <button class="btn-voltar" @click="router.push({name: 'Catalogo'})">
      <- Voltar ao catálogo
    </button>
    <div class="login-card">
      <h1 class="login-titulo">Área Administrativa</h1>
      <p class="login-sub">Studio Bella Mizi</p>

      <div v-if="erro" class="login-erro">{{ erro }}</div>

      <div class="login-campo">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="admin@email.com" />
      </div>

      <div class="login-campo">
        <label>Senha</label>
        <input v-model="senha" type="password" placeholder="••••••••" @keyup.enter="entrar" />
      </div>

      <button class="btn-primario" :disabled="carregando" @click="entrar">
        {{ carregando ? "Entrando..." : "Entrar" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--cor-fundo);
  gap: 1rem;
}

.btn-voltar {
  background: none;
  color: var(--cor-texto-suave);
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transicao);
}
.btn-voltar:hover { color: var(--cor-primaria); }

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

.login-erro {
  background: var(--cor-erro-fundo);
  color: var(--cor-erro);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.login-campo {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.login-campo label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--cor-texto);
}

.login-campo input {
  border: 1px solid var(--cor-borda);
  border-radius: 8px;
  padding: 0.65rem 0.9rem;
  font-size: 0.95rem;
  font-family: inherit;
  transition: var(--transicao);
  outline: none;
}

.login-campo input:focus {
  border-color: var(--cor-primaria);
  box-shadow: 0 0 0 3px var(--cor-primaria-clara);
}
</style>
