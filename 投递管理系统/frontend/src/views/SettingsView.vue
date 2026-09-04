<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { Application, BackupInfo, ImportResult, Tag } from '@/types'
import { backupDatabase, getBackups, importApplications, restoreDatabase } from '@/api/data'
import { createTag, deleteTag, getTags, renameTag } from '@/api/tags'
import { deleteApplication, getApplications, restoreApplication } from '@/api/applications'
import EmptyState from '@/components/EmptyState.vue'
import { formatSize } from '@/utils/format'

/** 数据与设置（PG-009）：备份恢复 / 导入导出 / 标签管理 / 已归档 */
const backups = ref<BackupInfo[]>([])
const backuping = ref(false)
const lastBackupAt = ref<string | null>(null)

async function loadBackups() {
  try {
    backups.value = await getBackups()
    lastBackupAt.value = backups.value[0]?.last_modified ?? null
  } catch {
    backups.value = []
  }
}

async function doBackup() {
  backuping.value = true
  try {
    const b = await backupDatabase()
    ElMessage.success(`备份完成：${b.object_key}`)
    loadBackups()
  } catch {
    /* 拦截器已提示 */
  } finally {
    backuping.value = false
  }
}

const restoreVisible = ref(false)
const restoreConfirmText = ref('')
const restoreTarget = ref('')
const restoring = ref(false)

function openRestore(b: BackupInfo) {
  restoreTarget.value = b.object_key
  restoreConfirmText.value = ''
  restoreVisible.value = true
}

async function doRestore() {
  if (restoreConfirmText.value !== '确认恢复') {
    ElMessage.warning('请输入「确认恢复」以执行该高危操作')
    return
  }
  restoring.value = true
  try {
    const r = await restoreDatabase(restoreTarget.value)
    ElMessage.success(r.message)
    restoreVisible.value = false
  } catch {
    /* 拦截器已提示 */
  } finally {
    restoring.value = false
  }
}

/* 导出 */
function doExport() {
  window.open('/api/v1/data/export/applications.csv', '_blank')
  ElMessage.success('已开始下载 CSV')
}

/* 导入 */
const importVisible = ref(false)
const importFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)
const importInput = ref<HTMLInputElement>()

function pickImportFile(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.length) importFile.value = input.files[0]
  input.value = ''
}

async function doImport() {
  if (!importFile.value) {
    ElMessage.warning('请先选择 CSV 文件')
    return
  }
  importing.value = true
  try {
    importResult.value = await importApplications(importFile.value)
    ElMessage.success(`导入完成：成功 ${importResult.value.success_count} 条，失败 ${importResult.value.fail_count} 条`)
  } catch {
    /* 拦截器已提示 */
  } finally {
    importing.value = false
  }
}

/* 标签管理 */
const tags = ref<Tag[]>([])
const newTagName = ref('')

async function loadTags() {
  try {
    tags.value = await getTags()
  } catch {
    tags.value = []
  }
}

async function addTag() {
  const name = newTagName.value.trim()
  if (!name) return
  try {
    await createTag(name)
    ElMessage.success(`已创建标签「${name}」`)
    newTagName.value = ''
    loadTags()
  } catch {
    /* 拦截器已提示 */
  }
}

async function rename(t: Tag) {
  const { value } = await ElMessageBoxPrompt(t.name)
  if (value && value !== t.name) {
    await renameTag(t.id, value)
    ElMessage.success('标签已重命名')
    loadTags()
  }
}

function ElMessageBoxPrompt(current: string) {
  // 轻量封装：使用 Element Plus MessageBox
  return import('element-plus').then(({ ElMessageBox }) =>
    ElMessageBox.prompt('输入新名称', '重命名标签', {
      inputValue: current,
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    }) as unknown as Promise<{ value: string }>,
  )
}

async function removeTag(t: Tag) {
  const count = t.usage_count ?? 0
  try {
    const { ElMessageBox } = await import('element-plus')
    await ElMessageBox.confirm(
      count > 0
        ? `标签「${t.name}」已被 ${count} 条投递使用，删除后将自动解绑（不影响投递记录本身）。确认删除？`
        : `确认删除标签「${t.name}」？`,
      '删除标签',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' },
    )
    await deleteTag(t.id)
    ElMessage.success('标签已删除')
    loadTags()
  } catch {
    /* 取消 */
  }
}

/* 已归档 / 回收站 */
const archivedApps = ref<Application[]>([])
const deletedApps = ref<Application[]>([])
const archivedLoading = ref(false)

async function loadArchived() {
  archivedLoading.value = true
  try {
    const [arch, del] = await Promise.all([
      getApplications({ archived: true, limit: 100 }),
      getApplications({ include_deleted: true, limit: 100 }),
    ])
    archivedApps.value = arch.items
    deletedApps.value = del.items.filter((a) => a.archived === false && isDeleted(a))
  } finally {
    archivedLoading.value = false
  }
}

function isDeleted(a: Application): boolean {
  // 列表返回的已删除记录在 include_deleted 时含 deleted_at（序列化为字符串）
  return (a as unknown as { deleted_at?: string }).deleted_at != null
}

async function unarchive(a: Application) {
  await import('@/api/applications').then((m) => m.updateApplication(a.id, { archived: false }))
  ElMessage.success('已取消归档')
  loadArchived()
}

async function restoreDeleted(a: Application) {
  await restoreApplication(a.id)
  ElMessage.success('已恢复')
  loadArchived()
}

async function purgeDeleted(a: Application) {
  await deleteApplication(a.id)
  ElMessage.success('已彻底删除')
  loadArchived()
}

onMounted(() => {
  loadBackups()
  loadTags()
  loadArchived()
})
</script>

<template>
  <div class="page settings-page">
    <div class="page-header">
      <h1>数据与设置</h1>
    </div>

    <!-- 数据备份 -->
    <div class="app-card">
      <div class="card-title">数据备份</div>
      <div class="backup-line">
        上次备份：
        <span v-if="lastBackupAt" class="num">{{ lastBackupAt }}</span>
        <span v-else class="warn-text">从未（建议现在备份一次，避免数据丢失）</span>
      </div>
      <div class="backup-ops">
        <el-button type="primary" :loading="backuping" @click="doBackup">
          {{ backuping ? '备份中…' : '立即备份' }}
        </el-button>
      </div>
      <div v-if="backups.length" class="backup-list">
        <div v-for="b in backups" :key="b.object_key" class="backup-row">
          <span class="bk-key num">{{ b.object_key }}</span>
          <span class="bk-size num">{{ formatSize(b.size) }}</span>
          <el-button link type="danger" size="small" @click="openRestore(b)">从备份恢复</el-button>
        </div>
      </div>
    </div>

    <!-- 导出 / 导入 -->
    <div class="app-card">
      <div class="card-title">导出与导入</div>
      <div class="backup-ops">
        <el-button @click="doExport">导出投递明细 CSV</el-button>
        <el-button @click="importVisible = true; importResult = null; importFile = null">批量导入投递</el-button>
      </div>
    </div>

    <!-- 标签管理 -->
    <div class="app-card">
      <div class="card-title">标签管理</div>
      <div class="tag-cloud">
        <div v-for="t in tags" :key="t.id" class="tag-chip">
          <span>{{ t.name }}</span>
          <span class="tag-count num">({{ t.usage_count ?? 0 }})</span>
          <el-button link size="small" @click="rename(t)">改</el-button>
          <el-button link type="danger" size="small" @click="removeTag(t)">删</el-button>
        </div>
        <span v-if="!tags.length" class="muted">暂无标签，可在投递表单中自由输入创建</span>
      </div>
      <div class="tag-add">
        <el-input v-model="newTagName" size="small" placeholder="新建标签，回车添加" style="width: 200px" @keyup.enter="addTag" />
        <el-button size="small" @click="addTag">+ 新建标签</el-button>
      </div>
    </div>

    <!-- 已归档 / 回收站 -->
    <div class="app-card">
      <div class="card-title">已归档与回收站</div>
      <div v-loading="archivedLoading">
        <div class="sec-title">已归档投递（{{ archivedApps.length }}）</div>
        <div v-if="!archivedApps.length" class="muted" style="padding: 8px 0">无归档记录</div>
        <div v-for="a in archivedApps" :key="a.id" class="arch-row">
          <span>{{ a.company_name }} · {{ a.position }}</span>
          <el-button link type="primary" size="small" @click="unarchive(a)">取消归档</el-button>
        </div>

        <div class="sec-title">回收站（{{ deletedApps.length }}）</div>
        <div v-if="!deletedApps.length" class="muted" style="padding: 8px 0">回收站为空</div>
        <div v-for="a in deletedApps" :key="a.id" class="arch-row">
          <span>{{ a.company_name }} · {{ a.position }}</span>
          <span>
            <el-button link type="primary" size="small" @click="restoreDeleted(a)">恢复</el-button>
            <el-popconfirm title="彻底删除后不可恢复，确认？" confirm-button-text="彻底删除" cancel-button-text="取消" @confirm="purgeDeleted(a)">
              <template #reference>
                <el-button link type="danger" size="small">彻底删除</el-button>
              </template>
            </el-popconfirm>
          </span>
        </div>
      </div>
    </div>

    <!-- 关于 -->
    <div class="app-card">
      <div class="card-title">关于</div>
      <div class="muted">
        秋招投递管理平台 v0.2.0 · 后端 FastAPI + SQLite + MinIO（localhost:5112） · 前端 Vite + Vue3（localhost:5111）
      </div>
    </div>

    <!-- 恢复确认弹窗（高危：需输入确认文字） -->
    <el-dialog v-model="restoreVisible" title="从备份恢复" width="440px">
      <el-alert
        type="error"
        show-icon
        :closable="false"
        title="恢复将覆盖当前全部数据"
        description="这是唯一会整体覆盖数据的操作。恢复完成后需要重启后端服务。"
        style="margin-bottom: 16px"
      />
      <div class="muted" style="margin-bottom: 8px">目标备份：<span class="num">{{ restoreTarget }}</span></div>
      <el-input v-model="restoreConfirmText" placeholder='请输入「确认恢复」以继续' />
      <template #footer>
        <el-button @click="restoreVisible = false">取消</el-button>
        <el-button type="danger" :loading="restoring" :disabled="restoreConfirmText !== '确认恢复'" @click="doRestore">
          恢复
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入弹窗 -->
    <el-dialog v-model="importVisible" title="批量导入投递（CSV）" width="560px">
      <div class="import-drop" @click="importInput?.click()">
        <template v-if="importFile">
          <b>{{ importFile.name }}</b>
        </template>
        <template v-else>
          点击选择 CSV 文件（UTF-8 / GBK 编码，表头：公司名称/投递类型/岗位名称/当前状态/…）
        </template>
        <input ref="importInput" type="file" accept=".csv" hidden @change="pickImportFile" />
      </div>
      <div v-if="importResult" class="import-result">
        <el-alert
          type="success"
          :closable="false"
          :title="`成功 ${importResult.success_count} 条，失败 ${importResult.fail_count} 条`"
        />
        <div v-if="importResult.failures.length" class="fail-list">
          <div v-for="f in importResult.failures" :key="f.row" class="fail-row">
            第 {{ f.row }} 行：{{ f.error }}
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="importVisible = false">关闭</el-button>
        <el-button type="primary" :loading="importing" @click="doImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.settings-page {
  max-width: 900px;
}

.backup-line {
  font-size: var(--fs-body);
  color: var(--color-gray-700);
  margin-bottom: var(--sp-3);
}

.warn-text {
  color: var(--color-warning-text);
}

.backup-ops {
  display: flex;
  gap: var(--sp-2);
  margin-bottom: var(--sp-3);
}

.backup-list {
  border-top: var(--border-light);
}

.backup-row {
  display: flex;
  align-items: center;
  gap: var(--sp-4);
  padding: var(--sp-2) 0;
  border-bottom: var(--border-light);
  font-size: var(--fs-sm);
}

.bk-key {
  flex: 1;
  color: var(--color-gray-600);
}

.bk-size {
  color: var(--color-gray-500);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-2);
  margin-bottom: var(--sp-3);
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  padding: 2px 6px 2px 12px;
  font-size: var(--fs-sm);
  color: var(--color-gray-700);
}

.tag-count {
  color: var(--color-gray-400);
  font-size: var(--fs-xs);
}

.tag-add {
  display: flex;
  gap: var(--sp-2);
}

.sec-title {
  font-size: var(--fs-sm);
  font-weight: 500;
  color: var(--color-gray-600);
  margin: var(--sp-3) 0 var(--sp-1);
}

.arch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-2) 0;
  border-bottom: var(--border-light);
  font-size: var(--fs-body);
  color: var(--color-gray-700);
}

.muted {
  color: var(--color-gray-400);
  font-size: var(--fs-sm);
}

.import-drop {
  border: 1px dashed var(--color-gray-300);
  border-radius: var(--radius-md);
  background: var(--color-gray-50);
  padding: var(--sp-6);
  text-align: center;
  color: var(--color-gray-500);
  cursor: pointer;
  font-size: var(--fs-sm);
  margin-bottom: var(--sp-3);
}

.fail-list {
  margin-top: var(--sp-2);
  max-height: 160px;
  overflow-y: auto;
}

.fail-row {
  font-size: var(--fs-sm);
  color: var(--color-error-text);
  padding: 2px 0;
}
</style>
