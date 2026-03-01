<template>
  <div class="flex flex-wrap gap-2">
    <button
      v-for="option in options"
      :key="option"
      @click="toggle(option)"
      class="px-4 py-2 rounded-lg text-sm font-mono border transition-all duration-200"
      :class="
        modelValue === option
          ? 'border-accent bg-accent-soft text-accent glow-accent'
          : 'border-border text-muted hover:border-border-2 hover:text-text'
      "
    >
      {{ option }}
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  options: { type: Array, required: true },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

function toggle(option) {
  emit('update:modelValue', props.modelValue === option ? '' : option)
}
</script>

