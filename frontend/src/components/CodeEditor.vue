<template>
  <div class="relative">
    <div ref="editorRef" class="code-editor-wrap" />
    <span class="absolute top-2 right-3 text-xs font-mono text-muted pointer-events-none z-10">
      {{ detectedLang }}
    </span>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, lineNumbers, highlightActiveLine, highlightActiveLineGutter } from '@codemirror/view'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { syntaxHighlighting, defaultHighlightStyle, bracketMatching } from '@codemirror/language'
import { javascript } from '@codemirror/lang-javascript'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'auto' },
})

const emit = defineEmits(['update:modelValue'])

const editorRef = ref(null)
const detectedLang = ref('Text')
let editorView = null

function detectLanguage(code) {
  if (props.language !== 'auto') {
    return props.language
  }
  if (/^\s*(import |from |def |class |print\(|if __name__)/.test(code)) return 'python'
  if (/^\s*(const |let |var |function |import |export |=>|require\()/.test(code)) return 'javascript'
  return 'text'
}

function getLangExtension(lang) {
  switch (lang) {
    case 'javascript': return javascript()
    case 'python': return python()
    default: return []
  }
}

function getLangLabel(lang) {
  switch (lang) {
    case 'javascript': return 'JavaScript'
    case 'python': return 'Python'
    default: return 'Text'
  }
}

onMounted(() => {
  const lang = detectLanguage(props.modelValue)
  detectedLang.value = getLangLabel(lang)

  const state = EditorState.create({
    doc: props.modelValue,
    extensions: [
      lineNumbers(),
      highlightActiveLine(),
      highlightActiveLineGutter(),
      history(),
      bracketMatching(),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
      keymap.of([...defaultKeymap, ...historyKeymap]),
      getLangExtension(lang),
      oneDark,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          const value = update.state.doc.toString()
          emit('update:modelValue', value)
          const newLang = detectLanguage(value)
          detectedLang.value = getLangLabel(newLang)
        }
      }),
      EditorView.theme({
        '&': { minHeight: '200px' },
      }),
    ],
  })

  editorView = new EditorView({
    state,
    parent: editorRef.value,
  })
})

watch(() => props.modelValue, (newVal) => {
  if (editorView && newVal !== editorView.state.doc.toString()) {
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: newVal,
      },
    })
  }
})

onUnmounted(() => {
  if (editorView) {
    editorView.destroy()
    editorView = null
  }
})
</script>

<style scoped>
.code-editor-wrap {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
}
</style>

