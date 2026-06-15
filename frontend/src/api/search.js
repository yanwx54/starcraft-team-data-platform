import api from './index'

export function search(keyword) {
  return api.get('/search', { params: { keyword } })
}
