import api from './index'

export function runCrawl() {
  return api.post('/admin/crawler/run')
}

export function runCrawlByWrId(wrId) {
  return api.post(`/admin/crawler/run/${wrId}`)
}

export function getCrawlLogs(params) {
  return api.get('/admin/crawler/logs', { params })
}
