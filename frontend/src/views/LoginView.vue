<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import StatusNotice from "../components/StatusNotice.vue";
import { login } from "../services/api.js";

const router = useRouter();
const route = useRoute();
const form = reactive({ nombre_usuario: "", contrasena: "" });
const loading = ref(false);
const error = ref("");

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    await login(form);
    const next = typeof route.query.next === "string" ? route.query.next : "/";
    await router.replace(next);
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <div class="brand-mark" aria-hidden="true">LR</div>
      <p class="eyebrow">Panel administrativo</p>
      <h1>Restaurant Las Retamas</h1>
      <p class="muted">Ingresa con tu cuenta autorizada para administrar el menú.</p>

      <StatusNotice :message="error" kind="error" />

      <form class="form-stack" @submit.prevent="submit">
        <label>
          Usuario
          <input
            v-model.trim="form.nombre_usuario"
            autocomplete="username"
            required
            maxlength="150"
          />
        </label>
        <label>
          Contraseña
          <input
            v-model="form.contrasena"
            type="password"
            autocomplete="current-password"
            required
            maxlength="200"
          />
        </label>
        <button class="button button-primary" type="submit" :disabled="loading">
          {{ loading ? "Verificando…" : "Ingresar" }}
        </button>
      </form>
    </section>
  </main>
</template>
