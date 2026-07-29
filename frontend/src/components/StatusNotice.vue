<script setup>
defineProps({
  message: { type: String, default: "" },
  kind: { type: String, default: "info" },
});
</script>

<template>
  <p v-if="message" class="notice" :class="`notice-${kind}`" role="status">
    {{ message }}
  </p>
</template>
