import api from './index'

export function getPlayers(params) {
  return api.get('/players', { params })
}

export function getPlayerDetail(id) {
  return api.get(`/players/${id}`)
}

export function getPlayerMatches(id, params) {
  return api.get(`/players/${id}/matches`, { params })
}

export function getPlayerPrizes(id) {
  return api.get(`/players/${id}/prizes`)
}

export function getPlayerMapStats(id) {
  return api.get(`/players/${id}/maps`)
}

export function getPlayerVsRecord(id, opponentId, params) {
  return api.get(`/players/${id}/vs/${opponentId}`, { params })
}
