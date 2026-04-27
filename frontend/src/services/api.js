const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Requisições GET
async function get(caminho) {
  const resposta = await fetch(`${BASE_URL}${caminho}`);
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resposta.status}`);
  }
  return resposta.json();
}

// Requisições POST e PUT com JSON
async function enviar(metodo, caminho, corpo) {
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: metodo,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resposta.status}`);
  }
  return resposta.json();
}

async function enviarForm(metodo, caminho, formData) {
  const token = localStorage.getItem("token");
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: metodo,
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resposta.status}`);
  }
  return resposta.json();
}

// Requisições autenticadas com JSON
async function enviarAutenticado(metodo, caminho, corpo) {
  const token = localStorage.getItem("token");
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: metodo,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(corpo),
  });
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resposta.status}`);
  }
  return resposta.json();
}

export const api = {
  // Público
  listarProdutos: () => get("/produtos"),
  buscarProduto: (id) => get(`/produtos/${id}`),

  // Admin — autenticado
  login: (email, senha) =>
    enviar("POST", "/admin/login", { email, senha }),

  criarProduto: (formData) =>
    enviarForm("POST", "/produtos", formData),

  atualizarProduto: (id, dados) =>
    enviarAutenticado("PUT", `/produtos/${id}`, dados),

  atualizarImagemProduto: (id, formData) =>
    enviarForm("POST", `/produtos/${id}/imagem`, formData),

  deletarProduto: (id) => {
    const token = localStorage.getItem("token");
    return fetch(`${BASE_URL}/produtos/${id}`, {
      method: "DELETE",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }).then((r) => {
      if (!r.ok && r.status !== 204) throw new Error(`Erro ${r.status}`);
    });
  },
};
