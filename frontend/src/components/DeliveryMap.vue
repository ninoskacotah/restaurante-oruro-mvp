<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const props = defineProps({
  destination: { type: Object, default: null },
  courier: { type: Object, default: null },
});

const mapElement = ref(null);
const now = ref(Date.now());
let map;
let destinationMarker;
let courierMarker;
let freshnessInterval;

const stale = computed(() => {
  if (!props.courier?.fecha_registro) return false;
  return now.value - new Date(props.courier.fecha_registro).getTime() > 30_000;
});

const lastUpdate = computed(() => {
  if (!props.courier?.fecha_registro) return "Sin ubicación del repartidor";
  return `Última actualización: ${new Intl.DateTimeFormat("es-BO", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(props.courier.fecha_registro))}`;
});

function coordinate(point) {
  if (point?.latitud == null || point?.longitud == null) return null;
  return [Number(point.latitud), Number(point.longitud)];
}

async function renderMarkers() {
  await nextTick();
  if (!mapElement.value) return;
  if (!map) {
    map = L.map(mapElement.value).setView([-17.97, -67.11], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap",
      maxZoom: 19,
    }).addTo(map);
  }
  if (destinationMarker) destinationMarker.remove();
  if (courierMarker) courierMarker.remove();
  const points = [];
  const destination = coordinate(props.destination);
  const courier = coordinate(props.courier);
  if (destination) {
    destinationMarker = L.circleMarker(destination, {
      radius: 9,
      color: "#a94f35",
      fillOpacity: 0.9,
    })
      .bindPopup("Destino del pedido")
      .addTo(map);
    points.push(destination);
  }
  if (courier) {
    courierMarker = L.circleMarker(courier, {
      radius: 9,
      color: stale.value ? "#746a62" : "#3d604b",
      fillOpacity: 0.9,
    })
      .bindPopup(stale.value ? "Última ubicación (desactualizada)" : "Repartidor")
      .addTo(map);
    points.push(courier);
  }
  if (points.length === 1) map.setView(points[0], 15);
  if (points.length > 1) map.fitBounds(points, { padding: [28, 28] });
  setTimeout(() => map?.invalidateSize(), 0);
}

watch(() => [props.destination, props.courier], renderMarkers, { deep: true });
watch(stale, renderMarkers);
onMounted(() => {
  renderMarkers();
  freshnessInterval = window.setInterval(() => {
    now.value = Date.now();
  }, 5_000);
});
onBeforeUnmount(() => {
  window.clearInterval(freshnessInterval);
  map?.remove();
});
</script>

<template>
  <div class="map-wrap">
    <div ref="mapElement" class="delivery-map" aria-label="Mapa del reparto" />
    <p class="muted">{{ lastUpdate }}</p>
    <p v-if="stale" class="map-warning">
      La última ubicación tiene más de 30 segundos y puede estar desactualizada.
    </p>
  </div>
</template>
