<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { Application, Issue } from '@/types'
import { deleteIssue, getIssues } from '@/api/issues'
import { getApplications } from '@/api/applications'
import { ISSUE_CATEGORIES, ISSUE_MASTERY, MASTERY_COLOR } from '@/constants/enums'
import EmptyState from '@/components/EmptyState.vue'
import IssueFormDrawer from '@/components/IssueFormDrawer.vue'

/** 问题记录（PG-007）：CRUD + 行展开 + 掌握程度就地切换 + 关联投递跳转 */
const router = useRouter()

const items = ref<Issue[]>([])
const appMap = ref<Record<number, Application>>({})
const loading = ref(false)
const expandedId = ref<number | null>(null)

const filters = reactive({ category: '', keyword: '' })

let searchTimer: ReturnType<typeof setTimeout> | null = null

async function load() {
  loading.value = true
  try {
    items.value = await getIssues({
      category: filters.category || undefined,
    })
    // 关键词前端过滤（问题量小，够用）
    const kw = filters.keyword.trim().toLowerCase()
    if (kw) {
      items.value = items.value.filter(
        (i) =>
          i.title.toLowerCase().includes(kw) ||
          (i.description || '').toLowerCase().includes(kw) ||
          (i.solution || '').toLowerCase().includes(kw) ||
          (i.tags || '').toLowerCase().includes(kw),
      )
    }
  } finally {
    loading.value = false
  }
}

async function loadApps() {
  try {
    const apps = await getApplications({ limit: 200 })
    appMap.value = Object.fromEntries(apps.items.map((a) => [a.id, a]))
  } catch {
    appMap.value = {}
  }
}

watch(
  () => [filters.category, filters.keyword],
  () => {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(load, 250)
  },
)

onMounted(() => {
  load()
  loadApps()
})

const masteryMap = computed<Record<number, string>>(() => {
  // 掌握程度存储于 tags 约定（已掌握/待复习/仍不会），若无则默认待复习
  const m: Record<number, string> = {}
  for (const i of items.value) {
    const tag = (i.tags || '')
      .split(/[,，]/)
      .map((s) => s.trim())
      .find((s) => ISSUE_MASTERY.includes(s))
    m[i.id] = tag || '待复习'
  }
  return m
})

function toggleExpand(i: Issue) {
  expandedId.value = expandedId.value === i.id ? null : i.id
}

function masteryLabel(i: Issue) {
  return masteryMap.value[i.id]
}

function relatedAppName(i: Issue): string {
  if (!i.related_application_id) return '—'
  const a = appMap.value[i.related_application_id]
  return a ? `${a.company_name} · ${a.position}` : `#${i.related_application_id}`
}

function goApp(i: Issue) {
  if (i.related_application_id) router.push(`/applications/${i.related_application_id}`)
}

/* 表单 */
const formVisible = ref(false)
const editing = ref<Issue | null>(null)

function openCreate() {
  editing.value = null
  formVisible.value = true
}

function openEdit(i: Issue) {
  editing.value = i
  formVisible.value = true
}

async function removeIssue(i: Issue) {
  await deleteIssue(i.id)
  ElMessage.success('问题已删除')
  load()
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>问题记录</h1>
      <div class="spacer" />
      <el-input
        v-model="filters.keyword"
        placeholder="搜索标题 / 描述 / 答案 / 标签"
        clearable
        style="width: 260px"
        :prefix-icon="'Search'"
      />
      <el-select v-model="filters.category" clearable placeholder="分类" style="width: 120px">
        <el-option v-for="c in ISSUE_CATEGORIES" :key="c" :label="c" :value="c" />
      </el-select>
      <el-button type="primary" @click="openCreate">+ 新增问题</el-button>
    </div>

    <div class="app-card" style="padding: 0; overflow: hidden">
      <el-table
        :data="items"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ background: 'var(--color-gray-50)', color: 'var(--color-gray-700)' }"
        @row-click="toggleExpand"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-box">
              <div class="expand-section">
                <div class="expand-label">问题描述</div>
                <div class="expand-text">{{ row.description || '—' }}</div>
              </div>
              <div class="expand-section">
                <div class="expand-label">解决方案 / 正确答案</div>
                <div class="expand-text">{{ row.solution || '—' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="90" />
        <el-table-column label="掌握程度" width="110">
          <template #default="{ row }">
            <span class="mastery" @click.stop>
              <span class="m-dot" :style="{ background: MASTERY_COLOR[masteryLabel(row)] }" />
              {{ masteryLabel(row) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="标签" width="160">
          <template #default="{ row }">
            <template v-if="row.tags">
              <el-tag
                v-for="t in (row.tags || '').split(/[,，]/).filter(Boolean).slice(0, 2)"
                :key="t"
                size="small"
                effect="plain"
                style="margin-right: 4px"
              >{{ t.trim() }}</el-tag>
            </template>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="关联投递" width="170" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="app-link" @click.stop="goApp(row)">{{ relatedAppName(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="日期" width="110">
          <template #default="{ row }"><span class="num">{{ row.recorded_date || '—' }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确认删除该问题？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removeIssue(row)">
              <template #reference>
                <el-button link type="danger" size="small" @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
        <template #empty>
          <EmptyState
            title="还没有问题记录"
            description="面试后记下被问到的题，考前可快速复习"
            icon="Warning"
          >
            <el-button type="primary" @click="openCreate">+ 新增问题</el-button>
          </EmptyState>
        </template>
      </el-table>
    </div>

    <IssueFormDrawer v-model:visible="formVisible" :editing="editing" @saved="load" />
  </div>
</template>

<style scoped>
.page-header .spacer {
  flex: 1;
}

.mastery {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--fs-body);
  color: var(--color-gray-700);
}

.m-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.app-link {
  cursor: pointer;
  color: var(--color-gray-700);
}

.app-link:hover {
  color: var(--color-primary-600);
  text-decoration: underline;
}

.expand-box {
  padding: 4px 24px 16px 56px;
  display: flex;
  gap: var(--sp-8);
}

.expand-section {
  flex: 1;
  max-height: 320px;
  overflow-y: auto;
}

.expand-label {
  font-size: var(--fs-sm);
  font-weight: 500;
  color: var(--color-gray-500);
  margin-bottom: 6px;
}

.expand-text {
  font-size: var(--fs-body);
  color: var(--color-gray-700);
  line-height: 22px;
  white-space: pre-wrap;
}
</style>
