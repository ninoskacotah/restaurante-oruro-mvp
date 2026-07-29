<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import StatusNotice from "../components/StatusNotice.vue";
import { apiRequest } from "../services/api.js";

const couriers = ref([]);
const editingId = ref(null);
const loading = ref(true);
const error = ref("");
const success = ref("");
const form = reactive({
  chat_id: "",
  nombre: "",
  telefono: "",
  activo: true,
});

const formTitle = computed(() =>
  editingId.value ? "Editar repartidor" : "Registrar repartidor",
);

function resetForm() {
  editingId.value = null;
  Object.assign(form, {
    chat_id: "",
    nombre: "",
    telefono: "",
    activo: true,
  });
}

async function loadCouriers() {
  loading.value = true;
  error.value = "";
  try {
    couriers.value = await apiRequest("/repartidores");
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

function editCourier(courier) {
  editingId.value = courier.id;
  Object.assign(form, {
    chat_id: courier.chat_id,
    nombre: courier.nombre || "",
    telefono: courier.telefono || "",
    activo: courier.activo,
  });
}

async function saveCourier() {
  error.value = "";
  success.value = "";
  const editing = editingId.value !== null;
  try {
    await apiRequest(
      editing ? `/repartidores/${editingId.value}` : "/repartidores",
      {
        method: editing ? "PUT" : "POST",
        body: JSON.stringify({
          chat_id: form.chat_id,
          nombre: form.nombre || null,
          telefono: form.telefono || null,
          activo: form.activo,
        }),
      },
    );
    success.value = editing
      ? "Repartidor actualizado."
      : "Repartidor registrado.";
    resetForm();
    await loadCouriers();
  } catch (requestError) {
    error.value = requestError.message;
  }
}

async function disableCourier(courier) {
  if (!window.confirm(`¿Deshabilitar a ${courier.nombre || courier.chat_id}?`)) {
    return;
  }
  try {
    await apiRequest(`/repartidores/${courier.id}`, { method: "DELETE" });
    success.value = "Repartidor deshabilitado.";
    await loadCouriers();
  } catch (requestError) {
    error.value = requestError.message;
  }
}

onMounted(loadCouriers);
</script>

<template>
  <header class="page-header">
    <div>
      <p class="eyebrow">Equipo de entrega</p>
      <h2>Repartidores</h2>
      <p class="muted">
        Solo los chats registrados y activos pueden utilizar los comandos de reparto.
      </p>
    </div>
  </header>

  <StatusNotice :message="error" kind="error" />
  <StatusNotice :message="success" kind="success" />

  <section class="panel form-panel">
    <div class="section-heading">
      <h3>{{ formTitle }}</h3>
      <button v-if="editingId" class="text-button" type="button" @click="resetForm">
        Cancelar edición
      </button>
    </div>
    <form class="form-grid" @submit.prevent="saveCourier">
      <label>
        Chat ID de Telegram
        <input v-model.trim="form.chat_id" required maxlength="100" />
      </label>
      <label>
        Nombre
        <input v-model.trim="form.nombre" maxlength="150" />
      </label>
      <label>
        Teléfono
        <input v-model.trim="form.telefono" maxlength="50" />
      </label>
      <label class="check-field">
        <input v-model="form.activo" type="checkbox" />
        Acceso habilitado
      </label>
      <button class="button button-primary align-end" type="submit">
        Guardar repartidor
      </button>
    </form>
  </section>

  <section class="panel">
    <h3>Repartidores registrados</h3>
    <p v-if="loading" class="empty-state">Cargando repartidores…</p>
    <p v-else-if="!couriers.length" class="empty-state">
      No existen repartidores registrados.
    </p>
    <div v-else class="card-grid">
      <article v-for="courier in couriers" :key="courier.id" class="dish-card">
        <div class="dish-card-top">
          <span class="status-chip" :class="{ inactive: !courier.activo }">
            {{ courier.activo ? "Habilitado" : "Deshabilitado" }}
          </span>
          <small>Chat {{ courier.chat_id }}</small>
        </div>
        <h4>{{ courier.nombre || `Repartidor #${courier.id}` }}</h4>
        <p>{{ courier.telefono || "Sin teléfono registrado." }}</p>
        <div class="card-actions">
          <button class="button button-secondary" @click="editCourier(courier)">
            Editar
          </button>
          <button
            v-if="courier.activo"
            class="button button-danger"
            @click="disableCourier(courier)"
          >
            Deshabilitar
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
