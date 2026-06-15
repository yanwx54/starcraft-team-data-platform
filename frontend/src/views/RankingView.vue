<template>
  <div class="ranking-page">
    <span class="section-number">04.</span>
    <h1 class="page-title">排行榜</h1>

    <div class="period-bar">
      <button
        v-for="p in periods"
        :key="p.value"
        class="period-btn"
        :class="{ active: period === p.value }"
        @click="changePeriod(p.value)"
      >{{ p.label }}</button>
      <div v-if="period === 'custom'" class="period-date">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="—"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          size="small"
          @change="refreshAll"
        />
      </div>
    </div>

    <el-tabs v-model="activeTab" class="ranking-tabs">
      <el-tab-pane label="胜场排行" name="wins">
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading" :size="28"><Loading /></el-icon>
        </div>
        <el-table v-else :data="winRanking" stripe style="width: 100%">
          <el-table-column label="排名" width="70">
            <template #default="{ $index }">
              <span class="rank-pos" :class="{ 'top3': $index < 3 }">{{ String($index + 1).padStart(2, '0') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="选手" min-width="150">
            <template #default="{ row }">
              <router-link :to="`/players/${row.player_id}`" class="table-link">{{ row.player_name }}</router-link>
            </template>
          </el-table-column>
          <el-table-column prop="race" label="种族" width="80">
            <template #default="{ row }">
              <span :class="getRaceClass(row.race)">{{ row.race }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="wins" label="胜场" width="100">
            <template #default="{ row }">
              <span class="value-highlight">{{ row.wins }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="losses" label="败场" width="100" />
          <el-table-column prop="win_rate" label="胜率" width="120">
            <template #default="{ row }">
              <div class="rate-cell">
                <div class="mini-bar"><div class="mini-bar-fill" :style="{ width: row.win_rate + '%' }"></div></div>
                <span class="rate-text">{{ row.win_rate }}%</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="胜率排行" name="win-rate">
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading" :size="28"><Loading /></el-icon>
        </div>
        <el-table v-else :data="winRateRanking" stripe style="width: 100%">
          <el-table-column label="排名" width="70">
            <template #default="{ $index }">
              <span class="rank-pos" :class="{ 'top3': $index < 3 }">{{ String($index + 1).padStart(2, '0') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="选手" min-width="150">
            <template #default="{ row }">
              <router-link :to="`/players/${row.player_id}`" class="table-link">{{ row.player_name }}</router-link>
            </template>
          </el-table-column>
          <el-table-column prop="race" label="种族" width="80">
            <template #default="{ row }">
              <span :class="getRaceClass(row.race)">{{ row.race }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_games" label="总场次" width="100" />
          <el-table-column prop="win_rate" label="胜率" width="120">
            <template #default="{ row }">
              <span class="value-highlight rate-value">{{ row.win_rate }}%</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="奖金排行" name="prize">
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading" :size="28"><Loading /></el-icon>
        </div>
        <el-table v-else :data="prizeRanking" stripe style="width: 100%">
          <el-table-column label="排名" width="70">
            <template #default="{ $index }">
              <span class="rank-pos" :class="{ 'top3': $index < 3 }">{{ String($index + 1).padStart(2, '0') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="选手" min-width="150">
            <template #default="{ row }">
              <router-link :to="`/players/${row.player_id}`" class="table-link">{{ row.player_name }}</router-link>
            </template>
          </el-table-column>
          <el-table-column prop="race" label="种族" width="80">
            <template #default="{ row }">
              <span :class="getRaceClass(row.race)">{{ row.race }}</span>
            </template>
          </el-table-column>
          <el-table-column label="奖金" width="160">
            <template #default="{ row }">
              <span class="prize-value">₩{{ Number(row.total_prize || 0).toLocaleString() }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="连胜排行" name="streak">
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading" :size="28"><Loading /></el-icon>
        </div>
        <el-table v-else :data="streakRanking" stripe style="width: 100%">
          <el-table-column label="排名" width="70">
            <template #default="{ $index }">
              <span class="rank-pos" :class="{ 'top3': $index < 3 }">{{ String($index + 1).padStart(2, '0') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="选手" min-width="150">
            <template #default="{ row }">
              <router-link :to="`/players/${row.player_id}`" class="table-link">{{ row.player_name }}</router-link>
            </template>
          </el-table-column>
          <el-table-column prop="race" label="种族" width="80">
            <template #default="{ row }">
              <span :class="getRaceClass(row.race)">{{ row.race }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="max_streak" label="最高连胜" width="120">
            <template #default="{ row }">
              <span class="streak-value">{{ row.max_streak }}连胜</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { getWinRanking, getWinRateRanking, getPrizeRanking, getStreakRanking } from '../api/rankings'

const periods = [
  { label: '总排行', value: 'all' },
  { label: '本赛季', value: 'season' },
  { label: '近30天', value: '30d' },
  { label: '近7天', value: '7d' },
  { label: '自定义', value: 'custom' },
]

const activeTab = ref('wins')
const period = ref('all')
const dateRange = ref(null)
const loading = ref(true)
const winRanking = ref([])
const winRateRanking = ref([])
const prizeRanking = ref([])
const streakRanking = ref([])

function getRaceClass(race) {
  if (!race) return ''
  const r = race.toUpperCase()
  if (r === 'T' || r === 'TERRAN') return 'race-tag terran'
  if (r === 'P' || r === 'PROTOSS') return 'race-tag protoss'
  if (r === 'Z' || r === 'ZERG') return 'race-tag zerg'
  return ''
}

function getPeriodParams() {
  const params = {}
  if (period.value === 'season') params.period = 'season'
  else if (period.value === '30d') params.period = '30d'
  else if (period.value === '7d') params.period = '7d'
  else if (period.value === 'custom' && dateRange.value) {
    params.date_from = dateRange.value[0]
    params.date_to = dateRange.value[1]
  }
  return params
}

const fetchMap = { wins: getWinRanking, 'win-rate': getWinRateRanking, prize: getPrizeRanking, streak: getStreakRanking }
const dataMap = { wins: winRanking, 'win-rate': winRateRanking, prize: prizeRanking, streak: streakRanking }

async function fetchTab(tab) {
  const fn = fetchMap[tab]; const data = dataMap[tab]
  if (!fn || !data) return
  loading.value = true
  try { const res = await fn(getPeriodParams()); data.value = res.data || res || [] }
  finally { loading.value = false }
}

function changePeriod(p) { period.value = p; if (p !== 'custom') refreshAll() }

function refreshAll() {
  winRanking.value = []; winRateRanking.value = []; prizeRanking.value = []; streakRanking.value = []
  fetchTab(activeTab.value)
}

onMounted(() => { fetchTab(activeTab.value) })
watch(activeTab, (tab) => { const data = dataMap[tab]; if (data && data.value.length === 0) fetchTab(tab) })
</script>

<style scoped>
.ranking-page {
  display: flex; flex-direction: column; gap: 32px;
  padding-top: 80px;
  padding-bottom: 60px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.period-bar { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }

.period-btn {
  font-family: var(--font-display); padding: 7px 18px; border-radius: var(--radius-sm);
  border: 1px solid var(--border-default); background: transparent;
  color: var(--text-secondary); cursor: pointer; font-size: 12px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.08em;
  transition: all 0.25s var(--ease-smooth);
}

.period-btn:hover { border-color: var(--border-glow); color: var(--accent); }
.period-btn.active { background: var(--accent-deep); border-color: var(--accent); color: var(--accent); box-shadow: var(--glow-accent); }

.period-date { display: flex; gap: 8px; align-items: center; }

.ranking-tabs {
  background: var(--bg-card); border: 1px solid var(--border-default);
  border-radius: var(--radius-md); padding: 28px;
  position: relative; overflow: hidden;
}

.ranking-tabs::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.rank-pos { font-family: var(--font-display); font-size: 12px; font-weight: 600; color: var(--text-muted); }
.rank-pos.top3 { color: var(--color-prize); text-shadow: var(--glow-prize); }

.table-link { color: var(--accent); text-decoration: none; font-weight: 600; transition: color 0.25s var(--ease-smooth); }
.table-link:hover { color: var(--accent-dim); }

.value-highlight { font-family: var(--font-display); font-weight: 700; color: var(--color-win); }
.rate-value { font-size: 16px; }

.rate-cell { display: flex; align-items: center; gap: 8px; }
.mini-bar { width: 60px; height: 3px; border-radius: 1px; background: var(--bg-void); overflow: hidden; }
.mini-bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent-deep), var(--color-win)); border-radius: 1px; transition: width 0.5s var(--ease-smooth); box-shadow: 0 0 4px var(--glow-win); }
.rate-text { font-family: var(--font-display); font-size: 12px; color: var(--text-secondary); }

.prize-value { font-family: var(--font-display); color: var(--color-prize); font-weight: 700; font-size: 13px; }
.streak-value { font-family: var(--font-display); color: var(--color-streak); font-weight: 700; font-size: 13px; }

.ranking-tabs :deep(.el-table) {
  --el-table-border-color: var(--border-dim);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-tr-bg-color: var(--bg-card);
  --el-table-row-hover-bg-color: var(--bg-card-hover);
  border-radius: var(--radius-sm); overflow: hidden;
}

.ranking-tabs :deep(.el-table th.el-table__cell) {
  font-family: var(--font-display); font-size: 12px; font-weight: 700;
  color: var(--text-muted); background: var(--bg-secondary);
  text-transform: uppercase; letter-spacing: 0.08em;
}

.ranking-tabs :deep(.el-table td.el-table__cell) { border-bottom: 1px solid var(--border-dim); }

.loading-container { display: flex; justify-content: center; align-items: center; min-height: 200px; color: var(--text-muted); }
.empty-state { text-align: center; color: var(--text-dim); padding: 40px 0; font-family: var(--font-display); font-size: 13px; text-transform: uppercase; letter-spacing: 0.1em; }
</style>
