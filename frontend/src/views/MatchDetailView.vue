<template>
  <div class="match-detail">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>
    <template v-else-if="match">
      <router-link to="/matches" class="back-link">← 返回比赛列表</router-link>

      <div class="match-header">
        <div class="match-header-top">
          <span class="match-date">{{ match.match_date }}</span>
          <span v-if="match.wr_id" class="match-wr">#{{ match.wr_id }}</span>
        </div>
        <h1 class="match-title">{{ match.title }}</h1>
      </div>

      <div v-if="teams && teams.length" class="teams-section">
        <div v-for="team in teams" :key="team.id" class="team-card">
          <router-link :to="`/teams/${team.id}`" class="team-name">{{ team.name }}</router-link>
          <div v-if="team.score !== undefined" class="team-score">{{ team.score }}</div>
        </div>
      </div>

      <div v-if="stages && stages.length" class="section">
        <h2 class="section-title">
          <span class="section-number-inline">01.</span> 比赛阶段
        </h2>
        <div class="stages-list">
          <div v-for="(stage, idx) in stages" :key="idx" class="stage-item">
            <span class="stage-type">{{ stage.stage_type }}</span>
            <span v-if="stage.winner_team_name" class="stage-winner">胜者: {{ stage.winner_team_name }}</span>
          </div>
        </div>
      </div>

      <div v-if="games && games.length" class="section">
        <h2 class="section-title">
          <span class="section-number-inline">02.</span> 对局明细
        </h2>
        <el-table :data="games" stripe style="width: 100%">
          <el-table-column prop="stage_type" label="阶段" width="80" />
          <el-table-column prop="game_number" label="局" width="60" />
          <el-table-column label="选手A" min-width="120">
            <template #default="{ row }">
              <router-link v-if="row.player_a_id" :to="`/players/${row.player_a_id}`" class="table-link">
                <span :class="getRaceClass(row.player_a_race)">{{ row.player_a_race }}</span>
                {{ row.player_a_name }}
              </router-link>
              <span v-else>{{ row.player_a_name || '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="VS" width="50" align="center">
            <template #default><span class="vs-text">vs</span></template>
          </el-table-column>
          <el-table-column label="选手B" min-width="120">
            <template #default="{ row }">
              <router-link v-if="row.player_b_id" :to="`/players/${row.player_b_id}`" class="table-link">
                <span :class="getRaceClass(row.player_b_race)">{{ row.player_b_race }}</span>
                {{ row.player_b_name }}
              </router-link>
              <span v-else>{{ row.player_b_name || '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="map_name" label="地图" width="120" />
          <el-table-column label="胜者" min-width="120">
            <template #default="{ row }">
              <span class="winner-text">{{ row.winner_name || '—' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="prizes && prizes.length" class="section">
        <h2 class="section-title">
          <span class="section-number-inline">03.</span> 奖金分配
        </h2>
        <el-table :data="prizes" stripe style="width: 100%">
          <el-table-column prop="player_name" label="选手" min-width="150">
            <template #default="{ row }">
              <router-link v-if="row.player_id" :to="`/players/${row.player_id}`" class="table-link">{{ row.player_name }}</router-link>
              <span v-else>{{ row.player_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="team_name" label="队伍" width="150" />
          <el-table-column label="奖金" width="150">
            <template #default="{ row }">
              <span class="prize-value">₩{{ Number(row.prize || 0).toLocaleString() }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>
    <div v-else class="empty-state">比赛数据不存在</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { getMatchDetail } from '../api/matches'

const route = useRoute()
const match = ref(null)
const teams = ref([])
const stages = ref([])
const games = ref([])
const prizes = ref([])
const loading = ref(true)

function getRaceClass(race) {
  if (!race) return ''
  const r = race.toLowerCase()
  if (r === 'terran' || r === 't') return 'race-tag terran'
  if (r === 'protoss' || r === 'p') return 'race-tag protoss'
  if (r === 'zerg' || r === 'z') return 'race-tag zerg'
  return ''
}

onMounted(async () => {
  try {
    const res = await getMatchDetail(route.params.id)
    const data = res.data || res
    match.value = data.match || data
    teams.value = data.teams || []
    stages.value = data.stages || []
    games.value = data.games || []
    prizes.value = data.prizes || []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.match-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 80px;
  padding-bottom: 60px;
  animation: fade-in 0.5s var(--ease-smooth) both;
}

.match-header {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 32px;
  position: relative;
  overflow: hidden;
}

.match-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.match-header-top {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}

.match-date {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.match-wr {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-deep);
  padding: 2px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(0, 212, 255, 0.25);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.match-title {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -1px;
  color: var(--text-primary);
}

.teams-section {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.team-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 28px 40px;
  text-align: center;
  min-width: 200px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.team-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.team-card:hover {
  border-color: var(--border-glow);
  box-shadow: var(--glow-accent);
}

.team-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  text-decoration: none;
  transition: color 0.25s var(--ease-smooth);
}

.team-name:hover { color: var(--accent); }

.team-score {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 800;
  color: var(--accent);
  margin-top: 8px;
}

.section-number-inline {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
  margin-right: 8px;
}

.stages-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stage-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 6px 14px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.stage-type {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 12px;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stage-winner {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-secondary);
}

.table-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.25s var(--ease-smooth);
}

.table-link:hover { color: var(--accent-dim); }

.vs-text {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.winner-text {
  color: var(--color-win);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 13px;
}

.prize-value {
  color: var(--color-prize);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 13px;
}

.section :deep(.el-table) {
  --el-table-border-color: var(--border-dim);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-tr-bg-color: var(--bg-card);
  --el-table-row-hover-bg-color: var(--bg-card-hover);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.section :deep(.el-table th.el-table__cell) {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  background: var(--bg-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.section :deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid var(--border-dim);
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  color: var(--text-muted);
}

.empty-state {
  text-align: center;
  color: var(--text-dim);
  padding: 60px 20px;
  font-family: var(--font-display);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
</style>
