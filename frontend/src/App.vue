<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppNav from '@/components/AppNav.vue'

const route = useRoute()

const showNav = computed(() => route.name !== 'landing')
</script>

<template>
  <AppNav v-if="showNav" />
  <router-view />
</template>

