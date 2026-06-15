import api from './index'

export function adminLogin(username, password) {
  return api.post('/admin/auth/login', { username, password })
}

export function getAdminMe() {
  return api.get('/admin/auth/me')
}
