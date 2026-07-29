<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import StatusNotice from "../components/StatusNotice.vue";
import { apiRequest } from "../services/api.js";

const menus = ref([]);
const dishes = ref([]);
const details = ref([]);
const selectedId = ref(null);
const date = ref(new Date().toISOString().slice(0, 10));
const loading = ref(true);
const error = ref("");
const success = ref("");
const offer = reactive({ plato_id: "", stock: 0, disponible: true });

const selectedMenu = computed(() =>
  menus.value.find((menu) => menu.id === selectedId.value),
);
const dishMap = computed(() =>
  Object.fromEntries(dishes.value.map((dish) => [dish.id, dish])),
);
const availableDishes = computed(() => {
  const existing = new Set(details.value.map((detail) => detail.plato_id));
  return dishes.value.filter((dish) => dish.activo && !existing.has(dish.id));
});

async function loadBase() {
  loading.value = true;
  error.value = "";
  try {
    [menus.value, dishes.value] = await Promise.all([
      apiRequest("/menus"),
      apiRequest("/platos"),
    ]);
    if (!selectedId.value && menus.value.length) {
      await selectMenu(menus.value[0].id);
    }
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

async function selectMenu(menuId) {
  selectedId.value = Number(menuId);
  error.value = "";
  try {
    details.value = await apiRequest(`/menus/${selectedId.value}/detalles`);
  } catch (requestError) {
    error.value = requestError.message;
  }
}

async function createOrSelectMenu() {
  error.value = "";
  success.value = "";
  try {
    const menu = await apiRequest("/menus", {
      method: "POST",
      body: JSON.stringify({ fecha: date.value }),
    });
    success.value = "Menú seleccionado para la fecha indicada.";
    await loadBase();
    await selectMenu(menu.id);
  } catch (requestError) {
    error.value = requestError.message;
  }
}

async function toggleMenu() {
  if (!selectedMenu.value) return;
  try {
    await apiRequest(`/menus/${selectedMenu.value.id}`, {
      method: "PATCH",
      body: JSON.stringify({ activo: !selectedMenu.value.activo }),
    });
    success.value = "Estado del menú actualizado.";
    await loadBase();
  } catch (requestError) {
    error.value = requestError.message;
  }
}

async function addOffer() {
  if (!selectedMenu.value) return;
  error.value = "";
  try {
    await apiRequest(`/menus/${selectedMenu.value.id}/detalles`, {
      method: "POST",
      body: JSON.stringify({
        plato_id: Number(offer.plato_id),
        stock: Number(offer.stock),
        disponible: offer.disponible,
      }),
    });
    Object.assign(offer, { plato_id: "", stock: 0, disponible: true });
    success.value = "Plato incorporado al menú.";
    await selectMenu(selectedMenu.value.id);
  } catch (requestError) {
    error.value = requestError.message;
  }
}

async function updateOffer(detail) {
  error.value = "";
  try {
    await apiRequest(`/menus/detalles/${detail.id}`, {
      method: "PATCH",
      body: JSON.stringify({
        stock: Number(detail.stock),
        disponible: detail.disponible,
      }),
    });
    success.value = "Disponibilidad actualizada.";
    await selectMenu(selectedMenu.value.id);
  } catch (requestError) {
    error.value = requestError.message;
  }
}

onMounted(loadBase);
</script>

<template>
  <header class="page-header">
    <div>
      <p class="eyebrow">Programación</p>
      <h2>Menús por fecha</h2>
      <p class="muted">Define qué platos estarán visibles y su stock disponible.</p>
    </div>
  </header>

  <StatusNotice :message="error" kind="error" />
  <StatusNotice :message="success" kind="success" />

  <section class="panel date-panel">
    <label>
      Fecha del menú
      <input v-model="date" type="date" required />
    </label>
    <button class="button button-primary" type="button" @click="createOrSelectMenu">
      Abrir o crear menú
    </button>
  </section>

  <section v-if="menus.length" class="menu-tabs" aria-label="Menús existentes">
    <button
      v-for="menu in menus"
      :key="menu.id"
      type="button"
      :class="{ active: selectedId === menu.id }"
      @click="selectMenu(menu.id)"
    >
      {{ menu.fecha }}
      <span>{{ menu.activo ? "Activo" : "Inactivo" }}</span>
    </button>
  </section>

  <p v-if="loading" class="empty-state">Cargando programación…</p>

  <template v-else-if="selectedMenu">
    <section class="panel menu-summary">
      <div>
        <p class="eyebrow">Menú seleccionado</p>
        <h3>{{ selectedMenu.fecha }}</h3>
      </div>
      <button
        class="button"
        :class="selectedMenu.activo ? 'button-danger' : 'button-primary'"
        type="button"
        @click="toggleMenu"
      >
        {{ selectedMenu.activo ? "Desactivar menú" : "Activar menú" }}
      </button>
    </section>

    <section class="panel">
      <h3>Agregar plato al menú</h3>
      <form class="form-grid offer-form" @submit.prevent="addOffer">
        <label>
          Plato
          <select v-model="offer.plato_id" required>
            <option value="" disabled>Selecciona un plato</option>
            <option v-for="dish in availableDishes" :key="dish.id" :value="dish.id">
              {{ dish.nombre }}
            </option>
          </select>
        </label>
        <label>
          Stock
          <input v-model="offer.stock" type="number" min="0" required />
        </label>
        <label class="check-field">
          <input v-model="offer.disponible" type="checkbox" />
          Disponible
        </label>
        <button class="button button-primary align-end" type="submit">
          Incorporar
        </button>
      </form>
    </section>

    <section class="panel">
      <h3>Oferta programada</h3>
      <p v-if="!details.length" class="empty-state">
        Este menú todavía no contiene platos.
      </p>
      <div v-else class="offer-list">
        <form
          v-for="detail in details"
          :key="detail.id"
          class="offer-row"
          @submit.prevent="updateOffer(detail)"
        >
          <div>
            <strong>{{ dishMap[detail.plato_id]?.nombre || "Plato registrado" }}</strong>
            <small>Bs {{ Number(dishMap[detail.plato_id]?.precio || 0).toFixed(2) }}</small>
          </div>
          <label>
            Stock
            <input v-model="detail.stock" type="number" min="0" required />
          </label>
          <label class="check-field">
            <input v-model="detail.disponible" type="checkbox" />
            Visible
          </label>
          <button class="button button-secondary" type="submit">Actualizar</button>
        </form>
      </div>
    </section>
  </template>
</template>
