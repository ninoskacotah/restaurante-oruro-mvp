import { createRouter, createWebHistory } from "vue-router";

import AdminLayout from "./components/AdminLayout.vue";
import { apiRequest, readToken } from "./services/api.js";
import CatalogView from "./views/CatalogView.vue";
import LoginView from "./views/LoginView.vue";
import MenusView from "./views/MenusView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView },
    {
      path: "/",
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: "/catalogo" },
        { path: "catalogo", name: "catalog", component: CatalogView },
        { path: "menus", name: "menus", component: MenusView },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});

router.beforeEach(async (to) => {
  const authenticated = Boolean(readToken());
  if (to.matched.some((record) => record.meta.requiresAuth) && !authenticated) {
    return { name: "login", query: { next: to.fullPath } };
  }
  if (to.matched.some((record) => record.meta.requiresAuth) && authenticated) {
    try {
      await apiRequest("/auth/me");
    } catch {
      return { name: "login", query: { next: to.fullPath } };
    }
  }
  if (to.name === "login" && authenticated) {
    return { name: "catalog" };
  }
  return true;
});

export default router;
