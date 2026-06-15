import api from './index'

export function getDashboardSummary() {
  return api.get('/dashboard/summary')
}

export function getLatestMatches(limit = 10) {
  return api.get('/dashboard/latest-matches', { params: { limit } })
}

export function getPrizeRanking(limit = 20) {
  return api.get('/dashboard/prize-ranking', { params: { limit } })
}

export function getWinStreakRanking(limit = 10) {
  return api.get('/dashboard/win-streak-ranking', { params: { limit } })
}
