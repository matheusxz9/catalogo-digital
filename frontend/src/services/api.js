const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

function getToken() {
  return localStorage.getItem('token')
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = { ...options.headers }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (res.status === 204) return null

  let data
  try {
    data = await res.json()
  } catch {
    const text = await res.text()
    throw new Error(
      `Resposta inesperada do servidor (${res.status}): ${text.slice(0, 200)}`,
    )
  }

  if (!res.ok) {
    throw new Error(data.detail || 'Erro na requisição')
  }
  return data
}

export const api = {
  async listarProdutos() {
    return request('/produtos/')
  },
  async buscarProduto(id) {
    return request(`/produtos/${id}`)
  },
  async criarProduto(formData) {
    return request('/produtos/', {
      method: 'POST',
      body: formData,
    })
  },
  async atualizarProduto(id, dados) {
    return request(`/produtos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(dados),
    })
  },
  async deletarProduto(id) {
    return request(`/produtos/${id}`, { method: 'DELETE' })
  },
  async adicionarImagens(id, formData) {
    return request(`/produtos/${id}/imagens`, {
      method: 'POST',
      body: formData,
    })
  },
  async deletarImagem(produtoId, imagemId) {
    return request(`/produtos/${produtoId}/imagens/${imagemId}`, { method: 'DELETE' })
  },
  async visualizarProduto(id) {
    return request(`/produtos/${id}/visualizar`, { method: 'POST' })
  },
  async login(email, senha) {
    return request('/admin/login', {
      method: 'POST',
      body: JSON.stringify({ email, senha }),
    })
  },
  async me() {
    return request('/admin/me')
  },
  async listarProdutosAdmin() {
    return request('/admin/produtos')
  },
  async duplicarProduto(id) {
    return request(`/admin/produtos/${id}/duplicar`, { method: 'POST' })
  },
  async toggleAtivo(id) {
    return request(`/admin/produtos/${id}/toggle-ativo`, { method: 'PATCH' })
  },
}
