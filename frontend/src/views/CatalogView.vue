<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import StatusNotice from "../components/StatusNotice.vue";
import { apiRequest } from "../services/api.js";

const dishes = ref([]);
const loading = ref(true);
const saving = ref(false);
const error = ref("");
const success = ref("");
const editingId = ref(null);
const form = reactive({
  nombre: "",
  descripcion: "",
  precio: "",
  activo: true,
});

const formTitle = computed(() =>
  editingId.value ? "Editar plato" : "Registrar plato",
);

function resetForm() {
  editingId.value = null;
  Object.assign(form, {
    nombre: "",
    descripcion: "",
    precio: "",
    activo: true,
  });
}

async function loadDishes() {
  loading.value = true;
  error.value = "";
  try {
    dishes.value = await apiRequest("/platos");
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

function editDish(dish) {
  editingId.value = dish.id;
  Object.assign(form, {
    nombre: dish.nombre,
    descripcion: dish.descripcion || "",
    precio: dish.precio,
    activo: dish.activo,
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function saveDish() {
  saving.value = true;
  error.value = "";
  success.value = "";
  const editing = editingId.value !== null;
  try {
    await apiRequest(editing ? `/platos/${editingId.value}` : "/platos", {
      method: editing ? "PUT" : "POST",
      body: JSON.stringify({
        ...form,
        descripcion: form.descripcion || null,
        precio: Number(form.precio),
      }),
    });
    success.value = editing ? "Plato actualizado." : "Plato registrado.";
    resetForm();
    await loadDishes();
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    saving.value = false;
  }
}

async function disableDish(dish) {
  if (!window.confirm(`¿Desactivar “${dish.nombre}”?`)) return;
  error.value = "";
  try {
    await apiRequest(`/platos/${dish.id}`, { method: "DELETE" });
    success.value = "Plato desactivado.";
    await loadDishes();
  } catch (requestError) {
    error.value = requestError.message;
  }
}

onMounted(loadDishes);
</script>

<template>
  <header class="page-header">
    <div>
      <p class="eyebrow">Catálogo</p>
      <h2>Platos del restaurante</h2>
      <p class="muted">Administra la información que podrá utilizar el menú diario.</p>
    </div>
    <span class="count-pill">{{ dishes.length }} platos</span>
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
    <form class="form-grid" @submit.prevent="saveDish">
      <label>
        Nombre
        <input v-model.trim="form.nombre" required maxlength="150" />
      </label>
      <label>
        Precio (Bs)
        <input v-model="form.precio" type="number" min="0" step="0.01" required />
      </label>
      <label class="span-two">
        Descripción
        <textarea v-model.trim="form.descripcion" rows="3" maxlength="500" />
      </label>
      <label class="check-field">
        <input v-model="form.activo" type="checkbox" />
        Plato activo
      </label>
      <button class="button button-primary align-end" type="submit" :disabled="saving">
        {{ saving ? "Guardando…" : "Guardar plato" }}
      </button>
    </form>
  </section>

  <section class="panel">
    <div class="section-heading">
      <h3>Catálogo registrado</h3>
      <button class="text-button" type="button" @click="loadDishes">Actualizar</button>
    </div>
    <p v-if="loading" class="empty-state">Cargando platos…</p>
    <p v-else-if="!dishes.length" class="empty-state">No existen platos registrados.</p>
    <div v-else class="card-grid">
      <article v-for="dish in dishes" :key="dish.id" class="dish-card">
        <div class="dish-card-top">
          <span class="status-chip" :class="{ inactive: !dish.activo }">
            {{ dish.activo ? "Activo" : "Inactivo" }}
          </span>
          <strong>Bs {{ Number(dish.precio).toFixed(2) }}</strong>
        </div>
        <h4>{{ dish.nombre }}</h4>
        <p>{{ dish.descripcion || "Sin descripción." }}</p>
        <div class="card-actions">
          <button class="button button-secondary" type="button" @click="editDish(dish)">
            Editar
          </button>
          <button
            v-if="dish.activo"
            class="button button-danger"
            type="button"
            @click="disableDish(dish)"
          >
            Desactivar
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
