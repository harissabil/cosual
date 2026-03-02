<template>
  <nav class="fixed top-0 left-0 right-0 z-50 border-b border-border backdrop-blur-xl bg-bg/70">
    <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
      <router-link to="/generate" class="flex items-center -gap-px font-display font-bold text-xl tracking-tight leading-none text-text hover:text-accent transition-colors">
        <img src="/cosual.svg" alt="C" class="w-6 h-6 block -mr-1.5 relative -top-[0.75px]" />
        <span>OSUAL</span>
      </router-link>
      <router-link to="/history" class="flex items-center gap-2 font-mono text-sm text-muted hover:text-text transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        History
      </router-link>
    </div>
  </nav>
</template>

