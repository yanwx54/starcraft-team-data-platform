<template>
  <div class="layout">
    <!-- Top accent line -->
    <div class="accent-top-line"></div>

    <!-- Left Sidebar Navigation -->
    <aside class="sidebar-left">
      <nav class="sidebar-nav">
        <router-link to="/" class="sidebar-item" exact-active-class="active">
          <span class="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </span>
        </router-link>
        <router-link to="/matches" class="sidebar-item" active-class="active">
          <span class="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
          </span>
        </router-link>
        <router-link to="/players" class="sidebar-item" active-class="active">
          <span class="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </span>
        </router-link>
        <router-link to="/maps" class="sidebar-item" active-class="active">
          <span class="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
          </span>
        </router-link>
        <router-link to="/rankings" class="sidebar-item" active-class="active">
          <span class="sidebar-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </span>
        </router-link>
      </nav>
      <div class="sidebar-line"></div>
    </aside>

    <!-- Right Sidebar -->
    <aside class="sidebar-right">
      <div class="social-links">
        <a href="https://github.com" target="_blank" class="social-link" aria-label="GitHub">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
        </a>
      </div>
      <div class="social-line"></div>
    </aside>

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

/* Top accent line */
.accent-top-line {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  z-index: 100;
  animation: pulse-glow 3s ease-in-out infinite;
}

/* ── Left Sidebar ── */
.sidebar-left {
  position: fixed;
  left: 20px;
  bottom: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  transition: all 0.25s var(--ease-smooth);
  position: relative;
  border: 1px solid transparent;
}

.sidebar-item:hover {
  color: var(--accent);
  border-color: var(--border-default);
  text-shadow: var(--glow-accent);
}

.sidebar-item.active {
  color: var(--accent);
  border-color: var(--border-glow);
  background: var(--accent-deep);
  box-shadow: var(--glow-accent);
}

.sidebar-item.active::after {
  content: '';
  position: absolute;
  left: -10px;
  width: 2px;
  height: 16px;
  background: var(--accent);
  border-radius: 1px;
  box-shadow: var(--glow-accent);
}

.sidebar-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-line {
  width: 1px;
  height: 60px;
  background: linear-gradient(to bottom, var(--border-glow), transparent);
}

/* ── Right Sidebar ── */
.sidebar-right {
  position: fixed;
  right: 24px;
  bottom: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.social-links {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 12px 0;
}

.social-link {
  color: var(--text-muted);
  transition: all 0.25s var(--ease-smooth);
  display: flex;
  align-items: center;
  justify-content: center;
}

.social-link:hover {
  color: var(--accent);
  transform: translateY(-3px);
  text-shadow: var(--glow-accent);
}

.social-line {
  width: 1px;
  height: 60px;
  background: linear-gradient(to bottom, var(--border-glow), transparent);
}

/* ── Main Content ── */
.layout-main {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 0 60px 100px;
}

/* ── Responsive ── */
@media (max-width: 1080px) {
  .sidebar-left { display: none; }
  .sidebar-right { display: none; }
  .layout-main { padding: 0 24px 80px; }
}

@media (max-width: 768px) {
  .layout-main { padding: 0 16px 60px; }
}
</style>
