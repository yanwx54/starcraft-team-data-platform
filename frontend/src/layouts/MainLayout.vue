<template>
  <div class="layout">
    <!-- Top accent line -->
    <div class="accent-top-line"></div>

    <!-- Top Navigation -->
    <header class="layout-header">
      <div class="header-inner">
        <router-link to="/" class="logo">
          <span class="logo-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/><line x1="12" y1="22" x2="12" y2="15.5"/><polyline points="22 8.5 12 15.5 2 8.5"/></svg>
          </span>
          <span class="logo-text">SC DATA</span>
        </router-link>
        <nav class="nav">
          <router-link to="/" class="nav-item" exact-active-class="active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            <span>首页</span>
          </router-link>
          <router-link to="/matches" class="nav-item" active-class="active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            <span>比赛</span>
          </router-link>
          <router-link to="/players" class="nav-item" active-class="active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <span>选手</span>
          </router-link>
          <router-link to="/vs" class="nav-item" active-class="active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8l2-2 2 2M8 16l-2 2-2-2"/><circle cx="12" cy="12" r="3"/><line x1="8" y1="8" x2="10" y2="10"/><line x1="14" y1="14" x2="16" y2="16"/></svg>
            <span>对战</span>
          </router-link>
          <router-link to="/maps" class="nav-item" active-class="active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
            <span>地图</span>
          </router-link>
          <router-link to="/rankings" class="nav-item" active-class="active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            <span>排行榜</span>
          </router-link>
          <router-link to="/admin" class="nav-item" active-class="active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            <span>后台</span>
          </router-link>
        </nav>
      </div>
    </header>

    <!-- Main Content -->
    <main class="layout-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  position: relative;
}

/* ── Top Accent Line ── */
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

/* ── Header ── */
.layout-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(6, 13, 26, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-default);
}

.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 32px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* ── Logo ── */
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: opacity 0.25s var(--ease-smooth);
}

.logo:hover {
  opacity: 0.8;
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

/* ── Navigation ── */
.nav {
  display: flex;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: all 0.25s var(--ease-smooth);
  border: 1px solid transparent;
}

.nav-item:hover {
  color: var(--accent);
  border-color: var(--border-default);
  background: rgba(0, 212, 255, 0.04);
}

.nav-item.active {
  color: var(--accent);
  border-color: var(--border-glow);
  background: var(--accent-deep);
  text-shadow: var(--glow-accent);
}

.nav-item svg {
  flex-shrink: 0;
}

/* ── Main Content ── */
.layout-main {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 0 32px;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .header-inner {
    padding: 0 16px;
    height: 48px;
  }

  .logo-text {
    display: none;
  }

  .nav {
    gap: 0;
  }

  .nav-item {
    padding: 6px 8px;
    font-size: 11px;
    gap: 4px;
  }

  .nav-item span {
    display: none;
  }

  .layout-main {
    padding: 0 16px;
  }
}
</style>
