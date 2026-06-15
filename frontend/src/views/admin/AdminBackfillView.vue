<template>
  <div class="backfill-page">
    <span class="section-number">02.</span>
    <h1 class="page-title">历史回补</h1>

    <!-- 启动回补 -->
    <div class="action-card">
      <div class="action-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <div class="action-info">
        <div class="action-title">启动新回补任务</div>
        <div class="action-desc">从指定日期开始批量导入历史数据</div>
      </div>
      <div class="backfill-form">
        <el-date-picker
          v-model="startDate"
          type="date"
          placeholder="起始日期"
          value-format="YYYY-MM-DD"
          size="default"
          style="width: 160px"
        />
        <el-button type="primary" :loading="startLoading" @click="handleStart">启动</el-button>
        <el-button @click="handleScan" :loading="scanLoading">仅扫描</el-button>
      </div>
    </div>

    <!-- 扫描结果 -->
    <div v-if="scanResult" class="section">
      <h3 class="section-title">扫描结果</h3>
      <div class="scan-info">
        <span>起始日期: {{ scanResult.start_date }}</span>
        <span>发现文章: <strong>{{ scanResult.total_found }}</strong> 篇</span>
      </div>
    </div>

    <!-- 回补任务列表 -->
    <section class="section" style="margin-top: 24px">
      <div class="section-header">
        <h2 class="section-title">回补任务</h2>
        <el-button size="small" @click="fetchJobs">刷新</el-button>
      </div>

      <div v-if="jobsLoading" class="loading-container">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      </div>
      <div v-else-if="jobs.length === 0" class="empty-state">暂无回补任务</div>
      <div v-else class="job-list">
        <div v-for="job in jobs" :key="job.job_id" class="job-card">
          <div class="job-header">
            <span class="job-id">JOB #{{ job.job_id }}</span>
            <span class="job-status" :class="getStatusClass(job.status)">{{ getStatusLabel(job.status) }}</span>
          </div>
          <div class="job-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getProgress(job) + '%' }"></div>
            </div>
            <span class="progress-text">{{ job.processed_count }}/{{ job.total_count }}</span>
          </div>
          <div class="job-meta">
            <span>起始: {{ job.start_date }}</span>
            <span>成功: {{ job.processed_count }}</span>
            <span>失败: {{ job.failed_count }}</span>
            <span>跳过: {{ job.skipped_count }}</span>
          </div>
          <div class="job-actions">
            <el-button
              v-if="job.status === 'running'"
              size="small"
              @click="handlePause(job.job_id)"
            >暂停</el-button>
            <el-button
              v-if="job.status === 'paused' || job.status === 'failed'"
              size="small"
              type="primary"
              @click="handleResume(job.job_id)"
            >恢复</el-button>
            <el-button
              size="small"
              @click="handleRefreshStatus(job.job_id)"
            >刷新状态</el-button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  startBackfill,
  resumeBackfill,
  pauseBackfill,
  getBackfillStatus,
  listBackfillJobs,
  scanBackfillHistory,
} from '../../api/adminBackfill'

const startDate = ref('2026-01-01')
const startLoading = ref(false)
const scanLoading = ref(false)
const scanResult = ref(null)

const jobs = ref([])
const jobsLoading = ref(true)

function getStatusClass(status) {
  const map = {
    pending: 'status-pending',
    running: 'status-running',
    paused: 'status-paused',
    completed: 'status-completed',
    failed: 'status-failed',
  }
  return map[status] || ''
}

function getStatusLabel(status) {
  const map = { pending: '等待中', running: '运行中', paused: '已暂停', completed: '已完成', failed: '已失败' }
  return map[status] || status
}

function getProgress(job) {
  if (!job.total_count) return 0
  return Math.round(((job.processed_count + job.failed_count + job.skipped_count) / job.total_count) * 100)
}

async function handleStart() {
  if (!startDate.value) {
    ElMessage.warning('请选择起始日期')
    return
  }
  startLoading.value = true
  try {
    await startBackfill(startDate.value)
    ElMessage.success('回补任务已启动')
    fetchJobs()
  } finally {
    startLoading.value = false
  }
}

async function handleScan() {
  if (!startDate.value) {
    ElMessage.warning('请选择起始日期')
    return
  }
  scanLoading.value = true
  try {
    const res = await scanBackfillHistory(startDate.value)
    scanResult.value = res.data || res
  } finally {
    scanLoading.value = false
  }
}

async function handlePause(jobId) {
  try {
    await pauseBackfill(jobId)
    ElMessage.success('任务已暂停')
    fetchJobs()
  } catch { /* handled */ }
}

async function handleResume(jobId) {
  try {
    await resumeBackfill(jobId)
    ElMessage.success('任务已恢复')
    fetchJobs()
  } catch { /* handled */ }
}

async function handleRefreshStatus(jobId) {
  try {
    const res = await getBackfillStatus(jobId)
    const data = res.data || res
    const idx = jobs.value.findIndex(j => j.job_id === jobId)
    if (idx >= 0) jobs.value[idx] = data
    ElMessage.success('状态已刷新')
  } catch { /* handled */ }
}

async function fetchJobs() {
  jobsLoading.value = true
  try {
    const res = await listBackfillJobs()
    jobs.value = res.data || res || []
  } finally {
    jobsLoading.value = false
  }
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.backfill-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.action-icon { color: var(--accent); flex-shrink: 0; }
.action-info { flex: 1; }

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

.backfill-form {
  display: flex;
  gap: 8px;
  align-items: center;
}

.scan-info {
  display: flex;
  gap: 24px;
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--text-secondary);
}

.scan-info strong {
  color: var(--accent);
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.job-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-dim);
  border-radius: var(--radius-md);
  padding: 20px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.job-id {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.job-status {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 2px 10px;
  border-radius: var(--radius-sm);
}

.status-pending { color: var(--text-muted); background: var(--bg-primary); }
.status-running { color: var(--accent); background: var(--accent-deep); border: 1px solid var(--accent); }
.status-paused { color: #ffd700; background: rgba(255, 215, 0, 0.1); border: 1px solid rgba(255, 215, 0, 0.25); }
.status-completed { color: var(--color-win); background: var(--color-win-bg); border: 1px solid rgba(0, 255, 136, 0.25); }
.status-failed { color: var(--color-lose); background: var(--color-lose-bg); border: 1px solid rgba(255, 68, 102, 0.25); }

.job-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: var(--bg-void);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-deep), var(--accent));
  border-radius: 2px;
  transition: width 0.5s var(--ease-smooth);
}

.progress-text {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}

.job-meta {
  display: flex;
  gap: 16px;
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--text-dim);
  margin-bottom: 12px;
}

.job-actions {
  display: flex;
  gap: 8px;
}
</style>
