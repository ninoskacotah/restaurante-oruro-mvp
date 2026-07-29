<script setup>
import { onMounted, ref } from "vue";

import StatusNotice from "../components/StatusNotice.vue";
import { apiRequest } from "../services/api.js";

const date = ref(new Date().toISOString().slice(0, 10));
const report = ref(null);
const loading = ref(false);
const error = ref("");

async function loadReport() {
  loading.value = true;
  error.value = "";
  try {
    report.value = await apiRequest(`/reportes?fecha=${date.value}`);
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadReport);
</script>

<template>
  <header class="page-header">
    <div>
      <p class="eyebrow">Indicadores</p>
      <h2>Reportes operativos</h2>
      <p class="muted">Todas las cifras proceden de pedidos almacenados.</p>
    </div>
    <form class="report-date" @submit.prevent="loadReport">
      <input v-model="date" type="date" required />
      <button class="button button-primary" type="submit">Consultar</button>
    </form>
  </header>
  <StatusNotice :message="error" kind="error" />
  <p v-if="loading" class="empty-state">Calculando reportes…</p>
  <template v-else-if="report">
    <section class="report-grid">
      <article class="metric-card featured">
        <span>Ventas del día</span>
        <strong>Bs {{ Number(report.ventas_dia).toFixed(2) }}</strong>
        <small>{{ report.pedidos_contabilizados }} pedidos contabilizados</small>
      </article>
      <article class="metric-card">
        <span>Tiempo promedio de entrega</span>
        <strong>
          {{
            report.tiempo_promedio_entrega_minutos == null
              ? "Sin datos"
              : `${Number(report.tiempo_promedio_entrega_minutos).toFixed(2)} min`
          }}
        </strong>
        <small>Desde EN_CAMINO hasta ENTREGADO</small>
      </article>
    </section>
    <section class="panel">
      <h3>Platos más pedidos</h3>
      <p v-if="!report.platos_mas_pedidos.length" class="empty-state">
        No existen ventas contabilizadas para esta fecha.
      </p>
      <ol v-else class="ranking">
        <li v-for="dish in report.platos_mas_pedidos" :key="dish.plato_id">
          <span>{{ dish.nombre }}</span>
          <strong>{{ dish.cantidad }} unidades</strong>
        </li>
      </ol>
    </section>
  </template>
</template>
