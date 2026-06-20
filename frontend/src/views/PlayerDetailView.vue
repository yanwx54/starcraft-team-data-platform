<template>
  <div class="player-detail">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>
    <template v-else-if="player">
      <router-link to="/players" class="back-link">← 返回选手列表</router-link>

      <div class="profile-section">
        <div class="profile-card">
          <div class="profile-race" :class="getRaceClass(player.race)">{{ player.race }}</div>
          <h1 class="profile-name">{{ player.name }}</h1>
          <div v-if="player.game_id" class="profile-game-id">
            <span class="label">ID:</span> {{ player.game_id }}
          </div>
          <div v-if="currentTeam" class="profile-team">
            <span class="label">队伍:</span>
            <router-link :to="`/teams/${currentTeam.id}`" class="team-link">{{ currentTeam.name }}</router-link>
          </div>
        </div>

        <div v-if="statistics" class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">总胜场</div>
            <div class="stat-value">{{ statistics.wins ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">总败场</div>
            <div class="stat-value">{{ statistics.losses ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">胜率</div>
            <div class="stat-value" :class="getWinRateColor(statistics.win_rate)">{{ statistics.win_rate ?? 0 }}%</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">最高连胜</div>
            <div class="stat-value">{{ statistics.max_streak ?? 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">累计奖金</div>
            <div class="stat-value prize">₩{{ Number(statistics.total_prize || 0).toLocaleString() }}</div>
          </div>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="地图胜率" name="maps">
          <div v-if="mapStats.length === 0" class="empty-state">暂无地图数据</div>
          <div v-else class="map-stats-grid">
            <div v-for="map in mapStats" :key="map.map_name" class="map-stat-card">
              <div class="map-stat-name">{{ map.map_name }}</div>
              <div class="map-stat-record">{{ map.wins }}胜 {{ map.losses }}负</div>
              <div class="map-stat-bar">
                <div class="win-rate-bar">
                  <div class="win-part" :style="{ width: map.win_rate + '%' }"></div>
                </div>
              </div>
              <div class="map-stat-rate">{{ map.win_rate }}%</div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="历史战绩" name="matches">
          <div v-if="matchLoading" class="loading-container">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          </div>
          <div v-else-if="playerMatches.length === 0" class="empty-state">暂无比赛记录</div>
          <template v-else>
            <el-table :data="playerMatches" stripe style="width: 100%">
              <el-table-column prop="match_date" label="日期" width="120" />
              <el-table-column prop="title" label="比赛" min-width="200">
                <template #default="{ row }">
                  <router-link :to="`/matches/${row.match_id}`" class="table-link">{{ row.title }}</router-link>
                </template>
              </el-table-column>
              <el-table-column prop="map_name" label="地图" width="120" />
              <el-table-column prop="opponent_name" label="对手" width="120">
                <template #default="{ row }">
                  <router-link v-if="row.opponent_id" :to="`/players/${row.opponent_id}`" class="table-link">{{ row.opponent_name }}</router-link>
                  <span v-else>{{ row.opponent_name }}</span>
                </template>
              </el-table-column>
              <el-table-column label="结果" width="80">
                <template #default="{ row }">
                  <span :class="row.is_win ? 'result-win' : 'result-lose'">{{ row.is_win ? '胜' : '负' }}</span>
                </template>
              </el-table-column>
            </el-table>
            <div v-if="matchTotal > matchPageSize" class="pagination-wrap">
              <el-pagination
                v-model:current-page="matchPage"
                :page-size="matchPageSize"
                :total="matchTotal"
                layout="prev, pager, next"
                @current-change="fetchPlayerMatches"
              />
            </div>
          </template>
        </el-tab-pane>

        <!-- 对阵查询 -->
        <el-tab-pane label="对阵查询" name="vs">
          <div class="vs-search">
            <el-select
              v-model="vsOpponentId"
              filterable
              remote
              reserve-keyword
              placeholder="输入选手名称搜索对手"
              :remote-method="searchOpponent"
              :loading="vsSearchLoading"
              value-key="id"
              style="width: 100%; max-width: 400px;"
            >
              <el-option
                v-for="p in vsSearchResults"
                :key="p.id"
                :label="`${p.cn_name || p.game_id} (${p.race || '?'})`"
                :value="p.id"
              />
            </el-select>
            <el-button type="primary" :disabled="!vsOpponentId" @click="goToVsPage">查看对阵</el-button>
          </div>
          <div v-if="vsOpponentId" class="vs-preview">
            <div v-if="vsLoading" class="loading-container">
              <el-icon class="is-loading" :size="24"><Loading /></el-icon>
            </div>
            <template v-else-if="vsData">
              <div class="vs-summary">
                <span class="vs-name">{{ vsData.player?.cn_name || vsData.player?.game_id }}</span>
                <span class="vs-score-win">{{ vsData.wins }}胜</span>
                <span class="vs-score-sep">:</span>
                <span class="vs-score-lose">{{ vsData.losses }}负</span>
                <span class="vs-name">{{ vsData.opponent?.cn_name || vsData.opponent?.game_id }}</span>
                <span class="vs-rate" :class="getWinRateColor(vsData.win_rate)">胜率 {{ vsData.win_rate }}%</span>
              </div>
              <div v-if="vsData.matches.length > 0" class="vs-recent">
                <div class="vs-recent-title">最近对局</div>
                <div v-for="m in vsData.matches.slice(0, 5)" :key="`${m.match_id}-${m.game_no}`" class="vs-recent-item">
                  <span class="vs-recent-date">{{ m.match_date }}</span>
                  <span class="vs-recent-map">{{ m.map_name || '—' }}</span>
                  <span :class="m.winner_player_id === Number(route.params.id) ? 'result-win' : 'result-lose'">{{ m.winner_name }}</span>
                </div>
              </div>
              <router-link :to="`/players/${route.params.id}/vs/${vsOpponentId}`" class="vs-detail-link">查看完整对阵详情 →</router-link>
            </template>
          </div>
        </el-tab-pane>

        <el-tab-pane label="奖金记录" name="prizes">
          <div v-if="prizeLoading" class="loading-container">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          </div>
          <div v-else-if="playerPrizes.length === 0" class="empty-state">暂无奖金记录</div>
          <el-table v-else :data="playerPrizes" stripe style="width: 100%">
            <el-table-column prop="match_date" label="日期" width="120" />
            <el-table-column prop="match_title" label="比赛" min-width="200">
              <template #default="{ row }">
                <router-link v-if="row.match_id" :to="`/matches/${row.match_id}`" class="table-link">{{ row.match_title }}</router-link>
                <span v-else>{{ row.match_title }}</span>
              </template>
            </el-table-column>
            <el-table-column label="奖金" width="150">
              <template #default="{ row }">
                <span class="prize-value">₩{{ Number(row.prize || 0).toLocaleString() }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </template>
    <div v-else class="empty-state">选手数据不存在</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getPlayerDetail, getPlayerMatches, getPlayerPrizes, getPlayerMapStats, getPlayerVsRecord } from '../api/players'
import { getPlayers } from '../api/players'

const route = useRoute()
const router = useRouter()
const player = ref(null)
const statistics = ref(null)
const currentTeam = ref(null)
const mapStats = ref([])
const playerMatches = ref([])
const playerPrizes = ref([])
const loading = ref(true)
const matchLoading = ref(false)
const prizeLoading = ref(false)
const activeTab = ref('maps')
const matchPage = ref(1)
const matchPageSize = 20
const matchTotal = ref(0)

// 对阵查询
const vsOpponentId = ref(null)
const vsSearchLoading = ref(false)
const vsSearchResults = ref([])
const vsLoading = ref(false)
const vsData = ref(null)

function getRaceClass(race) {
  if (!race) return ''
  const r = race.toUpperCase()
  if (r === 'T' || r === 'TERRAN') return 'terran'
  if (r === 'P' || r === 'PROTOSS') return 'protoss'
  if (r === 'Z' || r === 'ZERG') return 'zerg'
  return ''
}

function getWinRateColor(rate) {
  if (!rate) return ''
  if (rate >= 60) return 'rate-high'
  if (rate >= 40) return ''
  return 'rate-low'
}

async function searchOpponent(query) {
  if (!query) {
    vsSearchResults.value = []
    return
  }
  vsSearchLoading.value = true
  try {
    const res = await getPlayers({ keyword: query, page_size: 20 })
    const data = res.data || res
    vsSearchResults.value = (data.items || []).filter(p => p.id !== Number(route.params.id))
  } finally {
    vsSearchLoading.value = false
  }
}

async function fetchVsRecord() {
  if (!vsOpponentId.value) return
  vsLoading.value = true
  try {
    const res = await getPlayerVsRecord(route.params.id, vsOpponentId.value)
    vsData.value = res.data || res
  } finally {
    vsLoading.value = false
  }
}

function goToVsPage() {
  if (vsOpponentId.value) {
    router.push(`/players/${route.params.id}/vs/${vsOpponentId.value}`)
  }
}

watch(vsOpponentId, () => {
  if (vsOpponentId.value) {
    fetchVsRecord()
  } else {
    vsData.value = null
  }
})

async function fetchPlayerMatches() {
  matchLoading.value = true
  try {
    const res = await getPlayerMatches(route.params.id, { page: matchPage.value, page_size: matchPageSize })
    const data = res.data || res
    playerMatches.value = data.items || []
    matchTotal.value = data.total || 0
  } finally {
    matchLoading.value = false
  }
}

async function fetchPlayerPrizes() {
  prizeLoading.value = true
  try {
    const res = await getPlayerPrizes(route.params.id)
    playerPrizes.value = res.data || res || []
  } finally {
    prizeLoading.value = false
  }
}

onMounted(async () => {
  try {
    const [detailRes, mapRes] = await Promise.allSettled([
      getPlayerDetail(route.params.id),
      getPlayerMapStats(route.params.id),
    ])
    if (detailRes.status === 'fulfilled') {
      const data = detailRes.value || {}
      player.value = data.player || data
      statistics.value = data.statistics || null
      currentTeam.value = data.current_team || null
    }
    if (mapRes.status === 'fulfilled') {
      mapStats.value = mapRes.value || []
    }
    fetchPlayerMatches()
    fetchPlayerPrizes()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.player-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 80px;
  padding-bottom: 60px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.profile-section {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.profile-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 32px;
  text-align: center;
  min-width: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.profile-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.profile-card:hover { border-color: var(--border-glow); box-shadow: var(--glow-accent); }

.profile-race {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  padding: 6px 18px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.profile-race.terran { color: var(--race-terran); background: var(--race-terran-bg); border: 1px solid rgba(0, 212, 255, 0.25); }
.profile-race.protoss { color: var(--race-protoss); background: var(--race-protoss-bg); border: 1px solid rgba(255, 215, 0, 0.25); }
.profile-race.zerg { color: var(--race-zerg); background: var(--race-zerg-bg); border: 1px solid rgba(0, 255, 136, 0.25); }

.profile-name {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -1px;
  color: var(--text-primary);
}

.profile-game-id, .profile-team {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--text-secondary);
}

.profile-game-id .label, .profile-team .label { color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em; }

.team-link { color: var(--accent); text-decoration: none; font-weight: 500; }
.team-link:hover { color: var(--accent-dim); }

.stats-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 14px;
}

.rate-high { color: var(--color-win) !important; }
.rate-low { color: var(--color-lose) !important; }
.stat-value.prize { color: var(--color-prize) !important; }

.detail-tabs {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 28px;
  position: relative;
  overflow: hidden;
}

.detail-tabs::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.map-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
}

.map-stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.map-stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.map-stat-card:hover { border-color: var(--border-glow); box-shadow: var(--glow-accent); }

.map-stat-name { font-family: var(--font-display); font-size: 14px; font-weight: 700; color: var(--text-primary); }
.map-stat-record { font-family: var(--font-display); font-size: 12px; color: var(--text-secondary); }
.map-stat-rate { font-family: var(--font-display); font-size: 18px; font-weight: 700; color: var(--accent); }

.table-link { color: var(--accent); text-decoration: none; font-weight: 500; transition: color 0.25s var(--ease-smooth); }
.table-link:hover { color: var(--accent-dim); }

.result-win { color: var(--color-win); font-family: var(--font-display); font-weight: 700; }
.result-lose { color: var(--color-lose); font-family: var(--font-display); font-weight: 700; }
.prize-value { color: var(--color-prize); font-family: var(--font-display); font-weight: 700; }

/* ── VS Search ── */
.vs-search {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.vs-preview {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.vs-preview::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.vs-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.vs-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.vs-score-win {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 800;
  color: var(--color-win);
}

.vs-score-lose {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 800;
  color: var(--color-lose);
}

.vs-score-sep {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--text-muted);
}

.vs-rate {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
  margin-left: 8px;
}

.rate-high { color: var(--color-win) !important; }
.rate-low { color: var(--color-lose) !important; }

.vs-recent {
  margin-bottom: 16px;
}

.vs-recent-title {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.vs-recent-item {
  display: flex;
  gap: 16px;
  padding: 6px 0;
  font-family: var(--font-display);
  font-size: 13px;
  border-bottom: 1px solid var(--border-dim);
}

.vs-recent-date {
  color: var(--text-secondary);
  min-width: 90px;
}

.vs-recent-map {
  color: var(--text-primary);
  min-width: 100px;
}

.vs-detail-link {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  display: inline-block;
  margin-top: 8px;
  transition: all 0.25s var(--ease-smooth);
}

.vs-detail-link:hover {
  transform: translateX(4px);
}

.pagination-wrap { display: flex; justify-content: center; padding-top: 16px; }

.pagination-wrap :deep(.el-pager li) {
  background: var(--bg-card); color: var(--text-secondary); font-family: var(--font-display);
  border: 1px solid var(--border-dim); border-radius: var(--radius-sm);
  transition: all 0.25s var(--ease-smooth);
}

.pagination-wrap :deep(.el-pager li.is-active) {
  background: var(--accent-deep); color: var(--accent); border: 1px solid var(--accent);
  box-shadow: var(--glow-accent);
}

.pagination-wrap :deep(.btn-prev),
.pagination-wrap :deep(.btn-next) {
  background: var(--bg-card) !important; color: var(--text-secondary) !important;
  border: 1px solid var(--border-dim); border-radius: var(--radius-sm);
}

.detail-tabs :deep(.el-table) {
  --el-table-border-color: var(--border-dim);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-tr-bg-color: var(--bg-card);
  --el-table-row-hover-bg-color: var(--bg-card-hover);
  border-radius: var(--radius-sm); overflow: hidden;
}

.detail-tabs :deep(.el-table th.el-table__cell) {
  font-family: var(--font-display); font-size: 12px; font-weight: 700;
  color: var(--text-muted); background: var(--bg-secondary);
  text-transform: uppercase; letter-spacing: 0.08em;
}

.detail-tabs :deep(.el-table td.el-table__cell) { border-bottom: 1px solid var(--border-dim); }

.loading-container { display: flex; justify-content: center; align-items: center; min-height: 200px; color: var(--text-muted); }
.empty-state { text-align: center; color: var(--text-dim); padding: 40px 0; font-family: var(--font-display); font-size: 13px; text-transform: uppercase; letter-spacing: 0.1em; }

@media (max-width: 768px) { .profile-section { flex-direction: column; } }
</style>
