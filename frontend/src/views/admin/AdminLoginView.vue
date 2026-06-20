<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="logo-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/><line x1="12" y1="22" x2="12" y2="15.5"/><polyline points="22 8.5 12 15.5 2 8.5"/></svg>
        </span>
        <h1 class="login-title">SC ADMIN</h1>
        <p class="login-subtitle">后台管理系统</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </div>
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="login-button"
          size="large"
        >
          登 录
        </el-button>
      </form>

      <div class="login-footer">
        <router-link to="/" class="back-link">← 返回前台</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { adminLogin } from '../../api/admin'

const router = useRouter()
const loading = ref(false)
const form = ref({
  username: '',
  password: '',
})

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (loading.value) return  // 防止重复点击
  loading.value = true
  try {
    const data = await adminLogin(form.value.username, form.value.password)
    localStorage.setItem('admin_token', data.access_token)
    localStorage.setItem('admin_username', data.username || form.value.username)
    ElMessage.success('登录成功')
    router.push('/admin/crawler')
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '登录失败，请检查用户名和密码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-base);
  position: relative;
}

.login-card {
  width: 400px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: 48px 40px;
  position: relative;
  overflow: hidden;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border: 1px solid var(--accent);
  border-radius: var(--radius-md);
  color: var(--accent);
  background: var(--accent-deep);
  margin-bottom: 16px;
}

.login-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.login-subtitle {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 4px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}

.login-button {
  width: 100%;
  margin-top: 8px;
  height: 44px;
  font-size: 14px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}

.back-link {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  transition: color 0.25s var(--ease-smooth);
}

.back-link:hover {
  color: var(--accent);
}
</style>
