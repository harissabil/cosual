<template>
  <div class="pt-20 pb-12 px-6 max-w-6xl mx-auto">
    <div class="mb-8">
      <h1 class="font-display font-bold text-3xl text-text">Your Generations</h1>
      <p class="font-mono text-sm text-muted mt-1">Stored locally on this device</p>
    </div>

    <!-- Empty state -->
    <div v-if="!historyStore.items.length" class="flex flex-col items-center justify-center min-h-[40vh] text-center">
      <div class="w-20 h-20 rounded-2xl bg-surface-2 border border-border flex items-center justify-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>
      <p class="font-display font-medium text-lg text-text mb-2">No generations yet</p>
      <p class="font-mono text-sm text-muted mb-6">Create your first visual from code or ideas</p>
      <router-link
        to="/generate"
        class="px-8 py-3 rounded-xl font-display font-bold text-sm bg-accent text-bg glow-accent hover:opacity-90 transition-all duration-200"
      >
        Start Creating →
      </router-link>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <router-link
        v-for="item in historyStore.items"
        :key="item.job_id"
        :to="`/history/${item.job_id}`"
        class="glass-card overflow-hidden group hover:border-accent/50 hover:scale-[1.02] transition-all duration-300 block"
      >
        <!-- Thumbnail -->
        <div class="aspect-video bg-surface-2 overflow-hidden">
          <img
            v-if="item.output_url && item.output_type === 'image'"
            :src="mediaUrl(item.output_url)"
            :alt="item.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div
            v-else-if="item.output_type === 'video'"
            class="w-full h-full flex items-center justify-center"
          >
            <div class="w-14 h-14 rounded-full bg-accent/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
            </div>
          </div>
          <div v-else class="w-full h-full flex items-center justify-center">
            <div class="waveform-loader">
              <span /><span /><span /><span /><span />
            </div>
          </div>
        </div>

        <!-- Info -->
        <div class="p-4">
          <h3 class="font-display font-bold text-sm text-text truncate mb-2">
            {{ item.title || 'Untitled' }}
          </h3>
          <div class="flex items-center gap-2">
            <StatusBadge :status="item.status" />
            <span class="px-2 py-0.5 rounded text-xs font-mono bg-surface-2 text-muted border border-border">
              {{ item.output_type }}
            </span>
            <span class="ml-auto font-mono text-xs text-muted">
              {{ formatDate(item.created_at) }}
            </span>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useHistoryStore } from '@/stores/history'
import { mediaUrl } from '@/api/client'
import StatusBadge from '@/components/StatusBadge.vue'

const historyStore = useHistoryStore()

onMounted(() => {
  historyStore.loadFromStorage()
  historyStore.fetchMyHistory()
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

