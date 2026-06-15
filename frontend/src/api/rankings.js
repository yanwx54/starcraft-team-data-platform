import api from './index'

export function getWinRanking(params) {
  return api.get('/rankings/wins', { params })
}

export function getWinRateRanking(params) {
  return api.get('/rankings/win-rate', { params })
}

export function getPrizeRanking(params) {
  return api.get('/rankings/prize', { params })
}

export function getStreakRanking(params) {
  return api.get('/rankings/streak', { params })
}
