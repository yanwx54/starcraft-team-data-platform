<template>
  <div class="player-vs">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>
    <template v-else-if="data">
      <router-link :to="`/players/${playerId}`" class="back-link">← 返回选手详情</router-link>

      <!-- 双方选手对比 -->
      <div class="vs-header">
        <div class="vs-player" :class="{ winner: data.wins > data.losses }">
          <div class="vs-player-race" :class="getRaceClass(data.player?.race)">{{ data.player?.race }}</div>
          <div class="vs-player-name">{{ data.player?.cn_name || data.player?.game_id || '—' }}</div>
          <div v-if="data.player?.game_id" class="vs-player-id">{{ data.player.game_id }}</div>
          <div class="vs-player-score">{{ data.wins }}</div>
          <div class="vs-player-label">胜</div>
        </div>

        <div class="vs-center">
          <div class="vs-badge">VS</div>
          <div class="vs-total">{{ data.total }} 局</div>
          <div class="vs-win-rate" :class="getWinRateColor(data.win_rate)">胜率 {{ data.win_rate }}%</div>
          <div class="vs-rate-bar">
            <div class="win-part" :style="{ width: data.win_rate + '%' }"></div>
          </div>
        </div>

        <div class="vs-player" :class="{ winner: data.losses > data.wins }">
          <div class="vs-player-race" :class="getRaceClass(data.opponent?.race)">{{ data.opponent?.race }}</div>
          <div class="vs-player-name">{{ data.opponent?.cn_name || data.opponent?.game_id || '—' }}</div>
          <div v-if="data.opponent?.game_id" class="vs-player-id">{{ data.opponent.game_id }}</div>
          <div class="vs-player-score">{{ data.losses }}</div>
          <div class="vs-player-label">胜</div>
        </div>
      </div>

      <!-- 对局明细 -->
      <div class="section">
        <div class="section-header">
          <h2 class="section-title">对局明细</h2>
        </div>
        <div v-if="data.matches.length === 0" class="empty-state">暂无对局记录</div>
        <el-table v-else :data="data.matches" stripe style="width: 100%">
          <el-table-column label="#" width="60" align="center">
            <template #default="{ row }">{{ row.game_no }}</template>
          </el-table-column>
          <el-table-column prop="match_date" label="日期" width="120" />
          <el-table-column prop="title" label="比赛" min-width="200">
            <template #default="{ row }">
              <router-link :to="`/matches/${row.match_id}`" class="table-link">{{ row.title || '—' }}</router-link>
            </template>
          </el-table-column>
          <el-table-column prop="map_name" label="地图" width="140">
            <template #default="{ row }">{{ row.map_name || '—' }}</template>
          </el-table-column>
          <el-table-column label="胜者" width="140">
            <template #default="{ row }">
              <span :class="row.winner_player_id === playerId ? 'result-win' : 'result-lose'">
                {{ row.winner_name || '—' }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>
    <div v-else class="empty-state">未找到对阵数据</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getPlayerVsRecord } from '../api/players'

const route = useRoute()
const playerId = Number(route.params.id)
const opponentId = Number(route.params.opponentId)
const data = ref(null)
const loading = ref(true)

function getRaceClass(race) {
  if (!race) return ''
  const r = race.toUpperCase()
  if (r === 'T') return 'terran'
  if (r === 'P') return 'protoss'
  if (r === 'Z') return 'zerg'
  return ''
}

function getWinRateColor(rate) {
  if (!rate) return ''
  if (rate >= 60) return 'rate-high'
  if (rate >= 40) return ''
  return 'rate-low'
}

onMounted(async () => {
  try {
    const res = await getPlayerVsRecord(playerId, opponentId)
    data.value = res.data || res
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.player-vs {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 40px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

/* ── VS Header ── */
.vs-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 36px 24px;
}

.vs-player {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  max-width: 240px;
}

.vs-player.winner {
  background: var(--color-win-bg);
  border: 1px solid rgba(100, 255, 218, 0.15);
  border-radius: var(--radius-md);
  padding: 20px 16px;
}

.vs-player-race {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: var(--radius-sm);
}

.vs-player-race.terran { color: var(--race-terran); background: var(--race-terran-bg); border: 1px solid rgba(100, 255, 218, 0.2); }
.vs-player-race.protoss { color: var(--race-protoss); background: var(--race-protoss-bg); border: 1px solid rgba(255, 215, 0, 0.2); }
.vs-player-race.zerg { color: var(--race-zerg); background: var(--race-zerg-bg); border: 1px solid rgba(168, 230, 207, 0.2); }

.vs-player-name {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.vs-player-id {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-secondary);
}

.vs-player-score {
  font-family: var(--font-mono);
  font-size: 48px;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
}

.vs-player.winner .vs-player-score {
  color: var(--color-win);
}

.vs-player-label {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* ── VS Center ── */
.vs-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  min-width: 120px;
}

.vs-badge {
  font-family: var(--font-mono);
  font-size: 24px;
  font-weight: 800;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}

.vs-total {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--text-secondary);
}

.vs-win-rate {
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
}

.rate-high { color: var(--color-win) !important; }
.rate-low { color: var(--color-lose) !important; }

.vs-rate-bar {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: var(--bg-dark);
  overflow: hidden;
}

.vs-rate-bar .win-part {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.5s var(--ease-smooth);
}

/* ── Table ── */
.table-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.25s var(--ease-smooth);
}

.table-link:hover { color: var(--accent-light); }

.result-win { color: var(--color-win); font-family: var(--font-mono); font-weight: 700; }
.result-lose { color: var(--color-lose); font-family: var(--font-mono); font-weight: 700; }

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  color: var(--text-muted);
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 0;
  font-family: var(--font-mono);
  font-size: 13px;
}

@media (max-width: 768px) {
  .vs-header {
    flex-direction: column;
    gap: 20px;
    padding: 24px 16px;
  }

  .vs-player-name { font-size: 22px; }
  .vs-player-score { font-size: 36px; }
}
</style>
