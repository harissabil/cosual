import { defineStore } from 'pinia'
import { generateContent, getStatus } from '@/api/client'
import { useHistoryStore } from './history'
import router from '@/router'

export const useGenerateStore = defineStore('generate', {
  state: () => ({
    // Form fields
    activeTab: 'text',       // 'text' | 'github' | 'code'
    freeText: '',
    githubUrl: '',
    rawCode: '',
    outputType: 'image',     // 'image' | 'video'
    duration: null,          // 5 | 10 | 15 | null
    aspectRatio: '16:9',
    style: '',
    platform: 'linkedin',

    // Generation state
    currentJobId: null,
    currentStatus: null,
    polling: null,
    loading: false,
    error: null,
  }),

  actions: {
    validate() {
      const errors = []

      if (this.activeTab === 'text' && !this.freeText.trim()) {
        errors.push('Please enter a description.')
      }
      if (this.activeTab === 'github' && !this.githubUrl.trim()) {
        errors.push('Please enter a GitHub URL.')
      }
      if (this.activeTab === 'github' && this.githubUrl.trim()) {
        try {
          const url = new URL(this.githubUrl.trim())
          if (!url.hostname.includes('github.com')) {
            errors.push('Please enter a valid GitHub URL.')
          }
        } catch {
          errors.push('Please enter a valid URL.')
        }
      }
      if (this.activeTab === 'code' && !this.rawCode.trim()) {
        errors.push('Please paste some code.')
      }
      if (this.outputType === 'video' && !this.duration) {
        errors.push('Please select a video duration.')
      }

      return errors
    },

    async submitGenerate() {
      const errors = this.validate()
      if (errors.length) {
        this.error = errors.join(' ')
        return
      }

      this.loading = true
      this.error = null

      const body = {
        free_text: this.freeText || '',
        github_url: this.activeTab === 'github' ? this.githubUrl : null,
        raw_code: this.activeTab === 'code' ? this.rawCode : null,
        output_type: this.outputType,
        duration: this.outputType === 'video' ? this.duration : null,
        aspect_ratio: this.aspectRatio,
        style: this.style,
        platform: this.platform,
      }

      try {
        const { data } = await generateContent(body)
        this.currentJobId = data.job_id
        this.currentStatus = data

        const historyStore = useHistoryStore()
        historyStore.addJobId(data.job_id)

        router.push(`/status/${data.job_id}`)
      } catch (err) {
        this.error = err.response?.data?.detail || 'Generation failed. Please try again.'
      } finally {
        this.loading = false
      }
    },

    startPolling(jobId) {
      this.stopPolling()
      this.currentJobId = jobId

      const poll = async () => {
        try {
          const { data } = await getStatus(jobId)
          this.currentStatus = data
          if (data.status === 'completed' || data.status === 'failed') {
            this.stopPolling()
          }
        } catch (err) {
          console.error('Polling error:', err)
        }
      }

      poll() // immediate first call
      this.polling = setInterval(poll, 3000)
    },

    stopPolling() {
      if (this.polling) {
        clearInterval(this.polling)
        this.polling = null
      }
    },

    reset() {
      this.currentJobId = null
      this.currentStatus = null
      this.stopPolling()
    },
  },
})

