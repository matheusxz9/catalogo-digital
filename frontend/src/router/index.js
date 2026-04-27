import { createRouter, createWebHistory } from "vue-router";
import CatalogoView from "@/views/CatalogoView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Catalogo",
      component: CatalogoView,
    },
    {
      path: "/produto/:id",
      name: "produto",
      component: () => import("@/views/ProdutoView.vue"),
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("@/views/AdminView.vue"),
      meta: { requerAuth: true },
    },
    {
      path: "/admin/login",
      name: "adminLogin",
      component: () => import("@/views/AdminLoginView.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      redirect: "/",
    },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to, _from, next) => {
  if (to.meta.requerAuth) {
    const token = localStorage.getItem("token");
    if (!token) {
      next({ name: "adminLogin" });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
