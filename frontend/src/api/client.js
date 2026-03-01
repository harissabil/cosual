import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const api = axios.create({ baseURL: BASE_URL })

/**
 * Convert a relative output_url from the API to an absolute URL.
 * Always use this when binding to <img src> or <video src>.
 */
export const mediaUrl = (path) => {
  if (!path) return ''
  return `${BASE_URL}${path}`
}

/**
 * POST /generate
 * @param {Object} body — { free_text, github_url, raw_code, output_type, duration, aspect_ratio, style, platform }
 */
export const generateContent = (body) => api.post('/generate', body)

/**
 * GET /status/:id
 * @returns {{ job_id, title, status, output_type, output_url, caption, generated_prompt, error_message, created_at, updated_at }}
 */
export const getStatus = (id) => api.get(`/status/${id}`)

/**
 * GET /history
 * @returns {{ items: Array, total: number }}
 */
export const getHistory = () => api.get('/history')

/**
 * GET /history/:id
 * @returns full history detail with revisions
 */
export const getHistoryDetail = (id) => api.get(`/history/${id}`)

/**
 * POST /revise/:id
 * @param {string} id — job_id
 * @param {string} instruction — revision_instruction text
 */
export const revise = (id, instruction) =>
  api.post(`/revise/${id}`, { revision_instruction: instruction })

export default api

