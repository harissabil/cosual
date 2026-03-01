<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-mono font-medium"
    :class="badgeClass"
  >
    <span v-if="status === 'processing'" class="w-1.5 h-1.5 rounded-full bg-current mr-1.5 pulse-amber" />
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const badgeClass = computed(() => {
  switch (props.status) {
    case 'pending':
      return 'bg-muted/20 text-muted'
    case 'processing':
      return 'bg-accent-2/20 text-accent-2'
    case 'completed':
      return 'bg-success/20 text-success'
    case 'failed':
      return 'bg-danger/20 text-danger'
    default:
      return 'bg-muted/20 text-muted'
  }
})

const label = computed(() => {
  switch (props.status) {
    case 'pending': return 'Pending'
    case 'processing': return 'Processing'
    case 'completed': return 'Completed'
    case 'failed': return 'Failed'
    default: return props.status
  }
})
</script>

