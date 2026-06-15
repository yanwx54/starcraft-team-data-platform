import api from './index'

export function getMatches(params) {
  return api.get('/matches', { params })
}

export function getMatchDetail(id) {
  return api.get(`/matches/${id}`)
}

export function getMatchStages(id) {
  return api.get(`/matches/${id}/stages`)
}
