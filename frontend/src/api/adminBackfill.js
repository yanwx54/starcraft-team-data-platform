import api from './index'

export function startBackfill(startDate) {
  return api.post('/admin/crawler/backfill', { start_date: startDate })
}

export function resumeBackfill(jobId) {
  return api.post('/admin/crawler/backfill/resume', { job_id: jobId })
}

export function pauseBackfill(jobId) {
  return api.post(`/admin/crawler/backfill/pause/${jobId}`)
}

export function getBackfillStatus(jobId) {
  return api.get(`/admin/crawler/backfill/status/${jobId}`)
}

export function listBackfillJobs() {
  return api.get('/admin/crawler/backfill/jobs')
}

export function scanBackfillHistory(startDate) {
  return api.post('/admin/crawler/backfill/scan', { start_date: startDate })
}
