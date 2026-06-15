<template>
  <div class="admin-layout">
    <!-- Top accent line -->
    <div class="accent-top-line"></div>

    <!-- Sidebar -->
    <aside class="admin-sidebar">
      <router-link to="/admin" class="sidebar-logo">
        <span class="logo-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/><line x1="12" y1="22" x2="12" y2="15.5"/><polyline points="22 8.5 12 15.5 2 8.5"/></svg>
        </span>
        <span class="logo-text">SC ADMIN</span>
      </router-link>

      <nav class="sidebar-nav">
        <router-link to="/admin/crawler" class="sidebar-item" active-class="active">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
          <span>手动采集</span>
        </router-link>
        <router-link to="/admin/backfill" class="sidebar-item" active-class="active">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <span>历史回补</span>
        </router-link>
        <router-link to="/admin/issues" class="sidebar-item" active-class="active">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <span>异常中心</span>
        </router-link>
        <router-link to="/admin/translations" class="sidebar-item" active-class="active">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 8l6 6"/><path d="M4 14l6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="M22 22l-5-10-5 10"/><path d="M14 18h6"/></svg>
          <span>翻译规则</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/" class="sidebar-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          <span>返回前台</span>
        </router-link>
        <a class="sidebar-item" @click="handleLogout">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          <span>退出登录</span>
        </a>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="admin-main">
      <header class="admin-header">
        <div class="header-info">
          <span class="admin-badge">ADMIN</span>
          <span class="admin-username">{{ username }}</span>
        </div>
      </header>
      <div class="admin-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = computed(() => localStorage.getItem('admin_username') || 'admin')

function handleLogout() {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_username')
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  background: var(--bg-base);
  position: relative;
}

.accent-top-line {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  z-index: 200;
  animation: pulse-glow 3s ease-in-out infinite;
}

.admin-sidebar {
  width: 220px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  padding-top: 2px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  text-decoration: none;
  border-bottom: 1px solid var(--border-dim);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  color: var(--accent);
  background: var(--accent-deep);
}

.logo-text {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--text-primary);
  text-transform: uppercase;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: all 0.25s var(--ease-smooth);
  cursor: pointer;
}

.sidebar-item:hover {
  color: var(--accent);
  background: rgba(0, 212, 255, 0.04);
}

.sidebar-item.active {
  color: var(--accent);
  background: var(--accent-deep);
  border: 1px solid var(--border-glow);
  text-shadow: var(--glow-accent);
}

.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid var(--border-dim);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.admin-main {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-header {
  height: 52px;
  border-bottom: 1px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 32px;
  background: rgba(6, 13, 26, 0.92);
  backdrop-filter: blur(16px);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-badge {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-deep);
  border: 1px solid var(--accent);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  letter-spacing: 0.1em;
}

.admin-username {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
}

.admin-content {
  flex: 1;
  padding: 32px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

@media (max-width: 768px) {
  .admin-sidebar { width: 56px; }
  .admin-main { margin-left: 56px; }
  .sidebar-item span { display: none; }
  .logo-text { display: none; }
  .admin-content { padding: 16px; }
}
</style>
