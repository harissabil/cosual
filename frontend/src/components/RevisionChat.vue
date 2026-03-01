<template>
  <div class="space-y-3">
    <div class="flex gap-2">
      <textarea
        v-model="instruction"
        :disabled="loading"
        rows="2"
        placeholder="Describe changes to make..."
        class="flex-1 bg-surface-2 border border-border rounded-xl px-4 py-3 font-mono text-sm text-text placeholder-muted resize-none focus:outline-none focus:border-accent transition-colors"
      />
      <button
        @click="submitRevision"
        :disabled="loading || !instruction.trim()"
        class="px-5 py-3 rounded-xl font-display font-bold text-sm bg-accent text-bg hover:opacity-90 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 whitespace-nowrap"
      >
        <svg
          v-if="loading"
          class="w-4 h-4 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Revise →
      </button>
    </div>
    <p v-if="error" class="text-danger text-xs font-mono">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { revise, getStatus, getHistoryDetail } from '@/api/client'

const props = defineProps({
  jobId: { type: String, required: true },
  currentRevisionNumber: { type: Number, default: 0 },
})

const emit = defineEmits(['revised'])

const instruction = ref('')
const loading = ref(false)
const error = ref(null)
let pollInterval = null

async function submitRevision() {
  if (!instruction.value.trim() || loading.value) return

  loading.value = true
  error.value = null

  try {
    await revise(props.jobId, instruction.value.trim())
    instruction.value = ''

    // Poll until completed
    await new Promise((resolve, reject) => {
      pollInterval = setInterval(async () => {
        try {
          const { data } = await getStatus(props.jobId)
          if (data.status === 'completed') {
            clearInterval(pollInterval)
            pollInterval = null
            resolve()
          } else if (data.status === 'failed') {
            clearInterval(pollInterval)
            pollInterval = null
            reject(new Error(data.error_message || 'Revision failed'))
          }
        } catch (err) {
          clearInterval(pollInterval)
          pollInterval = null
          reject(err)
        }
      }, 3000)
    })

    // Re-fetch full detail
    const { data: detail } = await getHistoryDetail(props.jobId)
    emit('revised', detail)
  } catch (err) {
    error.value = err.message || 'Revision failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

