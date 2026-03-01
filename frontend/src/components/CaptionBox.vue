<template>
  <div class="rounded-xl bg-surface-2 border border-border p-4 relative">
    <!-- Platform chip -->
    <div class="flex items-center justify-between mb-3">
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-accent-soft text-accent">
        {{ platformLabel }}
      </span>
      <button
        @click="copyCaption"
        class="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono border border-border text-muted hover:text-text hover:border-border-2 transition-all duration-200"
      >
        <svg v-if="!copied" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
          <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
        {{ copied ? 'Copied!' : 'Copy Caption' }}
      </button>
    </div>
    <!-- Caption text -->
    <p class="text-sm text-text leading-relaxed whitespace-pre-wrap" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
      {{ caption || 'No caption available.' }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  caption: { type: String, default: '' },
  platform: { type: String, default: '' },
})

const copied = ref(false)

const platformLabel = computed(() => {
  const map = { linkedin: 'LinkedIn', instagram: 'Instagram', tiktok: 'TikTok' }
  return map[props.platform] || props.platform || 'Post'
})

async function copyCaption() {
  if (!props.caption) return
  try {
    await navigator.clipboard.writeText(props.caption)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    console.error('Failed to copy')
  }
}
</script>

