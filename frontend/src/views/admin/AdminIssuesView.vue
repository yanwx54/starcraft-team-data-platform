<template>
  <div class="issues-page">
    <span class="section-number">03.</span>
    <h1 class="page-title">异常中心</h1>

    <!-- 筛选 -->
    <div class="filter-bar">
      <el-select v-model="filters.issue_type" placeholder="异常类型" clearable @change="fetchIssues">
        <el-option label="翻译错误" value="translation_error" />
        <el-option label="选手未找到" value="player_not_found" />
        <el-option label="地图未找到" value="map_not_found" />
        <el-option label="比分冲突" value="score_conflict" />
        <el-option label="奖金异常" value="prize_error" />
        <el-option label="采集错误" value="crawl_error" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="fetchIssues">
        <el-option label="未解决" value="open" />
        <el-option label="已解决" value="resolved" />
      </el-select>
    </div>

    <!-- 统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">未解决</div>
        <div class="stat-value">{{ openCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已解决</div>
        <div class="stat-value">{{ resolvedCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总计</div>
        <div class="stat-value">{{ total }}</div>
      </div>
    </div>

    <!-- 列表 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
    </div>
    <div v-else-if="issues.length === 0" class="empty-state">暂无异常记录</div>
    <div v-else class="issue-list">
      <div v-for="issue in issues" :key="issue.id" class="issue-card" :class="{ 'issue-resolved': issue.status === 'resolved' }">
        <div class="issue-header">
          <span class="issue-type-badge" :class="getTypeClass(issue.issue_type)">{{ getTypeLabel(issue.issue_type) }}</span>
          <span class="issue-status" :class="issue.status === 'resolved' ? 'status-resolved' : 'status-open'">
            {{ issue.status === 'resolved' ? '已解决' : '未解决' }}
          </span>
        </div>
        <div class="issue-body">
          <div class="issue-desc">{{ issue.description }}</div>
          <div class="issue-meta">
            <span v-if="issue.source_table">来源: {{ issue.source_table }}</span>
            <span v-if="issue.source_id">ID: {{ issue.source_id }}</span>
            <span>{{ formatTime(issue.created_at) }}</span>
          </div>
        </div>
        <div class="issue-actions">
          <el-button
            v-if="issue.status === 'open'"
            size="small"
            type="primary"
            @click="handleResolve(issue.id)"
          >标记已解决</el-button>
          <el-button
            v-if="issue.status === 'resolved'"
            size="small"
            @click="handleReopen(issue.id)"
          >重新打开</el-button>
        </div>
      </div>
    </div>

    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchIssues"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getIssues, resolveIssue, reopenIssue } from '../../api/adminIssues'

const issues = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)
const openCount = ref(0)
const resolvedCount = ref(0)

const filters = ref({
  issue_type: '',
  status: '',
})

function getTypeClass(type) {
  const map = {
    translation_error: 'type-translation',
    player_not_found: 'type-player',
    map_not_found: 'type-map',
    score_conflict: 'type-score',
    prize_error: 'type-prize',
    crawl_error: 'type-crawl',
  }
  return map[type] || ''
}

function getTypeLabel(type) {
  const map = {
    translation_error: '翻译错误',
    player_not_found: '选手未找到',
    map_not_found: '地图未找到',
    score_conflict: '比分冲突',
    prize_error: '奖金异常',
    crawl_error: '采集错误',
  }
  return map[type] || type
}

function formatTime(iso) {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(0, 19)
}

async function fetchIssues() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.issue_type) params.issue_type = filters.value.issue_type
    if (filters.value.status) params.status = filters.value.status
    const res = await getIssues(params)
    const data = res.data || res
    issues.value = data.items || []
    total.value = data.total || 0

    // 统计
    openCount.value = issues.value.filter(i => i.status === 'open').length
    resolvedCount.value = issues.value.filter(i => i.status === 'resolved').length
  } finally {
    loading.value = false
  }
}

async function handleResolve(issueId) {
  try {
    await resolveIssue(issueId)
    ElMessage.success('已标记为已解决')
    fetchIssues()
  } catch { /* handled */ }
}

async function handleReopen(issueId) {
  try {
    await reopenIssue(issueId)
    ElMessage.success('已重新打开')
    fetchIssues()
  } catch { /* handled */ }
}

onMounted(() => {
  fetchIssues()
})
</script>

<style scoped>
.issues-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.issue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.issue-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
  transition: all 0.25s var(--ease-smooth);
}

.issue-card:hover {
  border-color: var(--border-glow);
}

.issue-card.issue-resolved {
  opacity: 0.6;
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.issue-type-badge {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 2px 10px;
  border-radius: var(--radius-sm);
}

.type-translation { color: #c084fc; background: rgba(192, 132, 252, 0.1); border: 1px solid rgba(192, 132, 252, 0.25); }
.type-player { color: var(--accent); background: var(--accent-deep); border: 1px solid rgba(0, 212, 255, 0.25); }
.type-map { color: var(--color-win); background: var(--color-win-bg); border: 1px solid rgba(0, 255, 136, 0.25); }
.type-score { color: #ffd700; background: rgba(255, 215, 0, 0.1); border: 1px solid rgba(255, 215, 0, 0.25); }
.type-prize { color: var(--color-prize); background: var(--color-prize-bg); border: 1px solid rgba(255, 215, 0, 0.25); }
.type-crawl { color: var(--color-lose); background: var(--color-lose-bg); border: 1px solid rgba(255, 68, 102, 0.25); }

.issue-status {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 2px 10px;
  border-radius: var(--radius-sm);
}

.status-open { color: var(--color-lose); background: var(--color-lose-bg); }
.status-resolved { color: var(--color-win); background: var(--color-win-bg); }

.issue-desc {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 8px;
}

.issue-meta {
  display: flex;
  gap: 16px;
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.issue-actions {
  margin-top: 12px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}
</style>
