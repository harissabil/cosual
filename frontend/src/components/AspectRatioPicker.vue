<template>
  <div class="flex flex-wrap gap-2">
    <button
      v-for="ratio in ratios"
      :key="ratio.value"
      @click="$emit('update:modelValue', ratio.value)"
      class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-mono border transition-all duration-200"
      :class="
        modelValue === ratio.value
          ? 'border-accent bg-accent-soft text-accent'
          : 'border-border text-muted hover:border-border-2 hover:text-text'
      "
    >
      <span
        class="border border-current opacity-60"
        :style="{ width: ratio.w + 'px', height: ratio.h + 'px', borderRadius: '2px' }"
      />
      {{ ratio.value }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: '16:9' },
})

defineEmits(['update:modelValue'])

const ratios = [
  { value: '16:9', w: 16, h: 9 },
  { value: '4:3', w: 16, h: 12 },
  { value: '1:1', w: 14, h: 14 },
  { value: '3:4', w: 12, h: 16 },
  { value: '9:16', w: 9, h: 16 },
]
</script>

