<template>
  <header class="header">
    <div class="container header-inner">
      <a href="/" class="header-logo">
        <img src="/logo.jpeg" alt="Studio Bella Mizi" class="logo-icone" />
        <div>
          <span class="logo-nome">Studio Bella Mizi</span>
          <span class="logo-sub">Produtos de beleza</span>
        </div>
      </a>
      <a href="/admin" class="header-admin">Admin</a>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: white;
  border-bottom: 1px solid var(--cor-borda);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--sombra);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icone {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  object-fit: cover;
}

.logo-nome {
  display: block;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--cor-texto);
}

.logo-sub {
  display: block;
  font-size: 0.75rem;
  color: var(--cor-texto-suave);
}

.header-admin {
  font-size: 0.85rem;
  color: var(--cor-texto-suave);
  transition: var(--transicao);
}

.header-admin:hover {
  color: var(--cor-primaria);
}
</style>
