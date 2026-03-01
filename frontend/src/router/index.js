import { createRouter, createWebHistory } from 'vue-router'

const LandingView = () => import('@/views/LandingView.vue')
const GenerateView = () => import('@/views/GenerateView.vue')
const StatusView = () => import('@/views/StatusView.vue')
const HistoryView = () => import('@/views/HistoryView.vue')
const HistoryDetailView = () => import('@/views/HistoryDetailView.vue')

const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/generate', name: 'generate', component: GenerateView },
  { path: '/status/:id', name: 'status', component: StatusView },
  { path: '/history', name: 'history', component: HistoryView },
  { path: '/history/:id', name: 'history-detail', component: HistoryDetailView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.name === 'landing' && localStorage.getItem('cosual_visited')) {
    next({ name: 'generate' })
  } else {
    next()
  }
})

export default router

