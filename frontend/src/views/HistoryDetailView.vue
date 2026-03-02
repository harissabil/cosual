<template>
  <div class="pt-20 pb-12 px-6 max-w-7xl mx-auto">
    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <div class="waveform-loader">
        <span /><span /><span /><span /><span />
      </div>
    </div>

    <!-- Detail layout -->
    <div v-else-if="detail" class="grid grid-cols-1 lg:grid-cols-12 gap-8">

      <!-- ═══ Left Column — Current Output ═══ -->
      <div class="lg:col-span-7 space-y-6">
        <h1 class="font-display font-bold text-2xl text-text">{{ detail.title }}</h1>

        <!-- Image -->
        <div v-if="detail.output_type === 'image'" class="glass-card p-3">
          <img
            :src="mediaUrl(activeOutputUrl)"
            :alt="detail.title"
            class="rounded-xl w-full max-h-[60vh] object-contain relative"
          />

          <div class="mt-3 flex items-center gap-3 justify-end">
            <a
              v-if="activeOutputUrl"
              :href="mediaUrl(activeOutputUrl)"
              :download="detailDownloadName"
              class="py-2 px-4 rounded-xl font-display font-bold text-sm text-center border border-accent text-accent hover:bg-accent-soft transition-all duration-200"
            >
              Download Image
            </a>
          </div>

          <!-- Revision loading overlay -->
          <div v-if="revising" class="absolute inset-0 rounded-xl bg-bg/60 flex items-center justify-center">
            <div class="waveform-loader">
              <span /><span /><span /><span /><span />
            </div>
          </div>
        </div>

        <!-- Video -->
        <div v-else-if="detail.output_type === 'video'" class="glass-card p-3">
          <video
            :src="mediaUrl(activeOutputUrl)"
            autoplay
            muted
            loop
            controls
            class="rounded-xl w-full max-h-[60vh]"
          />
          <div class="mt-3 flex items-center gap-3 justify-end">
            <a
              v-if="activeOutputUrl"
              :href="mediaUrl(activeOutputUrl)"
              :download="detailDownloadName"
              class="py-2 px-4 rounded-xl font-display font-bold text-sm text-center border border-accent text-accent hover:bg-accent-soft transition-all duration-200"
            >
              Download Video
            </a>
          </div>
        </div>

        <!-- Caption -->
        <CaptionBox
          :caption="activeCaption"
          :platform="detail.style_config?.platform || ''"
        />

        <!-- Share -->
        <ShareLinkedIn
          v-if="detail.status === 'completed' && detail.style_config?.platform === 'linkedin'"
          :url="mediaUrl(activeOutputUrl)"
          :title="detail.title"
          :summary="activeCaption || ''"
        />

        <!-- Revision Chat (only for completed images) -->
        <RevisionChat
          v-if="detail.output_type === 'image' && detail.status === 'completed'"
          :jobId="detail.job_id"
          :currentRevisionNumber="latestRevisionNumber"
          @revised="onRevised"
        />
      </div>

      <!-- ═══ Right Column — Timeline & Config ═══ -->
      <div class="lg:col-span-5 space-y-6 lg:sticky lg:top-20 self-start">

        <!-- Revision History -->
        <div class="glass-card p-6">
          <h3 class="font-display font-bold text-sm text-muted uppercase tracking-wider mb-5">Revision History</h3>

          <div v-if="sortedRevisions.length" class="space-y-0 max-h-[50vh] overflow-y-auto pr-1">
            <div
              v-for="(rev, i) in sortedRevisions"
              :key="rev.revision_number"
              @click="selectRevision(rev)"
              class="flex items-start gap-3 cursor-pointer group"
            >
              <div class="flex flex-col items-center">
                <div
                  class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-mono border transition-all duration-200"
                  :class="activeRevision === rev.revision_number
                    ? 'border-accent bg-accent-soft text-accent'
                    : 'border-border bg-surface-2 text-muted group-hover:border-border-2'"
                >
                  {{ rev.revision_number }}
                </div>
                <div v-if="i < sortedRevisions.length - 1" class="w-px h-6 border-l border-dashed border-border my-1" />
              </div>
              <div class="flex-1 pt-0.5 min-w-0">
                <p class="font-mono text-xs text-text truncate">
                  {{ rev.revision_number === 1 ? 'Original' : rev.revision_prompt }}
                </p>
                <div class="flex items-center gap-2 mt-1">
                  <img
                    v-if="rev.output_url"
                    :src="mediaUrl(rev.output_url)"
                    :alt="'Revision ' + rev.revision_number"
                    class="w-10 h-10 rounded object-cover border transition-all duration-200"
                    :class="activeRevision === rev.revision_number ? 'border-accent' : 'border-border'"
                  />
                  <span class="font-mono text-[10px] text-muted">
                    {{ formatDate(rev.created_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <p v-else class="font-mono text-xs text-muted">No revisions yet.</p>
        </div>

        <!-- Style Config Summary -->
        <div class="glass-card p-6">
          <h3 class="font-display font-bold text-sm text-muted uppercase tracking-wider mb-4">Configuration</h3>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <p class="font-mono text-[10px] text-muted uppercase mb-1">Output Type</p>
              <p class="font-mono text-sm text-text">{{ detail.style_config?.output_type || '—' }}</p>
            </div>
            <div>
              <p class="font-mono text-[10px] text-muted uppercase mb-1">Aspect Ratio</p>
              <p class="font-mono text-sm text-text">{{ detail.style_config?.aspect_ratio || '—' }}</p>
            </div>
            <div>
              <p class="font-mono text-[10px] text-muted uppercase mb-1">Platform</p>
              <p class="font-mono text-sm text-text capitalize">{{ detail.style_config?.platform || '—' }}</p>
            </div>
            <div>
              <p class="font-mono text-[10px] text-muted uppercase mb-1">Style</p>
              <p class="font-mono text-sm text-text">{{ detail.style_config?.style || 'Default' }}</p>
            </div>
            <div v-if="detail.style_config?.duration">
              <p class="font-mono text-[10px] text-muted uppercase mb-1">Duration</p>
              <p class="font-mono text-sm text-text">{{ detail.style_config.duration }}s</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else class="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <p class="font-display font-medium text-lg text-text mb-2">Item not found</p>
      <p class="font-mono text-sm text-muted mb-6">{{ error || 'Could not load this generation.' }}</p>
      <router-link
        to="/history"
        class="px-8 py-3 rounded-xl font-display font-bold text-sm bg-accent text-bg glow-accent hover:opacity-90 transition-all duration-200"
      >
        Back to History →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getHistoryDetail, mediaUrl } from '@/api/client'
import CaptionBox from '@/components/CaptionBox.vue'
import RevisionChat from '@/components/RevisionChat.vue'
import ShareLinkedIn from '@/components/ShareLinkedIn.vue'

const route = useRoute()

const detail = ref(null)
const loading = ref(true)
const error = ref(null)
const revising = ref(false)
const activeRevision = ref(null)

const sortedRevisions = computed(() => {
  if (!detail.value?.revisions) return []
  return [...detail.value.revisions].sort((a, b) => b.revision_number - a.revision_number)
})

const latestRevisionNumber = computed(() => {
  if (!sortedRevisions.value.length) return 0
  return sortedRevisions.value[0].revision_number
})

const activeOutputUrl = computed(() => {
  if (activeRevision.value && detail.value?.revisions) {
    const rev = detail.value.revisions.find(r => r.revision_number === activeRevision.value)
    if (rev?.output_url) return rev.output_url
  }
  return detail.value?.output_url
})

const activeCaption = computed(() => {
  if (activeRevision.value && detail.value?.revisions) {
    const rev = detail.value.revisions.find(r => r.revision_number === activeRevision.value)
    if (rev?.caption) return rev.caption
  }
  return detail.value?.caption
})

function selectRevision(rev) {
  activeRevision.value = rev.revision_number
}

async function fetchDetail() {
  try {
    loading.value = true
    const { data } = await getHistoryDetail(route.params.id)
    detail.value = data
    // Default to latest revision
    if (data.revisions?.length) {
      activeRevision.value = Math.max(...data.revisions.map(r => r.revision_number))
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load.'
  } finally {
    loading.value = false
  }
}

function onRevised(updatedDetail) {
  detail.value = updatedDetail
  if (updatedDetail.revisions?.length) {
    activeRevision.value = Math.max(...updatedDetail.revisions.map(r => r.revision_number))
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function safeFilename(title = 'cosual', url = '') {
  const extMatch = url?.split('?')[0].match(/\.([a-zA-Z0-9]+)$/)
  const ext = extMatch ? `.${extMatch[1]}` : '.png'
  const base = (title || 'cosual').toString().replace(/[^a-z0-9\-_ ]+/gi, '').trim().replace(/\s+/g, '_')
  return `${base}${ext}`
}

const detailDownloadName = computed(() => safeFilename(detail.value?.title, activeOutputUrl.value))

onMounted(fetchDetail)
</script>

