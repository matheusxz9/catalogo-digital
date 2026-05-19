const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
 
async function get(caminho) {
  const resposta = await fetch(`${BASE_URL}${caminho}`);
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resposta.status}`);
  }
  return resposta.json();
}
 
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
 
async function getAutenticado(caminho) {
  const token = localStorage.getItem("token");
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: "GET",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resposta.status}`);
  }
  return resposta.json();
}
 
async function deletarAutenticado(caminho) {
  const token = localStorage.getItem("token");
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: "DELETE",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!resposta.ok && resposta.status !== 204) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resposta.status}`);
  }
}
 
export const api = {
  listarProdutos: () => get("/produtos"),
  buscarProduto: (id) => get(`/produtos/${id}`),
  login: (email, senha) => enviar("POST", "/admin/login", { email, senha }),
  obterAdmin: () => getAutenticado("/admin/me"),
 
  // Criar produto com até 4 imagens
  criarProduto: (formData) => enviarForm("POST", "/produtos", formData),
 
  // Atualizar dados textuais
  atualizarProduto: (id, dados) => enviarAutenticado("PUT", `/produtos/${id}`, dados),
 
  // Adicionar novas imagens a produto existente
  adicionarImagens: (id, formData) => enviarForm("POST", `/produtos/${id}/imagens`, formData),
 
  // Deletar uma imagem específica
  deletarImagem: (produtoId, imagemId) =>
    deletarAutenticado(`/produtos/${produtoId}/imagens/${imagemId}`),
 
  // Deletar produto
  deletarProduto: (id) => deletarAutenticado(`/produtos/${id}`),
};
