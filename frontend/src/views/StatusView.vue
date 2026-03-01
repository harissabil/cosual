<template>
  <div class="pt-20 pb-12 px-6 max-w-3xl mx-auto">
    <!-- Loading / Pending / Processing -->
    <div v-if="!status || status.status === 'pending' || status.status === 'processing'" class="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h2 v-if="status?.title" class="font-display font-bold text-2xl text-text mb-8">
        {{ status.title }}
      </h2>

      <!-- Waveform loader -->
      <div class="waveform-loader mb-6">
        <span /><span /><span /><span /><span />
      </div>

      <p class="font-mono text-sm text-muted">
        generating {{ status?.output_type || 'content' }}<span class="animated-dots" />
      </p>
      <p class="font-mono text-xs text-muted/50 mt-3">This usually takes 20–40 seconds</p>
    </div>

    <!-- Completed — Image -->
    <div v-else-if="status.status === 'completed' && status.output_type === 'image'" class="space-y-6">
      <h2 class="font-display font-bold text-2xl text-text">{{ status.title }}</h2>
      <div class="glass-card p-3 inline-block">
        <img
          :src="mediaUrl(status.output_url)"
          :alt="status.title"
          class="rounded-xl max-h-[60vh] w-auto mx-auto"
        />
      </div>
      <CaptionBox :caption="status.caption" :platform="platform" />
      <ShareLinkedIn
        v-if="platform === 'linkedin'"
        :url="mediaUrl(status.output_url)"
        :title="status.title"
        :summary="status.caption || ''"
      />
      <div class="flex gap-3">
        <router-link
          :to="`/history/${status.job_id}`"
          class="flex-1 py-3 rounded-xl font-display font-bold text-sm text-center border border-accent text-accent hover:bg-accent-soft transition-all duration-200"
        >
          View in History →
        </router-link>
        <router-link
          to="/generate"
          class="flex-1 py-3 rounded-xl font-display font-bold text-sm text-center bg-surface-2 border border-border text-muted hover:text-text hover:border-border-2 transition-all duration-200"
        >
          Generate Another
        </router-link>
      </div>
    </div>

    <!-- Completed — Video -->
    <div v-else-if="status.status === 'completed' && status.output_type === 'video'" class="space-y-6">
      <h2 class="font-display font-bold text-2xl text-text">{{ status.title }}</h2>
      <div class="glass-card p-3">
        <video
          :src="mediaUrl(status.output_url)"
          autoplay
          muted
          loop
          controls
          class="rounded-xl w-full max-h-[60vh]"
        />
      </div>
      <CaptionBox :caption="status.caption" :platform="platform" />
      <ShareLinkedIn
        v-if="platform === 'linkedin'"
        :url="mediaUrl(status.output_url)"
        :title="status.title"
        :summary="status.caption || ''"
      />
      <div class="flex gap-3">
        <router-link
          :to="`/history/${status.job_id}`"
          class="flex-1 py-3 rounded-xl font-display font-bold text-sm text-center border border-accent text-accent hover:bg-accent-soft transition-all duration-200"
        >
          View in History →
        </router-link>
        <router-link
          to="/generate"
          class="flex-1 py-3 rounded-xl font-display font-bold text-sm text-center bg-surface-2 border border-border text-muted hover:text-text hover:border-border-2 transition-all duration-200"
        >
          Generate Another
        </router-link>
      </div>
    </div>

    <!-- Failed -->
    <div v-else-if="status.status === 'failed'" class="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <div class="w-16 h-16 rounded-full bg-danger/20 flex items-center justify-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 text-danger" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
      </div>
      <h2 class="font-display font-bold text-xl text-text mb-3">Generation Failed</h2>
      <p class="font-mono text-sm text-danger mb-8">{{ status.error_message || 'An unknown error occurred.' }}</p>
      <router-link
        to="/generate"
        class="px-8 py-3 rounded-xl font-display font-bold text-sm bg-accent text-bg glow-accent hover:opacity-90 transition-all duration-200"
      >
        Try Again →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGenerateStore } from '@/stores/generate'
import { mediaUrl } from '@/api/client'
import CaptionBox from '@/components/CaptionBox.vue'
import ShareLinkedIn from '@/components/ShareLinkedIn.vue'

const route = useRoute()
const generateStore = useGenerateStore()

const status = computed(() => generateStore.currentStatus)
const platform = computed(() => generateStore.platform)

onMounted(() => {
  generateStore.startPolling(route.params.id)
})

onUnmounted(() => {
  generateStore.stopPolling()
})
</script>

