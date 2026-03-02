<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-6 relative overflow-hidden">
    <!-- Animated title with logo as "C" -->
    <h1 class="flex items-center mb-6">
      <img
        src="/cosual.svg"
        alt="C"
        class="fade-up h-[4rem] w-[4rem] md:h-[6.5rem] md:w-[6.5rem] -mr-3.5 md:-mr-6 relative -top-0.5 md:-top-1"
        style="animation-delay: 0s"
      />
      <span
        v-for="(letter, i) in 'OSUAL'.split('')"
        :key="i"
        class="fade-up font-display font-extrabold text-6xl md:text-8xl text-text"
        :style="{ animationDelay: `${(i + 1) * 0.1}s` }"
      >
        {{ letter }}
      </span>
    </h1>

    <!-- Tagline -->
    <p
      class="fade-up font-mono text-lg md:text-xl text-muted mb-4"
      style="animation-delay: 0.6s"
    >
      Code → Visual Content
    </p>

    <!-- Sub-tagline -->
    <p
      class="fade-up font-mono text-sm text-muted/70 max-w-xl text-center mb-10 leading-relaxed"
      style="animation-delay: 0.9s"
    >
      Transform GitHub repos, raw code, or ideas into stunning architecture diagrams and cinematic video trailers
    </p>

    <!-- CTA -->
    <button
      @click="enter"
      class="fade-up px-8 py-3.5 rounded-xl font-display font-bold text-base bg-accent text-bg glow-accent hover:opacity-90 transition-all duration-300"
      style="animation-delay: 1.2s"
    >
      Start Creating →
    </button>

    <!-- Powered by -->
    <p
      class="fade-up absolute bottom-6 right-6 font-mono text-xs text-muted/50"
      style="animation-delay: 1.5s"
    >
      Powered by Qwen + Wan · Alibaba Cloud
    </p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  localStorage.setItem('cosual_visited', '1')
})

function enter() {
  router.push('/generate')
}
</script>

