<script setup>
import { onBeforeUnmount, onMounted } from "vue";
import { useRouter } from "vue-router";

import { logout } from "../services/api.js";

const router = useRouter();

async function closeSession() {
  try {
    await logout();
  } finally {
    await router.replace({ name: "login" });
  }
}

function redirectExpiredSession() {
  router.replace({ name: "login" });
}

onMounted(() => window.addEventListener("auth-expired", redirectExpiredSession));
onBeforeUnmount(() =>
  window.removeEventListener("auth-expired", redirectExpiredSession),
);
</script>

<template>
  <div class="admin-shell">
    <aside class="sidebar">
      <div>
        <p class="eyebrow">Restaurant</p>
        <h1>Las Retamas</h1>
        <p class="sidebar-copy">Administración del menú diario</p>
      </div>
      <nav aria-label="Navegación administrativa">
        <RouterLink to="/catalogo">Platos</RouterLink>
        <RouterLink to="/menus">Menús</RouterLink>
        <RouterLink to="/pedidos">Pedidos</RouterLink>
        <RouterLink to="/repartidores">Repartidores</RouterLink>
        <RouterLink to="/clientes">Clientes</RouterLink>
        <RouterLink to="/reportes">Reportes</RouterLink>
      </nav>
      <button class="button button-ghost" type="button" @click="closeSession">
        Cerrar sesión
      </button>
    </aside>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>
