import axios from 'axios'
import { ElMessage } from 'element-plus'

// 支持混合部署：Cloudflare Pages 代理 / 直接连接后端
// 开发环境: /api/v1 → Vite proxy → localhost:8000
// Cloudflare Pages: /api/v1 → Functions 代理 → Zeabur
// 独立部署: VITE_API_BASE_URL=https://xxx.zeabur.app/api/v1
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL,
  timeout: 15000,
})

// 请求拦截器：自动附加 JWT Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.success === false) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return data
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期或无效，跳转登录
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_username')
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/admin/login'
      }
      return Promise.reject(error)
    }
    const msg = error.response?.data?.detail || error.response?.data?.message || error.message || '网络错误'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default api
