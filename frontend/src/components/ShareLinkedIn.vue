<template>
  <button
    @click="shareOnLinkedIn"
    class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-display font-bold border border-[#0A66C2] text-[#0A66C2] hover:bg-[#0A66C2]/10 transition-all duration-200"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
    Share on LinkedIn
  </button>
</template>

<script setup>
const props = defineProps({
  url: { type: String, default: '' },
  title: { type: String, default: '' },
  summary: { type: String, default: '' },
})

function shareOnLinkedIn() {
  const shareUrl = props.url || window.location.href
  const params = new URLSearchParams({
    mini: 'true',
    url: shareUrl,
    title: props.title,
    summary: props.summary,
  })
  const linkedInUrl = `https://www.linkedin.com/shareArticle?${params.toString()}`
  window.open(linkedInUrl, '_blank', 'width=600,height=600,scrollbars=yes')
}
</script>

