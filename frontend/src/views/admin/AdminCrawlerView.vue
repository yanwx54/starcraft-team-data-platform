<template>
  <div class="crawler-page">
    <span class="section-number">01.</span>
    <h1 class="page-title">手动采集</h1>

    <!-- 快捷操作 -->
    <div class="action-grid">
      <div class="action-card">
        <div class="action-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
        </div>
        <div class="action-info">
          <div class="action-title">每日采集</div>
          <div class="action-desc">采集列表页最新文章并入库</div>
        </div>
        <el-button type="primary" :loading="crawlLoading" @click="handleRunCrawl">执行采集</el-button>
      </div>

      <div class="action-card">
        <div class="action-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </div>
        <div class="action-info">
          <div class="action-title">按 wr_id 采集</div>
          <div class="action-desc">采集指定文章编号</div>
        </div>
        <div class="wr-id-form">
          <el-input v-model="wrIdInput" placeholder="输入 wr_id" size="default" style="width: 120px" />
          <el-button type="primary" :loading="wrIdLoading" @click="handleRunCrawlByWrId">采集</el-button>
        </div>
      </div>
    </div>

    <!-- 采集日志 -->
    <section class="section" style="margin-top: 32px">
      <div class="section-header">
        <h2 class="section-title">采集日志</h2>
        <el-select v-model="logFilter" placeholder="日志级别" clearable size="small" style="width: 120px" @change="fetchLogs">
          <el-option label="INFO" value="info" />
          <el-option label="WARNING" value="warning" />
          <el-option label="ERROR" value="error" />
        </el-select>
      </div>

      <div v-if="logsLoading" class="loading-container">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      </div>
      <div v-else-if="logs.length === 0" class="empty-state">暂无日志</div>
      <div v-else class="log-list">
        <div v-for="log in logs" :key="log.id" class="log-item" :class="getLogLevelClass(log.log_level)">
          <span class="log-level">{{ log.log_level }}</span>
          <span class="log-wr-id" v-if="log.wr_id">wr_id: {{ log.wr_id }}</span>
          <span class="log-message">{{ log.message }}</span>
          <span class="log-time">{{ formatTime(log.created_at) }}</span>
        </div>
      </div>

      <div v-if="logsTotal > logsPageSize" class="pagination-wrap">
        <el-pagination
          v-model:current-page="logsPage"
          :page-size="logsPageSize"
          :total="logsTotal"
          layout="prev, pager, next"
          @current-change="fetchLogs"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { runCrawl, runCrawlByWrId, getCrawlLogs } from '../../api/adminCrawler'

const crawlLoading = ref(false)
const wrIdLoading = ref(false)
const wrIdInput = ref('')

const logs = ref([])
const logsLoading = ref(true)
const logsPage = ref(1)
const logsPageSize = 20
const logsTotal = ref(0)
const logFilter = ref('')

function getLogLevelClass(level) {
  if (!level) return ''
  const l = level.toLowerCase()
  if (l === 'error') return 'log-error'
  if (l === 'warning') return 'log-warning'
  return 'log-info'
}

function formatTime(iso) {
  if (!iso) return ''
  return iso.replace('T', ' ').slice(0, 19)
}

async function handleRunCrawl() {
  crawlLoading.value = true
  try {
    await runCrawl()
    ElMessage.success('采集任务已启动')
    fetchLogs()
  } finally {
    crawlLoading.value = false
  }
}

async function handleRunCrawlByWrId() {
  const wrId = parseInt(wrIdInput.value)
  if (!wrId || wrId <= 0) {
    ElMessage.warning('请输入有效的 wr_id')
    return
  }
  wrIdLoading.value = true
  try {
    await runCrawlByWrId(wrId)
    ElMessage.success(`采集任务已启动: wr_id=${wrId}`)
    fetchLogs()
  } finally {
    wrIdLoading.value = false
  }
}

async function fetchLogs() {
  logsLoading.value = true
  try {
    const params = { page: logsPage.value, page_size: logsPageSize }
    if (logFilter.value) params.log_level = logFilter.value
    const res = await getCrawlLogs(params)
    const data = res.data || res
    logs.value = data.items || []
    logsTotal.value = data.total || 0
  } finally {
    logsLoading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.crawler-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.action-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s var(--ease-smooth);
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.5;
}

.action-card:hover {
  border-color: var(--border-glow);
  box-shadow: var(--glow-accent);
}

.action-icon {
  color: var(--accent);
  flex-shrink: 0;
}

.action-info {
  flex: 1;
}

.action-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.action-desc {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.wr-id-form {
  display: flex;
  gap: 8px;
  align-items: center;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 13px;
  transition: background 0.2s;
}

.log-item:hover {
  background: var(--bg-card-hover);
}

.log-level {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  min-width: 56px;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  text-align: center;
}

.log-info .log-level {
  color: var(--accent);
  background: var(--accent-deep);
}

.log-warning .log-level {
  color: #ffd700;
  background: rgba(255, 215, 0, 0.1);
}

.log-error .log-level {
  color: var(--color-lose);
  background: var(--color-lose-bg);
}

.log-wr-id {
  color: var(--text-muted);
  font-size: 12px;
  min-width: 80px;
}

.log-message {
  flex: 1;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-time {
  color: var(--text-dim);
  font-size: 11px;
  white-space: nowrap;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}
</style>
