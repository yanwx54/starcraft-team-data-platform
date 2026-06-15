<template>
  <div class="map-page">
    <span class="section-number">03.</span>
    <h1 class="page-title">地图</h1>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>
    <div v-else-if="maps.length === 0" class="empty-state">暂无地图数据</div>
    <div v-else class="maps-grid">
      <router-link
        v-for="map in maps"
        :key="map.id"
        :to="`/maps/${map.id}`"
        class="map-card"
      >
        <div class="map-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
        </div>
        <div class="map-name">{{ map.name }}</div>
        <div v-if="map.usage_count !== undefined" class="map-usage">使用次数: {{ map.usage_count }}</div>
        <div v-if="map.season_name" class="map-season">{{ map.season_name }}</div>
        <div v-if="map.win_rate !== undefined" class="map-win-rate">
          <div class="win-rate-bar">
            <div class="win-part" :style="{ width: map.win_rate + '%' }"></div>
          </div>
          <span class="win-rate-text">{{ map.win_rate.toFixed(1) }}%</span>
        </div>
        <div class="map-link">查看详情 →</div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { getMaps } from '../api/maps'

const maps = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getMaps()
    maps.value = res.data || res || []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.map-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-top: 80px;
  padding-bottom: 60px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.map-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  text-decoration: none;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.map-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.map-card:hover {
  border-color: var(--border-glow);
  box-shadow: var(--glow-accent);
}

.map-icon { color: var(--accent); margin-bottom: 4px; }
.map-name { font-family: var(--font-display); font-size: 16px; font-weight: 700; color: var(--text-primary); }
.map-usage { font-family: var(--font-display); font-size: 12px; color: var(--text-secondary); }
.map-season { font-family: var(--font-display); font-size: 12px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em; }

.map-win-rate { display: flex; align-items: center; gap: 8px; }

.win-rate-bar {
  flex: 1; height: 3px; border-radius: 1px; background: var(--bg-void); overflow: hidden;
}

.win-rate-bar .win-part {
  height: 100%; background: linear-gradient(90deg, var(--accent-deep), var(--color-win)); border-radius: 1px; transition: width 0.5s var(--ease-smooth);
  box-shadow: 0 0 4px var(--glow-win);
}

.win-rate-text { font-family: var(--font-display); font-size: 12px; font-weight: 600; color: var(--text-secondary); white-space: nowrap; }

.map-link {
  font-family: var(--font-display); font-size: 12px; font-weight: 600;
  color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; transition: all 0.25s var(--ease-smooth);
}

.map-card:hover .map-link { transform: translateX(4px); }

.loading-container { display: flex; justify-content: center; padding: 48px 0; color: var(--text-muted); }
.empty-state { text-align: center; padding: 48px 0; color: var(--text-dim); font-family: var(--font-display); text-transform: uppercase; letter-spacing: 0.1em; }
</style>
