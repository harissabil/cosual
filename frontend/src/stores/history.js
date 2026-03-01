import { defineStore } from 'pinia'
import { getHistory } from '@/api/client'

const STORAGE_KEY = 'cosual_job_ids'

export const useHistoryStore = defineStore('history', {
  state: () => ({
    jobIds: [],
    items: [],
  }),

  actions: {
    loadFromStorage() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        this.jobIds = raw ? JSON.parse(raw) : []
      } catch {
        this.jobIds = []
      }
    },

    saveToStorage() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.jobIds))
    },

    addJobId(id) {
      if (!this.jobIds.includes(id)) {
        this.jobIds.unshift(id)
        this.saveToStorage()
      }
      this.fetchMyHistory()
    },

    removeJobId(id) {
      this.jobIds = this.jobIds.filter((jid) => jid !== id)
      this.saveToStorage()
      this.items = this.items.filter((item) => item.job_id !== id)
    },

    async fetchMyHistory() {
      try {
        const { data } = await getHistory()
        this.items = (data.items || []).filter((item) =>
          this.jobIds.includes(item.job_id)
        )
      } catch (err) {
        console.error('Failed to fetch history:', err)
      }
    },
  },
})

