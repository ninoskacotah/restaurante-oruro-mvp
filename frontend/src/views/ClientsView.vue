<script setup>
import { onMounted, ref } from "vue";

import StatusNotice from "../components/StatusNotice.vue";
import { apiRequest } from "../services/api.js";

const clients = ref([]);
const detail = ref(null);
const loading = ref(true);
const error = ref("");

async function loadClients() {
  try {
    clients.value = await apiRequest("/clientes");
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

async function selectClient(id) {
  error.value = "";
  try {
    detail.value = await apiRequest(`/clientes/${id}`);
  } catch (requestError) {
    error.value = requestError.message;
  }
}

onMounted(loadClients);
</script>

<template>
  <header class="page-header">
    <div>
      <p class="eyebrow">Relación con clientes</p>
      <h2>Fichas e historial</h2>
      <p class="muted">La frecuencia se calcula a partir de pedidos persistidos.</p>
    </div>
  </header>
  <StatusNotice :message="error" kind="error" />
  <div class="clients-layout">
    <section class="panel client-list">
      <p v-if="loading" class="empty-state">Cargando clientes…</p>
      <button
        v-for="client in clients"
        v-else
        :key="client.id"
        type="button"
        @click="selectClient(client.id)"
      >
        <strong>{{ client.nombre || `Cliente #${client.id}` }}</strong>
        <span>Chat ID: {{ client.chat_id }}</span>
      </button>
    </section>
    <section v-if="detail" class="panel">
      <p class="eyebrow">Ficha del cliente</p>
      <h3>{{ detail.cliente.nombre || `Cliente #${detail.cliente.id}` }}</h3>
      <div class="metric-strip">
        <div>
          <strong>{{ detail.frecuencia_pedidos }}</strong>
          <span>pedidos válidos</span>
        </div>
        <div>
          <strong>{{ detail.cliente.telefono || "No registrado" }}</strong>
          <span>contacto</span>
        </div>
        <div>
          <strong>{{ detail.cliente.chat_id }}</strong>
          <span>Chat ID de Telegram</span>
        </div>
      </div>
      <h4>Historial de pedidos</h4>
      <ul class="line-list">
        <li v-for="order in detail.pedidos" :key="order.id">
          <span>{{ order.codigo_seguimiento || `Pedido #${order.id}` }}</span>
          <strong>{{ order.estado_actual }} · Bs {{ Number(order.total).toFixed(2) }}</strong>
        </li>
      </ul>
    </section>
    <section v-else class="panel empty-state">
      Selecciona un cliente para consultar su ficha.
    </section>
  </div>
</template>
