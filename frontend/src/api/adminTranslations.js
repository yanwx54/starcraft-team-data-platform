import api from './index'

export function getTranslations(params) {
  return api.get('/admin/translations', { params })
}

export function createTranslation(data) {
  return api.post('/admin/translations', data)
}

export function updateTranslation(ruleId, data) {
  return api.put(`/admin/translations/${ruleId}`, data)
}

export function deleteTranslation(ruleId) {
  return api.delete(`/admin/translations/${ruleId}`)
}
