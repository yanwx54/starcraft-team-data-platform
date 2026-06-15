<template>
  <div class="player-list-page">
    <span class="section-number">02.</span>
    <h1 class="page-title">选手列表</h1>

    <div class="filter-bar">
      <el-input
        v-model="filters.keyword"
        placeholder="搜索选手..."
        clearable
        :prefix-icon="Search"
        @keyup.enter="fetchPlayers"
        @clear="fetchPlayers"
      />
      <el-select v-model="filters.race" placeholder="种族" clearable @change="fetchPlayers">
        <el-option label="人族 (T)" value="T" />
        <el-option label="神族 (P)" value="P" />
        <el-option label="虫族 (Z)" value="Z" />
      </el-select>
      <el-button type="primary" @click="fetchPlayers">搜索</el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>
    <div v-else-if="players.length === 0" class="empty-state">暂无选手数据</div>
    <div v-else class="players-grid">
      <router-link
        v-for="player in players"
        :key="player.id"
        :to="`/players/${player.id}`"
        class="player-card"
      >
        <div class="player-race-badge" :class="getRaceClass(player.race)">{{ player.race }}</div>
        <div class="player-name">{{ player.name }}</div>
        <div v-if="player.game_id" class="player-game-id">{{ player.game_id }}</div>
        <div v-if="player.team_name" class="player-team">{{ player.team_name }}</div>
        <div v-if="player.win_rate !== undefined" class="player-win-rate">
          <div class="win-rate-bar">
            <div class="win-part" :style="{ width: player.win_rate + '%' }"></div>
          </div>
          <span class="win-rate-text">{{ player.win_rate }}%</span>
        </div>
      </router-link>
    </div>

    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchPlayers"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import { getPlayers } from '../api/players'

const players = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 24
const total = ref(0)

const filters = ref({
  keyword: '',
  race: null,
})

function getRaceClass(race) {
  if (!race) return ''
  const r = race.toUpperCase()
  if (r === 'T' || r === 'TERRAN') return 'terran'
  if (r === 'P' || r === 'PROTOSS') return 'protoss'
  if (r === 'Z' || r === 'ZERG') return 'zerg'
  return ''
}

async function fetchPlayers() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.race) params.race = filters.value.race
    const res = await getPlayers(params)
    const data = res.data || res
    players.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPlayers()
})
</script>

<style scoped>
.player-list-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-top: 80px;
  padding-bottom: 60px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-bar .el-input { width: 220px; }

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.player-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 28px 16px 22px;
  text-decoration: none;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.player-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.player-card:hover {
  border-color: var(--border-glow);
  box-shadow: var(--glow-accent);
}

.player-race-badge {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: var(--radius-sm);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.player-race-badge.terran {
  color: var(--race-terran);
  background: var(--race-terran-bg);
  border: 1px solid rgba(0, 212, 255, 0.25);
}

.player-race-badge.protoss {
  color: var(--race-protoss);
  background: var(--race-protoss-bg);
  border: 1px solid rgba(255, 215, 0, 0.25);
}

.player-race-badge.zerg {
  color: var(--race-zerg);
  background: var(--race-zerg-bg);
  border: 1px solid rgba(0, 255, 136, 0.25);
}

.player-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.player-game-id {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
}

.player-team {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-secondary);
}

.player-win-rate {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.win-rate-bar {
  flex: 1;
  height: 3px;
  border-radius: 1px;
  background: var(--bg-void);
  overflow: hidden;
}

.win-rate-bar .win-part {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-deep), var(--color-win));
  border-radius: 1px;
  transition: width 0.5s var(--ease-smooth);
  box-shadow: 0 0 4px var(--glow-win);
}

.win-rate-text {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 48px 0;
  color: var(--text-muted);
}

.empty-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-dim);
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}

.pagination-wrap :deep(.el-pager li) {
  background: var(--bg-card);
  color: var(--text-secondary);
  font-family: var(--font-display);
  border: 1px solid var(--border-dim);
  border-radius: var(--radius-sm);
  transition: all 0.25s var(--ease-smooth);
}

.pagination-wrap :deep(.el-pager li.is-active) {
  background: var(--accent-deep);
  color: var(--accent);
  border: 1px solid var(--accent);
  box-shadow: var(--glow-accent);
}

.pagination-wrap :deep(.btn-prev),
.pagination-wrap :deep(.btn-next) {
  background: var(--bg-card) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border-dim);
  border-radius: var(--radius-sm);
}
</style>
