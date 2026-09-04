<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { Resume } from '@/types'
import { deleteResume, getResumes, getResumeUrl, uploadResume } from '@/api/resumes'
import EmptyState from '@/components/EmptyState.vue'
import { formatDateTime, formatSize } from '@/utils/format'

/** 简历资产（PG-006）：版本库网格 + 上传（初始简历/定制版） + 预览 */
const items = ref<Resume[]>([])
const loading = ref(false)
const gridMode = ref(true)

async function load() {
  loading.value = true
  try {
    items.value = await getResumes()
  } finally {
    loading.value = false
  }
}

onMounted(load)

const sorted = computed(() => items.value)

/* 上传弹窗 */
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadForm = ref({
  company: '',
  version: '',
  isBase: false,
})
const fileInput = ref<HTMLInputElement>()
const pendingFile = ref<File | null>(null)

function openUpload() {
  uploadForm.value = { company: '', version: '', isBase: false }
  pendingFile.value = null
  uploadVisible.value = true
}

function pickFile(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.length) pendingFile.value = input.files[0]
  input.value = ''
}

function onDrop(e: DragEvent) {
  if (e.dataTransfer?.files?.length) pendingFile.value = e.dataTransfer.files[0]
}

async function doUpload() {
  if (!pendingFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  uploading.value = true
  try {
    await uploadResume({
      file: pendingFile.value,
      company: uploadForm.value.company || null,
      isBase: uploadForm.value.isBase,
      version: uploadForm.value.version || null,
    })
    ElMessage.success('简历已上传')
    uploadVisible.value = false
    load()
  } catch {
    /* 拦截器已提示 */
  } finally {
    uploading.value = false
  }
}

async function preview(r: Resume) {
  const url = await getResumeUrl(r.id)
  window.open(url, '_blank')
}

async function remove(r: Resume) {
  await deleteResume(r.id)
  ElMessage.success('简历已删除')
  load()
}

const hasBase = computed(() => items.value.some((r) => r.is_base))
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>简历资产</h1>
      <div class="spacer" />
      <el-radio-group v-model="gridMode" size="small">
        <el-radio-button :value="true">网格</el-radio-button>
        <el-radio-button :value="false">列表</el-radio-button>
      </el-radio-group>
      <el-button type="primary" @click="openUpload">+ 上传简历</el-button>
    </div>

    <el-alert
      v-if="!hasBase && items.length"
      title="尚未标记初始简历，建议先指定一份作为母版"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 16px"
    />

    <div v-loading="loading">
      <!-- 网格视图 -->
      <div v-if="gridMode && sorted.length" class="resume-grid">
        <div v-for="r in sorted" :key="r.id" class="resume-card" :class="{ base: r.is_base }">
          <div class="resume-thumb" @click="preview(r)">
            <el-icon :size="32"><Document /></el-icon>
            <span v-if="r.is_base" class="base-badge">★ 初始</span>
          </div>
          <div class="resume-name" :title="r.filename">{{ r.filename }}</div>
          <div class="resume-meta">
            {{ r.company || '通用' }}<template v-if="r.version"> · {{ r.version }}</template>
          </div>
          <div class="resume-sub num">{{ formatSize(r.size) }} · {{ formatDateTime(r.uploaded_at)?.slice(0, 10) }}</div>
          <div class="resume-ops">
            <el-button link type="primary" size="small" @click="preview(r)">预览</el-button>
            <el-popconfirm title="确认删除该简历？" confirm-button-text="删除" cancel-button-text="取消" @confirm="remove(r)">
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else-if="sorted.length" class="app-card" style="padding: 0; overflow: hidden">
        <el-table :data="sorted" style="width: 100%">
          <el-table-column prop="filename" label="文件名" min-width="220" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="num">{{ row.is_base ? '★ ' : '' }}{{ row.filename }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="company" label="公司" width="120" />
          <el-table-column prop="version" label="版本" width="90" />
          <el-table-column label="大小" width="90" align="right">
            <template #default="{ row }"><span class="num">{{ formatSize(row.size) }}</span></template>
          </el-table-column>
          <el-table-column label="上传时间" width="160">
            <template #default="{ row }"><span class="num">{{ formatDateTime(row.uploaded_at) }}</span></template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="preview(row)">预览</el-button>
              <el-popconfirm title="确认删除该简历？" confirm-button-text="删除" cancel-button-text="取消" @confirm="remove(row)">
                <template #reference>
                  <el-button link type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <EmptyState
        v-else-if="!loading"
        title="还没有简历"
        description="上传你的初始简历，之后可基于它生成定制版本"
        icon="Document"
      >
        <el-button type="primary" @click="openUpload">+ 上传简历</el-button>
      </EmptyState>
    </div>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传简历" width="560px">
      <div
        class="upload-drop"
        @dragover.prevent
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <template v-if="pendingFile">
          <el-icon :size="28" color="var(--color-primary-500)"><Document /></el-icon>
          <div class="uf-name">{{ pendingFile.name }}</div>
          <div class="uf-size num">{{ formatSize(pendingFile.size) }}</div>
        </template>
        <template v-else>
          <el-icon :size="28"><UploadFilled /></el-icon>
          <div>拖拽文件到此处，或 点击选择（≤ 20MB）</div>
        </template>
        <input ref="fileInput" type="file" hidden @change="pickFile" />
      </div>
      <el-form label-width="110px" style="margin-top: 12px">
        <el-form-item label="公司（快照）">
          <el-input v-model="uploadForm.company" placeholder="如：字节跳动；初始简历可留空" />
        </el-form-item>
        <el-form-item label="版本号">
          <el-input v-model="uploadForm.version" placeholder="如 v1、v2 或「字节版」" />
        </el-form-item>
        <el-form-item label="初始简历">
          <el-switch v-model="uploadForm.isBase" />
          <span class="hint">标记母版，便于对比各定制版本</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="doUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-header .spacer {
  flex: 1;
}

.resume-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--sp-4);
}

.resume-card {
  background: var(--color-gray-0);
  border: var(--border-base);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xs);
  padding: var(--sp-3);
  text-align: left;
}

.resume-card.base {
  border: 2px solid var(--color-amber-400);
}

.resume-thumb {
  height: 120px;
  background: var(--color-gray-50);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-400);
  cursor: pointer;
  position: relative;
  margin-bottom: var(--sp-2);
}

.base-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  background: var(--color-amber-50);
  color: var(--color-amber-700);
  font-size: var(--fs-xs);
  padding: 1px 8px;
  border-radius: var(--radius-full);
}

.resume-name {
  font-size: var(--fs-body);
  font-weight: 500;
  color: var(--color-gray-900);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resume-meta {
  font-size: var(--fs-sm);
  color: var(--color-gray-600);
  margin-top: 2px;
}

.resume-sub {
  font-size: var(--fs-xs);
  color: var(--color-gray-400);
  margin-top: 2px;
}

.resume-ops {
  margin-top: var(--sp-2);
  display: flex;
  gap: var(--sp-1);
}

.upload-drop {
  height: 140px;
  border: 1px dashed var(--color-gray-300);
  border-radius: var(--radius-md);
  background: var(--color-gray-50);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--color-gray-500);
  cursor: pointer;
  font-size: var(--fs-sm);
}

.uf-name {
  font-weight: 500;
  color: var(--color-gray-800);
}

.hint {
  margin-left: 10px;
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
}
</style>
