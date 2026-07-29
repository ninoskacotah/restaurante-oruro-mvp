<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";

import DeliveryMap from "../components/DeliveryMap.vue";
import StatusNotice from "../components/StatusNotice.vue";
import { apiObjectUrl, apiRequest } from "../services/api.js";

const orders = ref([]);
const detail = ref(null);
const history = ref([]);
const tracking = ref(null);
const couriers = ref([]);
const selectedId = ref(null);
const filter = ref("");
const loading = ref(true);
const error = ref("");
const success = ref("");
const receiptUrls = reactive({});
const assignment = ref("");

const filteredOrders = computed(() =>
  orders.value.filter(
    (order) => !filter.value || order.estado_actual === filter.value,
  ),
);
const states = computed(() => [
  ...new Set(orders.value.map((order) => order.estado_actual)),
]);
const activeAssignment = computed(() =>
  detail.value?.asignaciones.find((item) => item.activa),
);

function formatDate(value) {
  return value ? new Intl.DateTimeFormat("es-BO", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value)) : "Sin registro";
}

async function loadOrders() {
  loading.value = true;
  error.value = "";
  try {
    orders.value = await apiRequest("/pedidos");
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

function releaseReceiptUrls() {
  Object.values(receiptUrls).forEach((url) => URL.revokeObjectURL(url));
  Object.keys(receiptUrls).forEach((key) => delete receiptUrls[key]);
}

async function selectOrder(orderId) {
  selectedId.value = orderId;
  error.value = "";
  releaseReceiptUrls();
  try {
    const [orderDetail, orderHistory, orderTracking, availableCouriers] =
      await Promise.all([
        apiRequest(`/pedidos/${orderId}`),
        apiRequest(`/pedidos/${orderId}/historial`),
        apiRequest(`/pedidos/${orderId}/seguimiento`),
        apiRequest("/repartidores"),
      ]);
    detail.value = orderDetail;
    history.value = orderHistory;
    tracking.value = orderTracking;
    couriers.value = availableCouriers;
    assignment.value = activeAssignment.value?.repartidor_id || "";
    for (const receipt of orderDetail.comprobantes) {
      try {
        receiptUrls[receipt.id] = await apiObjectUrl(
          `/comprobantes/${receipt.id}/archivo`,
        );
      } catch {
        receiptUrls[receipt.id] = "";
      }
    }
  } catch (requestError) {
    error.value = requestError.message;
  }
}

async function reviewReceipt(receipt, approved) {
  const observation = window.prompt(
    approved ? "Observación opcional:" : "Motivo del rechazo:",
    "",
  );
  if (observation === null) return;
  try {
    await apiRequest(`/comprobantes/${receipt.id}/revision`, {
      method: "POST",
      body: JSON.stringify({ aprobado: approved, observacion: observation || null }),
    });
    success.value = approved ? "Pago confirmado manualmente." : "Comprobante rechazado.";
    await loadOrders();
    await selectOrder(selectedId.value);
  } catch (requestError) {
    error.value = requestError.message;
  }
}

async function assignCourier() {
  if (!assignment.value) return;
  try {
    await apiRequest(`/pedidos/${selectedId.value}/asignaciones`, {
      method: "POST",
      body: JSON.stringify({ repartidor_id: Number(assignment.value) }),
    });
    success.value = activeAssignment.value
      ? "Pedido reasignado."
      : "Repartidor asignado.";
    await loadOrders();
    await selectOrder(selectedId.value);
  } catch (requestError) {
    error.value = requestError.message;
  }
}

onMounted(loadOrders);
onBeforeUnmount(releaseReceiptUrls);
</script>

<template>
  <header class="page-header">
    <div>
      <p class="eyebrow">Operación</p>
      <h2>Tablero de pedidos</h2>
      <p class="muted">Revisa pagos, asignaciones y seguimiento en tiempo real.</p>
    </div>
    <select v-model="filter" class="compact-select" aria-label="Filtrar por estado">
      <option value="">Todos los estados</option>
      <option v-for="state in states" :key="state" :value="state">{{ state }}</option>
    </select>
  </header>

  <StatusNotice :message="error" kind="error" />
  <StatusNotice :message="success" kind="success" />

  <div class="orders-layout">
    <section class="panel order-list">
      <p v-if="loading" class="empty-state">Cargando pedidos…</p>
      <p v-else-if="!filteredOrders.length" class="empty-state">
        No existen pedidos para este filtro.
      </p>
      <button
        v-for="order in filteredOrders"
        v-else
        :key="order.id"
        class="order-item"
        :class="{ active: selectedId === order.id }"
        type="button"
        @click="selectOrder(order.id)"
      >
        <span>
          <strong>{{ order.codigo_seguimiento || `Pedido #${order.id}` }}</strong>
          <small>{{ formatDate(order.fecha_creacion) }}</small>
        </span>
        <span>
          <strong>Bs {{ Number(order.total).toFixed(2) }}</strong>
          <small>{{ order.estado_actual }}</small>
        </span>
      </button>
    </section>

    <div v-if="detail" class="order-detail">
      <section class="panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">Detalle</p>
            <h3>{{ detail.pedido.codigo_seguimiento }}</h3>
          </div>
          <span class="status-chip">{{ detail.pedido.estado_actual }}</span>
        </div>
        <div class="detail-grid">
          <div>
            <span>Total</span>
            <strong>Bs {{ Number(detail.pedido.total).toFixed(2) }}</strong>
          </div>
          <div>
            <span>Referencia</span>
            <strong>{{ detail.pedido.referencia_entrega || "Sin referencia" }}</strong>
          </div>
        </div>
        <ul class="line-list">
          <li v-for="line in detail.detalles" :key="line.id">
            <span>{{ line.cantidad }} × {{ line.nombre_plato }}</span>
            <strong>Bs {{ Number(line.subtotal).toFixed(2) }}</strong>
          </li>
        </ul>
      </section>

      <section class="panel">
        <h3>Comprobantes</h3>
        <p v-if="!detail.comprobantes.length" class="empty-state">
          El cliente todavía no envió un comprobante.
        </p>
        <article
          v-for="receipt in detail.comprobantes"
          :key="receipt.id"
          class="receipt-card"
        >
          <img
            v-if="receiptUrls[receipt.id]"
            :src="receiptUrls[receipt.id]"
            alt="Comprobante enviado por el cliente"
          />
          <div>
            <strong>{{ receipt.estado_revision }}</strong>
            <p>{{ formatDate(receipt.fecha_envio) }}</p>
            <div v-if="receipt.estado_revision === 'PENDIENTE'" class="card-actions">
              <button class="button button-primary" @click="reviewReceipt(receipt, true)">
                Confirmar pago
              </button>
              <button class="button button-danger" @click="reviewReceipt(receipt, false)">
                Rechazar
              </button>
            </div>
          </div>
        </article>
      </section>

      <section class="panel">
        <h3>Asignación del reparto</h3>
        <form class="assignment-form" @submit.prevent="assignCourier">
          <select v-model="assignment" required>
            <option value="" disabled>Selecciona un repartidor</option>
            <option v-for="courier in couriers" :key="courier.id" :value="courier.id">
              {{ courier.nombre || `Repartidor #${courier.id}` }}
            </option>
          </select>
          <button class="button button-primary" type="submit">
            {{ activeAssignment ? "Reasignar" : "Asignar" }}
          </button>
        </form>
        <p v-if="activeAssignment" class="muted">
          Asignación activa #{{ activeAssignment.id }}
          <span v-if="activeAssignment.fecha_acuse">
            · Acuse {{ formatDate(activeAssignment.fecha_acuse) }}
          </span>
        </p>
      </section>

      <section class="panel">
        <h3>Seguimiento</h3>
        <DeliveryMap
          :destination="{
            latitud: detail.pedido.entrega_latitud,
            longitud: detail.pedido.entrega_longitud,
          }"
          :courier="tracking"
        />
        <p v-if="detail.pedido.estado_actual === 'EN_DESTINO'" class="arrival-badge">
          El repartidor registró su llegada.
        </p>
      </section>

      <section class="panel">
        <h3>Historial de estados</h3>
        <ol class="timeline">
          <li v-for="event in history" :key="event.id">
            <span>{{ event.estado_nuevo }}</span>
            <small>{{ event.evento }} · {{ formatDate(event.fecha_registro) }}</small>
          </li>
        </ol>
      </section>
    </div>
    <section v-else class="panel empty-state">
      Selecciona un pedido para revisar su operación.
    </section>
  </div>
</template>
