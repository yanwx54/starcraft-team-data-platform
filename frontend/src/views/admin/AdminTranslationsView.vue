<template>
  <div class="translations-page">
    <span class="section-number">04.</span>
    <h1 class="page-title">翻译规则管理</h1>

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select v-model="filters.rule_type" placeholder="规则类型" clearable @change="fetchRules">
          <el-option label="选手" value="player" />
          <el-option label="地图" value="map" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索原文/译文..."
          clearable
          style="width: 220px"
          @keyup.enter="fetchRules"
          @clear="fetchRules"
        />
        <el-button @click="fetchRules">搜索</el-button>
      </div>
      <el-button type="primary" @click="showAddDialog">新增规则</el-button>
    </div>

    <!-- 表格 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
    </div>
    <div v-else>
      <el-table :data="rules" class="admin-table" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="rule_type" label="类型" width="90">
          <template #default="{ row }">
            <span class="type-badge" :class="row.rule_type === 'player' ? 'type-player' : 'type-map'">
              {{ row.rule_type === 'player' ? '选手' : '地图' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="source_text" label="原文" min-width="160" />
        <el-table-column prop="translated_text" label="译文" min-width="160" />
        <el-table-column prop="alias_group" label="别名组" width="140">
          <template #default="{ row }">
            <span v-if="row.alias_group" class="alias-badge">{{ row.alias_group }}</span>
            <span v-else class="text-dim">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="showEditDialog(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > pageSize" class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="fetchRules"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑翻译规则' : '新增翻译规则'" width="500px">
      <el-form :model="form" label-width="80px" label-position="top">
        <el-form-item label="规则类型">
          <el-select v-model="form.rule_type" placeholder="选择类型">
            <el-option label="选手" value="player" />
            <el-option label="地图" value="map" />
          </el-select>
        </el-form-item>
        <el-form-item label="原文">
          <el-input v-model="form.source_text" placeholder="韩文原文" />
        </el-form-item>
        <el-form-item label="译文">
          <el-input v-model="form.translated_text" placeholder="中文翻译" />
        </el-form-item>
        <el-form-item label="别名组">
          <el-input v-model="form.alias_group" placeholder="别名组（可选）" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="form.priority" :min="1" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTranslations, createTranslation, updateTranslation, deleteTranslation } from '../../api/adminTranslations'

const rules = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)

const filters = ref({
  rule_type: '',
  keyword: '',
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const submitLoading = ref(false)

const form = ref({
  rule_type: 'player',
  source_text: '',
  translated_text: '',
  alias_group: '',
  priority: 1,
})

function resetForm() {
  form.value = {
    rule_type: 'player',
    source_text: '',
    translated_text: '',
    alias_group: '',
    priority: 1,
  }
}

function showAddDialog() {
  resetForm()
  isEdit.value = false
  editId.value = null
  dialogVisible.value = true
}

function showEditDialog(row) {
  form.value = {
    rule_type: row.rule_type,
    source_text: row.source_text,
    translated_text: row.translated_text,
    alias_group: row.alias_group || '',
    priority: row.priority,
  }
  isEdit.value = true
  editId.value = row.id
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.source_text || !form.value.translated_text) {
    ElMessage.warning('请填写原文和译文')
    return
  }
  submitLoading.value = true
  try {
    const data = {
      rule_type: form.value.rule_type,
      source_text: form.value.source_text,
      translated_text: form.value.translated_text,
      alias_group: form.value.alias_group || null,
      priority: form.value.priority,
    }
    if (isEdit.value) {
      await updateTranslation(editId.value, data)
      ElMessage.success('修改成功')
    } else {
      await createTranslation(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchRules()
  } catch {
    // handled by interceptor
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(ruleId) {
  try {
    await ElMessageBox.confirm('确定删除该翻译规则？', '确认', { type: 'warning' })
    await deleteTranslation(ruleId)
    ElMessage.success('已删除')
    fetchRules()
  } catch {
    // cancelled or error
  }
}

async function fetchRules() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filters.value.rule_type) params.rule_type = filters.value.rule_type
    if (filters.value.keyword) params.keyword = filters.value.keyword
    const res = await getTranslations(params)
    const data = res.data || res
    rules.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRules()
})
</script>

<style scoped>
.translations-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.type-badge {
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.type-badge.type-player {
  color: var(--accent);
  background: var(--accent-deep);
  border: 1px solid rgba(0, 212, 255, 0.25);
}

.type-badge.type-map {
  color: var(--color-win);
  background: var(--color-win-bg);
  border: 1px solid rgba(0, 255, 136, 0.25);
}

.alias-badge {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-secondary);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.text-dim {
  color: var(--text-dim);
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}
</style>
