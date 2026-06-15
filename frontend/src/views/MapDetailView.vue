<template>
  <div class="map-detail">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>
    <template v-else-if="map">
      <router-link to="/maps" class="back-link">← 返回地图列表</router-link>

      <div class="map-header">
        <div class="map-icon-large">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>
        </div>
        <h1 class="map-name">{{ map.name }}</h1>
        <div class="map-meta">
          <span v-if="map.usage_count !== undefined" class="meta-item">使用次数: {{ map.usage_count }}</span>
          <span v-if="map.season_name" class="meta-item">赛季: {{ map.season_name }}</span>
        </div>
      </div>

      <div v-if="raceStats" class="section">
        <h2 class="section-title">
          <span class="section-number-inline">01.</span> 种族胜率
        </h2>
        <div class="race-stats-grid">
          <div v-if="raceStats.T !== undefined" class="race-stat-card terran">
            <div class="race-label">人族 (T)</div>
            <div class="race-value">{{ raceStats.T }}%</div>
            <div class="race-bar"><div class="race-bar-fill" :style="{ width: raceStats.T + '%' }"></div></div>
          </div>
          <div v-if="raceStats.P !== undefined" class="race-stat-card protoss">
            <div class="race-label">神族 (P)</div>
            <div class="race-value">{{ raceStats.P }}%</div>
            <div class="race-bar"><div class="race-bar-fill" :style="{ width: raceStats.P + '%' }"></div></div>
          </div>
          <div v-if="raceStats.Z !== undefined" class="race-stat-card zerg">
            <div class="race-label">虫族 (Z)</div>
            <div class="race-value">{{ raceStats.Z }}%</div>
            <div class="race-bar"><div class="race-bar-fill" :style="{ width: raceStats.Z + '%' }"></div></div>
          </div>
        </div>
      </div>

      <div v-if="statistics" class="section">
        <h2 class="section-title">
          <span class="section-number-inline">02.</span> 统计信息
        </h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">总对局数</div>
            <div class="stat-value">{{ statistics.total_games ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">人族胜场</div>
            <div class="stat-value terran-stat">{{ statistics.terran_wins ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">神族胜场</div>
            <div class="stat-value protoss-stat">{{ statistics.protoss_wins ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">虫族胜场</div>
            <div class="stat-value zerg-stat">{{ statistics.zerg_wins ?? 0 }}</div>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="empty-state">地图数据不存在</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getMapDetail, getMapRaceStats } from '../api/maps'

const route = useRoute()
const map = ref(null)
const raceStats = ref(null)
const statistics = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const [detailRes, raceRes] = await Promise.allSettled([
      getMapDetail(route.params.id),
      getMapRaceStats(route.params.id),
    ])
    if (detailRes.status === 'fulfilled') {
      const data = detailRes.value.data || detailRes.value
      map.value = data.map || data
      statistics.value = data.statistics || null
    }
    if (raceRes.status === 'fulfilled') {
      raceStats.value = raceRes.value.data || raceRes.value || null
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.map-detail {
  display: flex; flex-direction: column; gap: 24px;
  padding-top: 80px; padding-bottom: 60px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.map-header {
  background: var(--bg-card); border: 1px solid var(--border-default);
  border-radius: var(--radius-md); padding: 32px;
  display: flex; flex-direction: column; align-items: center; text-align: center;
  position: relative; overflow: hidden;
}

.map-header::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.map-icon-large { color: var(--accent); margin-bottom: 16px; }

.map-name {
  font-family: var(--font-display); font-size: 36px; font-weight: 800;
  letter-spacing: -1px; margin-bottom: 12px; color: var(--text-primary);
}

.map-meta { display: flex; gap: 16px; }
.meta-item { font-family: var(--font-display); font-size: 13px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em; }

.section-number-inline {
  font-family: var(--font-display); font-size: 14px; font-weight: 600;
  color: var(--accent); margin-right: 8px;
}

.race-stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }

.race-stat-card {
  border-radius: var(--radius-sm); padding: 20px; text-align: center;
  position: relative; overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.race-stat-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.race-stat-card:hover { transform: translateY(-2px); border-color: var(--border-glow); box-shadow: var(--glow-accent); }

.race-stat-card.terran { background: var(--race-terran-bg); border: 1px solid rgba(0, 212, 255, 0.25); }
.race-stat-card.protoss { background: var(--race-protoss-bg); border: 1px solid rgba(255, 215, 0, 0.25); }
.race-stat-card.zerg { background: var(--race-zerg-bg); border: 1px solid rgba(0, 255, 136, 0.25); }

.race-label {
  font-family: var(--font-display); font-size: 12px; font-weight: 700;
  margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.1em;
}

.race-stat-card.terran .race-label { color: var(--race-terran); }
.race-stat-card.protoss .race-label { color: var(--race-protoss); }
.race-stat-card.zerg .race-label { color: var(--race-zerg); }

.race-value {
  font-family: var(--font-display); font-size: 32px; font-weight: 800;
  letter-spacing: -1px; color: var(--text-primary); margin-bottom: 12px;
}

.race-bar { height: 3px; border-radius: 1px; background: var(--bg-void); overflow: hidden; }
.race-bar-fill { height: 100%; border-radius: 1px; transition: width 0.5s var(--ease-smooth); }
.race-stat-card.terran .race-bar-fill { background: linear-gradient(90deg, var(--accent-deep), var(--race-terran)); box-shadow: 0 0 4px rgba(0, 212, 255, 0.3); }
.race-stat-card.protoss .race-bar-fill { background: linear-gradient(90deg, var(--accent-deep), var(--race-protoss)); box-shadow: 0 0 4px rgba(255, 215, 0, 0.3); }
.race-stat-card.zerg .race-bar-fill { background: linear-gradient(90deg, var(--accent-deep), var(--race-zerg)); box-shadow: 0 0 4px rgba(0, 255, 136, 0.3); }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.terran-stat { color: var(--race-terran) !important; }
.protoss-stat { color: var(--race-protoss) !important; }
.zerg-stat { color: var(--race-zerg) !important; }

.loading-container { display: flex; justify-content: center; align-items: center; min-height: 200px; color: var(--text-muted); }
.empty-state { text-align: center; color: var(--text-dim); padding: 40px 0; font-family: var(--font-display); font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em; }

@media (max-width: 768px) {
  .race-stats-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
