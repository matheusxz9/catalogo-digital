import { createRouter, createWebHistory } from 'vue-router'
import CatalogoView from '@/views/CatalogoView.vue'
import ProdutoView from '@/views/ProdutoView.vue'
import AdminLoginView from '@/views/AdminLoginView.vue'
import AdminView from '@/views/AdminView.vue'

const routes = [
  { path: '/', name: 'Catalogo', component: CatalogoView },
  { path: '/produto/:id', name: 'Produto', component: ProdutoView },
  { path: '/admin/login', name: 'AdminLogin', component: AdminLoginView },
  { path: '/admin', name: 'Admin', component: AdminView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next({ name: 'AdminLogin' })
  } else {
    next()
  }
})

export default router
