import api from './index'

export function getMaps() {
  return api.get('/maps')
}

export function getMapDetail(id) {
  return api.get(`/maps/${id}`)
}

export function getMapRaceStats(id) {
  return api.get(`/maps/${id}/race-stats`)
}

export function getCurrentSeasonMaps() {
  return api.get('/maps/current-season')
}
