<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { Application, CompanyWithCount } from '@/types'
import { getApplications } from '@/api/applications'
import StatusTag from './StatusTag.vue'

/** 公司详情抽屉（PG-011）：公司字段 + 该公司全部投递（REQ-COM-002） */
const props = defineProps<{
  visible: boolean
  company: CompanyWithCount | null
}>()

const emit = defineEmits<{ (e: 'update:visible', v: boolean): void }>()

const router = useRouter()
const apps = ref<Application[]>([])
const loading = ref(false)

watch(
  () => props.visible,
  async (v) => {
    if (!v || !props.company) return
    loading.value = true
    try {
      const data = await getApplications({ company_id: props.company.id, limit: 100 })
      apps.value = data.items
    } catch {
      apps.value = []
    } finally {
      loading.value = false
    }
  },
)

function openApp(app: Application) {
  emit('update:visible', false)
  router.push(`/applications/${app.id}`)
}

function viewAll() {
  if (!props.company) return
  emit('update:visible', false)
  router.push({ path: '/applications', query: { company_id: String(props.company.id) } })
}
</script>

<template>
  <el-drawer
    :model-value="visible"
    :title="company?.name || '公司详情'"
    size="520px"
    @update:model-value="emit('update:visible', $event)"
  >
    <template v-if="company">
      <div class="company-meta">
        <div v-if="company.alias" class="meta-line"><span class="k">别名</span>{{ company.alias }}</div>
        <div v-if="company.city" class="meta-line"><span class="k">城市</span>{{ company.city }}</div>
        <div v-if="company.industry" class="meta-line"><span class="k">行业</span>{{ company.industry }}</div>
        <div v-if="company.scale" class="meta-line"><span class="k">规模</span>{{ company.scale }}</div>
        <div v-if="company.website" class="meta-line">
          <span class="k">官网</span>
          <a :href="company.website" target="_blank" class="site-link">{{ company.website }}</a>
        </div>
        <div v-if="company.notes" class="meta-line"><span class="k">备注</span>{{ company.notes }}</div>
      </div>

      <div class="apps-head">
        <span>全部投递（{{ company.application_count }}）</span>
        <el-button link type="primary" size="small" @click="viewAll">查看全部 ▸</el-button>
      </div>

      <el-empty v-if="!apps.length && !loading" description="该公司下暂无投递记录" :image-size="64" />
      <div v-for="app in apps" :key="app.id" class="app-row" @click="openApp(app)">
        <div class="app-info">
          <div class="app-position">{{ app.position }}</div>
          <div class="app-sub">{{ app.type }} · {{ app.city || '—' }} · {{ app.apply_date || '未投递' }}</div>
        </div>
        <StatusTag :status="app.status" size="S" />
      </div>
    </template>
  </el-drawer>
</template>

<style scoped>
.company-meta {
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
  padding: var(--sp-3) var(--sp-4);
  margin-bottom: var(--sp-4);
}

.meta-line {
  font-size: var(--fs-body);
  color: var(--color-gray-700);
  padding: 3px 0;
}

.meta-line .k {
  display: inline-block;
  width: 48px;
  color: var(--color-gray-500);
  font-size: var(--fs-sm);
}

.site-link {
  color: var(--color-primary-600);
}

.apps-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--fs-h3);
  font-weight: 600;
  margin-bottom: var(--sp-3);
}

.app-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-3) var(--sp-2);
  border-bottom: var(--border-light);
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.app-row:hover {
  background: var(--color-primary-50);
}

.app-position {
  font-size: var(--fs-body-l);
  font-weight: 500;
  color: var(--color-gray-900);
}

.app-sub {
  font-size: var(--fs-sm);
  color: var(--color-gray-500);
  margin-top: 2px;
}
</style>
