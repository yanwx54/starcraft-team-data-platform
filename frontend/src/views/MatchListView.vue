<template>
  <div class="match-list-page">
    <span class="section-number">01.</span>
    <h1 class="page-title">比赛列表</h1>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="—"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        :clearable="true"
        @change="fetchMatches"
      />
      <el-select v-model="filters.season_id" placeholder="选择赛季" clearable @change="fetchMatches">
        <el-option v-for="s in seasonOptions" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
    </div>

    <!-- 比赛列表 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
    </div>
    <div v-else-if="matches.length === 0" class="empty-state">暂无比赛数据</div>
    <div v-else class="matches">
      <router-link
        v-for="match in matches"
        :key="match.id"
        :to="`/matches/${match.id}`"
        class="match-card"
      >
        <div class="match-card-top">
          <span class="match-card-date">{{ match.match_date }}</span>
          <span v-if="match.wr_id" class="match-card-wr">#{{ match.wr_id }}</span>
        </div>
        <div class="match-card-title">{{ match.title }}</div>
        <div class="match-card-bottom">
          <span class="match-card-link">查看详情 →</span>
        </div>
      </router-link>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchMatches"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { getMatches } from '../api/matches'

const matches = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)
const dateRange = ref(null)
const seasonOptions = ref([])

const filters = ref({
  season_id: null,
})

async function fetchMatches() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (filters.value.season_id) params.season_id = filters.value.season_id
    if (dateRange.value && dateRange.value[0]) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    const res = await getMatches(params)
    const data = res.data || res
    matches.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMatches()
})
</script>

<style scoped>
.match-list-page {
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
}

.matches {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.match-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  text-decoration: none;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.match-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.match-card:hover {
  border-color: var(--border-glow);
  box-shadow: var(--glow-accent);
}

.match-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.match-card-date {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.match-card-wr {
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

.match-card-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.match-card-bottom {
  display: flex;
  justify-content: flex-end;
}

.match-card-link {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  transition: all 0.25s var(--ease-smooth);
}

.match-card:hover .match-card-link {
  transform: translateX(4px);
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 60px 0;
  color: var(--text-muted);
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--text-dim);
  font-family: var(--font-display);
  font-size: 14px;
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
