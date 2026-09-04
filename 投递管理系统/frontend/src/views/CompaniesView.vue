<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { CompanyWithCount } from '@/types'
import { deleteCompany, getCompanies } from '@/api/companies'
import EmptyState from '@/components/EmptyState.vue'
import CompanyFormDialog from '@/components/CompanyFormDialog.vue'
import CompanyDetailDrawer from '@/components/CompanyDetailDrawer.vue'

/** 公司管理（PG-005）：CRUD + 每家公司投递数聚合 */
const router = useRouter()

const items = ref<CompanyWithCount[]>([])
const loading = ref(false)
const keyword = ref('')

let searchTimer: ReturnType<typeof setTimeout> | null = null

async function load() {
  loading.value = true
  try {
    const list = await getCompanies({ keyword: keyword.value || undefined, with_count: true })
    items.value = list as CompanyWithCount[]
  } finally {
    loading.value = false
  }
}

watch(keyword, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(load, 300)
})

onMounted(load)

/* 表单 */
const formVisible = ref(false)
const editing = ref<CompanyWithCount | null>(null)

function openCreate() {
  editing.value = null
  formVisible.value = true
}

function openEdit(c: CompanyWithCount) {
  editing.value = c
  formVisible.value = true
}

function onSaved() {
  load()
}

/* 详情抽屉 */
const drawerVisible = ref(false)
const drawerCompany = ref<CompanyWithCount | null>(null)

function openDetail(c: CompanyWithCount) {
  drawerCompany.value = c
  drawerVisible.value = true
}

function goApplications(c: CompanyWithCount) {
  router.push({ path: '/applications', query: { company_id: String(c.id) } })
}

async function removeCompany(c: CompanyWithCount) {
  if (c.application_count > 0) {
    ElMessage.warning(`该公司下还有 ${c.application_count} 条投递记录，请先处理相关投递`)
    return
  }
  await deleteCompany(c.id)
  ElMessage.success(`已删除公司：${c.name}`)
  load()
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>公司管理</h1>
      <div class="spacer" />
      <el-input
        v-model="keyword"
        placeholder="搜索公司名 / 别名"
        clearable
        style="width: 260px"
        :prefix-icon="'Search'"
      />
      <el-button type="primary" @click="openCreate">+ 新增公司</el-button>
    </div>

    <div class="app-card" style="padding: 0; overflow: hidden">
      <el-table
        :data="items"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ background: 'var(--color-gray-50)', color: 'var(--color-gray-700)' }"
      >
        <el-table-column label="公司名称" min-width="160">
          <template #default="{ row }">
            <span class="company-name" @click="openDetail(row)">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="alias" label="别名/英文" width="140" show-overflow-tooltip />
        <el-table-column prop="city" label="城市" width="90" />
        <el-table-column prop="industry" label="行业" width="110" show-overflow-tooltip />
        <el-table-column prop="scale" label="规模" width="80" />
        <el-table-column label="投递数" width="90" align="right">
          <template #default="{ row }">
            <span class="count-link num" @click="goApplications(row)">{{ row.application_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDetail(row)">查看</el-button>
            <el-button link size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm
              :title="row.application_count > 0
                ? `该公司下还有 ${row.application_count} 条投递记录，删除后这些记录将失去归属，确认删除？`
                : '确认删除该公司？'"
              confirm-button-text="删除"
              cancel-button-text="取消"
              width="260"
              @confirm="removeCompany(row)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
        <template #empty>
          <EmptyState
            title="还没有公司记录"
            description="新增公司，或在新增投递时自动创建"
            icon="OfficeBuilding"
          >
            <el-button type="primary" @click="openCreate">+ 新增公司</el-button>
          </EmptyState>
        </template>
      </el-table>
    </div>

    <CompanyFormDialog v-model:visible="formVisible" :editing="editing" @saved="onSaved" />
    <CompanyDetailDrawer v-model:visible="drawerVisible" :company="drawerCompany" />
  </div>
</template>

<style scoped>
.page-header .spacer {
  flex: 1;
}

.company-name {
  font-weight: 500;
  color: var(--color-gray-900);
  cursor: pointer;
}

.company-name:hover {
  color: var(--color-primary-600);
  text-decoration: underline;
}

.count-link {
  cursor: pointer;
  color: var(--color-gray-700);
}

.count-link:hover {
  color: var(--color-primary-600);
  text-decoration: underline;
}
</style>
