<template>
  <div class="vs-query">
    <span class="section-number">05. Head-to-Head</span>
    <h1 class="page-title">对战查询</h1>

    <!-- 查询表单 -->
    <div class="query-panel section">
      <div class="query-row">
        <div class="query-player">
          <label class="query-label">选手 A</label>
          <el-select
            v-model="playerAId"
            filterable
            remote
            reserve-keyword
            placeholder="搜索选手..."
            :remote-method="searchPlayers"
            :loading="searchLoading"
            @change="onPlayerSelected"
          >
            <el-option
              v-for="p in playerOptions"
              :key="p.id"
              :label="p.cn_name || p.game_id"
              :value="p.id"
            >
              <div class="option-inner">
                <span class="race-tag" :class="getRaceClass(p.race)">{{ p.race }}</span>
                <span class="option-name">{{ p.cn_name || p.game_id }}</span>
              </div>
            </el-option>
          </el-select>
        </div>

        <div class="vs-divider">
          <div class="vs-icon">VS</div>
        </div>

        <div class="query-player">
          <label class="query-label">选手 B</label>
          <el-select
            v-model="playerBId"
            filterable
            remote
            reserve-keyword
            placeholder="搜索选手..."
            :remote-method="searchPlayers"
            :loading="searchLoading"
            @change="onPlayerSelected"
          >
            <el-option
              v-for="p in playerOptions"
              :key="p.id"
              :label="p.cn_name || p.game_id"
              :value="p.id"
            >
              <div class="option-inner">
                <span class="race-tag" :class="getRaceClass(p.race)">{{ p.race }}</span>
                <span class="option-name">{{ p.cn_name || p.game_id }}</span>
              </div>
            </el-option>
          </el-select>
        </div>
      </div>

      <div class="query-actions">
        <el-button type="primary" :disabled="!canQuery" @click="doQuery">
          查询对战记录
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="queryLoading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>

    <!-- 查询结果 -->
    <template v-else-if="vsData">
      <!-- 双方对比 -->
      <div class="vs-header">
        <div class="vs-player" :class="{ winner: vsData.wins > vsData.losses }">
          <router-link :to="`/players/${playerAId}`" class="vs-player-link">
            <div class="vs-player-race" :class="getRaceClass(vsData.player?.race)">{{ vsData.player?.race }}</div>
            <div class="vs-player-name">{{ vsData.player?.cn_name || vsData.player?.game_id || '—' }}</div>
            <div v-if="vsData.player?.game_id" class="vs-player-id">{{ vsData.player.game_id }}</div>
          </router-link>
          <div class="vs-player-score">{{ vsData.wins }}</div>
          <div class="vs-player-label">胜</div>
        </div>

        <div class="vs-center">
          <div class="vs-badge">VS</div>
          <div class="vs-total">{{ vsData.total }} 局</div>
          <div class="vs-win-rate" :class="getWinRateColor(vsData.win_rate)">胜率 {{ vsData.win_rate }}%</div>
          <div class="vs-rate-bar">
            <div class="win-part" :style="{ width: vsData.win_rate + '%' }"></div>
          </div>
        </div>

        <div class="vs-player" :class="{ winner: vsData.losses > vsData.wins }">
          <router-link :to="`/players/${playerBId}`" class="vs-player-link">
            <div class="vs-player-race" :class="getRaceClass(vsData.opponent?.race)">{{ vsData.opponent?.race }}</div>
            <div class="vs-player-name">{{ vsData.opponent?.cn_name || vsData.opponent?.game_id || '—' }}</div>
            <div v-if="vsData.opponent?.game_id" class="vs-player-id">{{ vsData.opponent.game_id }}</div>
          </router-link>
          <div class="vs-player-score">{{ vsData.losses }}</div>
          <div class="vs-player-label">胜</div>
        </div>
      </div>

      <!-- 对局明细 -->
      <div class="section" style="margin-top: 24px;">
        <div class="section-header">
          <h2 class="section-title">对局明细</h2>
        </div>
        <div v-if="vsData.matches && vsData.matches.length === 0" class="empty-state">暂无对局记录</div>
        <el-table v-else :data="vsData.matches" stripe style="width: 100%">
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
              <span :class="row.winner_player_id === playerAId ? 'result-win' : 'result-lose'">
                {{ row.winner_name || '—' }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <!-- 空状态 -->
    <div v-else-if="hasQueried" class="empty-state">未找到对阵数据</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getPlayers, getPlayerVsRecord } from '../api/players'

const route = useRoute()

const playerAId = ref(null)
const playerBId = ref(null)
const playerOptions = ref([])
const searchLoading = ref(false)
const queryLoading = ref(false)
const vsData = ref(null)
const hasQueried = ref(false)

const canQuery = computed(() => playerAId.value && playerBId.value && playerAId.value !== playerBId.value)

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

async function searchPlayers(query) {
  if (!query) return
  searchLoading.value = true
  try {
    const res = await getPlayers({ keyword: query, page_size: 20 })
    const data = res.data || res
    playerOptions.value = data.items || data || []
  } finally {
    searchLoading.value = false
  }
}

function onPlayerSelected() {
  // Auto-query when both players are selected
  if (canQuery.value) {
    doQuery()
  }
}

async function doQuery() {
  if (!canQuery.value) return
  queryLoading.value = true
  hasQueried.value = true
  try {
    const res = await getPlayerVsRecord(playerAId.value, playerBId.value)
    vsData.value = res.data || res
  } finally {
    queryLoading.value = false
  }
}

onMounted(() => {
  // Support pre-filled params from route
  const a = route.query.playerA
  const b = route.query.playerB
  if (a && b) {
    playerAId.value = Number(a)
    playerBId.value = Number(b)
    doQuery()
  }
})
</script>

<style scoped>
.vs-query {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 40px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

/* ── Query Panel ── */
.query-panel {
  padding: 28px;
}

.query-row {
  display: flex;
  align-items: flex-end;
  gap: 20px;
}

.query-player {
  flex: 1;
}

.query-label {
  display: block;
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 8px;
}

.vs-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-bottom: 8px;
}

.vs-icon {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 800;
  color: var(--text-dim);
  letter-spacing: 0.1em;
  padding: 8px 4px;
}

.query-actions {
  margin-top: 20px;
  text-align: center;
}

.option-inner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-name {
  font-size: 14px;
  color: var(--text-primary);
}

/* ── VS Header ── */
.vs-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 36px 24px;
  position: relative;
  overflow: hidden;
}

.vs-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.vs-player {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  max-width: 240px;
  padding: 20px 16px;
  border-radius: var(--radius-md);
  transition: all 0.3s var(--ease-smooth);
}

.vs-player.winner {
  background: var(--color-win-bg);
  border: 1px solid rgba(0, 255, 136, 0.15);
  box-shadow: 0 0 16px rgba(0, 255, 136, 0.08);
}

.vs-player-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: opacity 0.25s var(--ease-smooth);
}

.vs-player-link:hover {
  opacity: 0.8;
}

.vs-player-race {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: var(--radius-sm);
}

.vs-player-race.terran { color: var(--race-terran); background: var(--race-terran-bg); border: 1px solid rgba(0, 212, 255, 0.25); }
.vs-player-race.protoss { color: var(--race-protoss); background: var(--race-protoss-bg); border: 1px solid rgba(255, 215, 0, 0.25); }
.vs-player-race.zerg { color: var(--race-zerg); background: var(--race-zerg-bg); border: 1px solid rgba(0, 255, 136, 0.25); }

.vs-player-name {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.vs-player-id {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-secondary);
}

.vs-player-score {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1;
}

.vs-player.winner .vs-player-score {
  color: var(--color-win);
  text-shadow: 0 0 12px var(--glow-win);
}

.vs-player-label {
  font-family: var(--font-display);
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
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 800;
  color: var(--text-dim);
  letter-spacing: 0.1em;
}

.vs-total {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--text-secondary);
}

.vs-win-rate {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
}

.rate-high { color: var(--color-win) !important; text-shadow: 0 0 8px var(--glow-win); }
.rate-low { color: var(--color-lose) !important; text-shadow: 0 0 8px var(--glow-lose); }

.vs-rate-bar {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: var(--bg-void);
  overflow: hidden;
}

.vs-rate-bar .win-part {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-deep), var(--accent));
  border-radius: 2px;
  transition: width 0.5s var(--ease-smooth);
  box-shadow: 0 0 4px var(--accent-glow);
}

/* ── Table ── */
.table-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.25s var(--ease-smooth);
}

.table-link:hover { text-shadow: var(--glow-accent); }

.result-win { color: var(--color-win); font-family: var(--font-display); font-weight: 700; }
.result-lose { color: var(--color-lose); font-family: var(--font-display); font-weight: 700; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .query-row {
    flex-direction: column;
    gap: 12px;
  }

  .vs-divider {
    padding-bottom: 0;
  }

  .vs-header {
    flex-direction: column;
    gap: 20px;
    padding: 24px 16px;
  }

  .vs-player-name { font-size: 22px; }
  .vs-player-score { font-size: 36px; }
}
</style>
