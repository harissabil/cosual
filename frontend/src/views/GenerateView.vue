<template>
  <div class="pt-20 pb-12 px-6 max-w-7xl mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- ═══ Left Column — Form ═══ -->
      <div class="lg:col-span-7 space-y-6">

        <!-- Content Input Card -->
        <div class="glass-card p-6">
          <h3 class="font-display font-bold text-lg text-text mb-4">Content Input</h3>

          <!-- Tab bar -->
          <div class="flex gap-1 mb-5 bg-surface-2 rounded-xl p-1">
            <button
              v-for="tab in tabs"
              :key="tab.value"
              @click="switchTab(tab.value)"
              class="flex-1 px-4 py-2 rounded-lg text-sm font-mono transition-all duration-200"
              :class="store.activeTab === tab.value
                ? 'bg-surface text-accent border-b-2 border-accent'
                : 'text-muted hover:text-text'"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Free Text tab -->
          <div v-if="store.activeTab === 'text'">
            <textarea
              v-model="store.freeText"
              rows="4"
              placeholder="Describe your architecture or concept..."
              class="w-full bg-surface-2 border border-border rounded-xl px-4 py-3 font-mono text-sm text-text placeholder-muted resize-none focus:outline-none focus:border-accent transition-colors"
            />
          </div>

          <!-- GitHub URL tab -->
          <div v-if="store.activeTab === 'github'" class="space-y-3">
            <input
              v-model="store.githubUrl"
              type="url"
              placeholder="https://github.com/owner/repo"
              class="w-full bg-surface-2 border border-border rounded-xl px-4 py-3 font-mono text-sm text-text placeholder-muted focus:outline-none focus:border-accent transition-colors"
            />
            <textarea
              v-model="store.freeText"
              rows="2"
              placeholder="Additional context (optional)"
              class="w-full bg-surface-2 border border-border rounded-xl px-4 py-3 font-mono text-sm text-text placeholder-muted resize-none focus:outline-none focus:border-accent transition-colors"
            />
          </div>

          <!-- Raw Code tab -->
          <div v-if="store.activeTab === 'code'" class="space-y-3">
            <CodeEditor v-model="store.rawCode" />
            <textarea
              v-model="store.freeText"
              rows="2"
              placeholder="Additional context (optional)"
              class="w-full bg-surface-2 border border-border rounded-xl px-4 py-3 font-mono text-sm text-text placeholder-muted resize-none focus:outline-none focus:border-accent transition-colors"
            />
          </div>
        </div>

        <!-- Output Type Card -->
        <div class="glass-card p-6">
          <h3 class="font-display font-bold text-lg text-text mb-4">Output Type</h3>
          <div class="flex gap-3">
            <button
              v-for="t in outputTypes"
              :key="t.value"
              @click="setOutputType(t.value)"
              class="flex-1 px-6 py-3 rounded-xl font-display font-bold text-sm border transition-all duration-200"
              :class="store.outputType === t.value
                ? 'border-accent bg-accent-soft text-accent glow-accent'
                : 'border-border text-muted hover:border-border-2 hover:text-text'"
            >
              {{ t.label }}
            </button>
          </div>
          <!-- Duration chips for video -->
          <div v-if="store.outputType === 'video'" class="mt-4">
            <p class="text-xs font-mono text-muted mb-2">Duration</p>
            <div class="flex gap-2">
              <button
                v-for="d in [5, 10, 15]"
                :key="d"
                @click="store.duration = d"
                class="px-4 py-2 rounded-lg text-sm font-mono border transition-all duration-200"
                :class="store.duration === d
                  ? 'border-accent bg-accent-soft text-accent'
                  : 'border-border text-muted hover:border-border-2 hover:text-text'"
              >
                {{ d }}s
              </button>
            </div>
          </div>
        </div>

        <!-- Style Card -->
        <div class="glass-card p-6">
          <h3 class="font-display font-medium text-lg text-text mb-4">Visual Style</h3>
          <StyleChips
            :options="stylePresets"
            :modelValue="selectedPreset"
            @update:modelValue="onPresetSelect"
          />
          <input
            v-model="customStyle"
            @input="onCustomStyleInput"
            type="text"
            placeholder="Or describe your own style..."
            class="w-full mt-3 bg-surface-2 border border-border rounded-xl px-4 py-3 font-mono text-sm text-text placeholder-muted focus:outline-none focus:border-accent transition-colors"
          />
        </div>

        <!-- Settings Row -->
        <div class="glass-card p-6 space-y-5">
          <div>
            <p class="text-sm font-display font-medium text-text mb-3">Aspect Ratio</p>
            <AspectRatioPicker v-model="store.aspectRatio" />
          </div>
          <div>
            <p class="text-sm font-display font-medium text-text mb-3">Platform</p>
            <PlatformPicker v-model="store.platform" />
          </div>
        </div>

        <!-- Validation errors -->
        <div v-if="store.error" class="text-danger text-sm font-mono bg-danger/10 border border-danger/30 rounded-xl px-4 py-3">
          {{ store.error }}
        </div>

        <!-- Submit -->
        <button
          @click="store.submitGenerate()"
          :disabled="store.loading"
          class="w-full py-4 rounded-xl font-display font-bold text-base bg-accent text-bg glow-accent hover:opacity-90 transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <svg
            v-if="store.loading"
            class="w-5 h-5 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          {{ store.loading ? 'Generating...' : 'Generate →' }}
        </button>
      </div>

      <!-- ═══ Right Column — Info ═══ -->
      <div class="lg:col-span-5 space-y-6 lg:sticky lg:top-20 self-start">

        <!-- Workflow card -->
        <div class="glass-card p-6">
          <h3 class="font-display font-bold text-sm text-muted uppercase tracking-wider mb-5">How it works</h3>
          <div class="space-y-0">
            <div v-for="(step, i) in workflowSteps" :key="i" class="flex items-start gap-4">
              <div class="flex flex-col items-center">
                <div
                  class="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-mono"
                  :class="i === 0 ? 'bg-accent text-bg' : 'bg-surface-2 text-muted border border-border'"
                >
                  {{ i + 1 }}
                </div>
                <div v-if="i < workflowSteps.length - 1" class="w-px h-8 border-l border-dashed border-border-2 my-1" />
              </div>
              <div class="pt-1.5">
                <p class="font-display font-medium text-sm text-text">{{ step.title }}</p>
                <p class="font-mono text-xs text-muted mt-0.5">{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tips card -->
        <div class="glass-card p-6">
          <h3 class="font-display font-bold text-sm text-muted uppercase tracking-wider mb-4">Tips for better results</h3>
          <ul class="space-y-2.5">
            <li v-for="(tip, i) in tips" :key="i" class="flex items-start gap-2">
              <span class="text-accent mt-0.5">•</span>
              <span class="font-mono text-xs text-muted leading-relaxed">{{ tip }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGenerateStore } from '@/stores/generate'
import CodeEditor from '@/components/CodeEditor.vue'
import StyleChips from '@/components/StyleChips.vue'
import AspectRatioPicker from '@/components/AspectRatioPicker.vue'
import PlatformPicker from '@/components/PlatformPicker.vue'

const store = useGenerateStore()

const tabs = [
  { value: 'text', label: 'Free Text' },
  { value: 'github', label: 'GitHub URL' },
  { value: 'code', label: 'Raw Code' },
]

const outputTypes = [
  { value: 'image', label: '🖼 Image' },
  { value: 'video', label: '🎬 Video' },
]

const stylePresets = [
  'data viz futuristic',
  'hollywood',
  'neon cyberpunk',
  'vintage retro',
  'minimalist clean',
  'architectural classic',
]

const selectedPreset = ref(store.style && stylePresets.includes(store.style) ? store.style : '')
const customStyle = ref(store.style && !stylePresets.includes(store.style) ? store.style : '')

function onPresetSelect(val) {
  selectedPreset.value = val
  customStyle.value = ''
  store.style = val
}

function onCustomStyleInput() {
  if (customStyle.value.trim()) {
    selectedPreset.value = ''
    store.style = customStyle.value
  } else {
    store.style = selectedPreset.value
  }
}

function setOutputType(val) {
  store.outputType = val
  if (val === 'image') store.duration = null
}

function switchTab(tab) {
  // Clear previous tab's input
  if (store.activeTab === 'github') store.githubUrl = ''
  if (store.activeTab === 'code') store.rawCode = ''
  if (store.activeTab === 'text' && tab !== 'text') store.freeText = ''
  store.activeTab = tab
  store.error = null
}

const workflowSteps = [
  { title: 'Parse Input', desc: 'Analyze your code, URL, or description' },
  { title: 'Analyze Architecture', desc: 'Identify components and relationships' },
  { title: 'Generate Prompt', desc: 'Craft optimized visual prompt' },
  { title: 'Create Visual', desc: 'Render high-quality image or video' },
]

const tips = [
  'Be specific about what components or flows you want visualized',
  'Include framework names for better architecture detection',
  'Use GitHub URLs pointing to the repository root for best results',
  'Combine free text with code for the most context-rich output',
]
</script>

