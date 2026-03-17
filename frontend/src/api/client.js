import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

/** Fetch paginated/filtered paper list. */
export function fetchPapers(filters = {}) {
  const params = { limit: 120 }
  if (filters.subfield) params.subfield = filters.subfield
  if (filters.dateFrom) params.date_from = filters.dateFrom
  if (filters.dateTo) params.date_to = filters.dateTo
  if (filters.minScore > 0) params.min_score = filters.minScore
  return api.get('/papers', { params }).then(r => r.data)
}

/** Fetch a single paper by ID. */
export function fetchPaper(id) {
  return api.get(`/papers/${id}`).then(r => r.data)
}

/** Fetch aggregate stats. */
export function fetchStats() {
  return api.get('/stats').then(r => r.data)
}

/** Fetch past digests. */
export function fetchDigests() {
  return api.get('/digests').then(r => r.data)
}

/** Manually trigger the pipeline. */
export function runPipeline() {
  return api.post('/pipeline/run').then(r => r.data)
}
