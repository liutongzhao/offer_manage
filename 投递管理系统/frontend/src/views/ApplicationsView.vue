<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { Application, CompanyWithCount } from '@/types'
import {
  deleteApplication,
  exportUrl,
  getApplications,
  updateApplication,
} from '@/api/applications'
import { getTags } from '@/api/tags'
import { CHANNELS, STATUS_LIST, TYPE_LIST } from '@/constants/enums'
import StatusTag from '@/components/StatusTag.vue'
import TypeTag from '@/components/TypeTag.vue'
import EmptyState from '@/components/EmptyState.vue'
import KanbanBoard from '@/components/KanbanBoard.vue'
import ApplicationFormDrawer from '@/components/ApplicationFormDrawer.vue'
import CompanyDetailDrawer from '@/components/CompanyDetailDrawer.vue'
import { deadlineUrgency } from '@/utils/format'

/** 投递记录（PG-002 核心页）：多条件筛选 + 列表/看板双视图 + 行内改状态 + 导出导入 */
const route = useRoute()
const router = useRouter()

const items = ref<Application[]>([])
const total = ref(0)
const loading = ref(false)
const view = ref<'list' | 'kanban'>('list')

const filters = reactive({
  type: '',
  status: (route.query.status as string) || '',
  channel: '',
  city: '',
  company_id: (route.query.company_id as string) || '',
  keyword: '',
  tag: '',
  sort_by: 'id',
  order: 'desc',
  page: 1,
  pageSize: 20,
})

const tagOptions = ref<string[]>([])
const cityOptions = ref<string[]>([])

let searchTimer: ReturnType<typeof setTimeout> | null = null

async function load() {
  loading.value = true
  try {
    const data = await getApplications({
      type: filters.type || undefined,
      status: filters.status || undefined,
      channel: filters.channel || undefined,
      city: filters.city || undefined,
      company_id: filters.company_id ? Number(filters.company_id) : undefined,
      keyword: filters.keyword || undefined,
      tag: filters.tag || undefined,
      sort_by: filters.sort_by,
      order: filters.order,
      skip: (filters.page - 1) * filters.pageSize,
      limit: filters.pageSize,
    })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  try {
    tagOptions.value = (await getTags()).map((t) => t.name)
  } catch {
    tagOptions.value = []
  }
}

watch(
  () => [filters.type, filters.status, filters.channel, filters.city, filters.company_id, filters.tag],
  () => {
    filters.page = 1
    load()
  },
)

watch(
  () => filters.keyword,
  () => {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      filters.page = 1
      load()
    }, 300)
  },
)

watch(
  () => route.query,
  (q) => {
    if (q.status !== undefined) filters.status = (q.status as string) || ''
    if (q.company_id !== undefined) filters.company_id = (q.company_id as string) || ''
    load()
  },
)

onMounted(() => {
  load()
  loadOptions()
})

const hasFilters = computed(
  () => !!(filters.type || filters.status || filters.channel || filters.city || filters.company_id || filters.keyword || filters.tag),
)

const activeChips = computed(() => {
  const chips: { label: string; clear: () => void }[] = []
  if (filters.type) chips.push({ label: `类型：${filters.type}`, clear: () => (filters.type = '') })
  if (filters.status) chips.push({ label: `状态：${filters.status}`, clear: () => (filters.status = '') })
  if (filters.channel) chips.push({ label: `渠道：${filters.channel}`, clear: () => (filters.channel = '') })
  if (filters.city) chips.push({ label: `城市：${filters.city}`, clear: () => (filters.city = '') })
  if (filters.tag) chips.push({ label: `标签：${filters.tag}`, clear: () => (filters.tag = '') })
  if (filters.company_id) chips.push({ label: `公司ID：${filters.company_id}`, clear: () => (filters.company_id = '') })
  if (filters.keyword) chips.push({ label: `关键词：${filters.keyword}`, clear: () => (filters.keyword = '') })
  return chips
})

function clearFilters() {
  filters.type = ''
  filters.status = ''
  filters.channel = ''
  filters.city = ''
  filters.company_id = ''
  filters.keyword = ''
  filters.tag = ''
}

function sortBy(col: string) {
  if (filters.sort_by === col) {
    filters.order = filters.order === 'desc' ? 'asc' : 'desc'
  } else {
    filters.sort_by = col
    filters.order = 'desc'
  }
  load()
}

/* 新增/编辑 */
const formVisible = ref(false)
const editing = ref<Application | null>(null)

function openCreate() {
  editing.value = null
  formVisible.value = true
}

function openEdit(app: Application) {
  editing.value = app
  formVisible.value = true
}

function onSaved() {
  load()
}

/* 行内改状态 */
async function changeStatus(app: Application, status: string) {
  if (app.status === status) return
  try {
    await updateApplication(app.id, { status })
    ElMessage.success(`已更新为：${status}`)
    load()
  } catch {
    /* 回滚由重载完成 */
  }
}

function openDetail(app: Application) {
  router.push(`/applications/${app.id}`)
}

async function removeApp(app: Application) {
  await deleteApplication(app.id)
  ElMessage.success(`已删除：${app.company_name} · ${app.position}（可在设置页恢复）`)
  load()
}

/* 公司详情抽屉 */
const companyDrawerVisible = ref(false)
const companyDrawer = ref<CompanyWithCount | null>(null)

function openCompany(app: Application) {
  companyDrawer.value = {
    id: app.company_id,
    name: app.company_name || '',
    alias: null,
    city: null,
    industry: null,
    scale: null,
    website: null,
    notes: null,
    created_at: null,
    application_count: 0,
  }
  companyDrawerVisible.value = true
}

function deadlineClass(deadline: string | null): string {
  const u = deadlineUrgency(deadline)
  return u === 'overdue' ? 'dl-overdue' : u === 'soon' ? 'dl-soon' : ''
}

/* 看板拖拽 */
async function onKanbanChange(appId: number, status: string) {
  try {
    await updateApplication(appId, { status })
    ElMessage.success(`已更新为：${status}`)
  } finally {
    load()
  }
}

/* 导出 */
function doExport() {
  const url = exportUrl({
    type: filters.type || undefined,
    status: filters.status || undefined,
    channel: filters.channel || undefined,
    city: filters.city || undefined,
    company_id: filters.company_id ? Number(filters.company_id) : undefined,
    keyword: filters.keyword || undefined,
    tag: filters.tag || undefined,
  })
  window.open(url, '_blank')
  ElMessage.success('已开始下载 CSV')
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>投递记录</h1>
      <div class="spacer" />
      <el-button @click="doExport">导出 CSV</el-button>
      <el-button type="primary" @click="openCreate">+ 新增投递</el-button>
    </div>

    <!-- 工具条 -->
    <div class="toolbar">
      <el-input
        v-model="filters.keyword"
        placeholder="搜索公司 / 岗位 / 备注 / 招聘要求"
        clearable
        style="width: 280px"
        :prefix-icon="'Search'"
      />
      <el-select v-model="filters.type" clearable placeholder="类型" style="width: 120px">
        <el-option v-for="t in TYPE_LIST" :key="t.value" :label="t.value" :value="t.value" />
      </el-select>
      <el-select v-model="filters.status" clearable placeholder="状态" style="width: 120px">
        <el-option v-for="s in STATUS_LIST" :key="s.value" :label="s.value" :value="s.value" />
      </el-select>
      <el-select v-model="filters.channel" clearable placeholder="渠道" style="width: 120px">
        <el-option v-for="c in CHANNELS" :key="c" :label="c" :value="c" />
      </el-select>
      <el-select v-model="filters.city" clearable filterable allow-create placeholder="城市" style="width: 110px">
        <el-option v-for="c in cityOptions" :key="c" :label="c" :value="c" />
      </el-select>
      <el-select v-model="filters.tag" clearable filterable placeholder="标签" style="width: 120px">
        <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
      </el-select>
      <div class="spacer" />
      <el-radio-group v-model="view" size="small">
        <el-radio-button value="list">列表</el-radio-button>
        <el-radio-button value="kanban">看板</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 筛选条 -->
    <div v-if="hasFilters" class="filter-chips">
      <el-tag
        v-for="(chip, i) in activeChips"
        :key="i"
        closable
        type="info"
        effect="plain"
        @close="chip.clear()"
      >{{ chip.label }}</el-tag>
      <el-button v-if="activeChips.length >= 2" link type="primary" size="small" @click="clearFilters">清空筛选</el-button>
    </div>

    <!-- 看板视图 -->
    <KanbanBoard
      v-if="view === 'kanban'"
      :items="items"
      @change-status="onKanbanChange"
      @open="openDetail"
    />

    <!-- 列表视图 -->
    <div v-else class="table-card app-card">
      <el-table
        :data="items"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ background: 'var(--color-gray-50)', color: 'var(--color-gray-700)' }"
        @row-click="openDetail"
      >
        <el-table-column label="公司" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="company-link" @click.stop="openCompany(row)">{{ row.company_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="岗位" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="position-text">{{ row.position }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" sortable :sort-method="undefined">
          <template #header>
            <span class="sortable" @click.stop="sortBy('status')">状态</span>
          </template>
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(s: string) => changeStatus(row, s)">
              <StatusTag :status="row.status" size="S" @click.stop />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="s in STATUS_LIST" :key="s.value" :command="s.value">
                    <span class="menu-dot" :style="{ background: s.dot }" />{{ s.value }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }"><TypeTag :type="row.type" /></template>
        </el-table-column>
        <el-table-column prop="city" label="城市" width="90" show-overflow-tooltip />
        <el-table-column prop="channel" label="渠道" width="90" />
        <el-table-column label="投递日期" width="120" align="right">
          <template #header>
            <span class="sortable" @click.stop="sortBy('apply_date')">投递日期</span>
          </template>
          <template #default="{ row }">
            <span class="num">{{ row.apply_date || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="截止日期" width="120" align="right">
          <template #header>
            <span class="sortable" @click.stop="sortBy('deadline')">截止日期</span>
          </template>
          <template #default="{ row }">
            <span class="num" :class="deadlineClass(row.deadline)">{{ row.deadline || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="110">
          <template #default="{ row }">
            <el-tag v-for="t in row.tag_names.slice(0, 2)" :key="t" size="small" effect="plain" style="margin-right: 4px">{{ t }}</el-tag>
            <span v-if="row.tag_names.length > 2" class="more-tags">+{{ row.tag_names.length - 2 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="openDetail(row)">详情</el-button>
            <el-button link size="small" @click.stop="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确认删除这条投递？（可在设置页恢复）" confirm-button-text="删除" cancel-button-text="取消" @confirm="removeApp(row)">
              <template #reference>
                <el-button link type="danger" size="small" @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
        <template #empty>
          <EmptyState
            :title="hasFilters ? '没有符合条件的记录' : '还没有投递记录'"
            :description="hasFilters ? '试试减少筛选条件，或清空后重新筛选' : '创建第一条投递，开始追踪你的秋招进度'"
          >
            <el-button v-if="hasFilters" @click="clearFilters">清空筛选</el-button>
            <el-button v-else type="primary" @click="openCreate">+ 新增投递</el-button>
          </EmptyState>
        </template>
      </el-table>

      <div class="pagination-row">
        <span class="total-text">共 {{ total }} 条</span>
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="sizes, prev, pager, next"
          @current-change="load"
          @size-change="load"
        />
      </div>
    </div>

    <ApplicationFormDrawer v-model:visible="formVisible" :editing="editing" @saved="onSaved" />
    <CompanyDetailDrawer v-model:visible="companyDrawerVisible" :company="companyDrawer" />
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  height: 48px;
  flex-wrap: wrap;
}

.toolbar .spacer,
.page-header .spacer {
  flex: 1;
}

.filter-chips {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  min-height: 40px;
  flex-wrap: wrap;
}

.table-card {
  padding: 0;
  overflow: hidden;
}

.company-link {
  color: var(--color-gray-900);
  font-weight: 500;
  cursor: pointer;
}

.company-link:hover {
  color: var(--color-primary-600);
  text-decoration: underline;
}

.position-text {
  font-weight: 500;
  color: var(--color-gray-900);
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  color: var(--color-primary-600);
}

.menu-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.dl-soon {
  color: var(--color-warning-text);
  font-weight: 500;
}

.dl-overdue {
  color: var(--color-error-text);
  font-weight: 500;
}

.more-tags {
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
}

.pagination-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--sp-4);
  padding: var(--sp-3) var(--sp-4);
}

.total-text {
  font-size: var(--fs-sm);
  color: var(--color-gray-500);
}
</style>
