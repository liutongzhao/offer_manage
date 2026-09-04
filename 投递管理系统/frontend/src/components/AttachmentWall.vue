<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { Attachment } from '@/types'
import { ATTACHMENT_TYPES } from '@/constants/enums'
import { formatSize } from '@/utils/format'
import {
  deleteAttachment,
  getAttachmentUrl,
  uploadAttachment,
  updateAttachmentType,
} from '@/api/attachments'
import Lightbox from './Lightbox.vue'

/**
 * 附件墙（UI-CP-019 Uploader）：
 * 拖拽多文件上传、类型标注、图片灯箱预览、删除（REQ-ATT-001/002）。
 */
const props = defineProps<{ applicationId: number; attachments: Attachment[] }>()

const emit = defineEmits<{ (e: 'refresh'): void }>()

const uploading = ref(false)
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement>()

const imageUrls = computed(() => props.attachments.filter(isImage).map((a) => a.object_key))

function isImage(a: Attachment): boolean {
  return /\.(png|jpe?g|gif|webp|bmp)$/i.test(a.filename)
}

async function uploadFiles(files: FileList | File[] | null | undefined) {
  if (!files || uploading.value) return
  const list = Array.from(files)
  if (!list.length) return
  uploading.value = true
  let okCount = 0
  for (const f of list) {
    try {
      await uploadAttachment({ applicationId: props.applicationId, file: f })
      okCount += 1
    } catch {
      /* 单个失败继续 */
    }
  }
  uploading.value = false
  if (okCount) {
    ElMessage.success(`已上传 ${okCount} 个文件`)
    emit('refresh')
  }
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  uploadFiles(e.dataTransfer?.files)
}

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  uploadFiles(input.files)
  input.value = ''
}

async function preview(a: Attachment) {
  try {
    const url = await getAttachmentUrl(a.id)
    window.open(url, '_blank')
  } catch {
    ElMessage.error('预览失败：存储服务未连接')
  }
}

async function changeType(a: Attachment, t: string) {
  await updateAttachmentType(a.id, t)
  ElMessage.success('类型已更新')
  emit('refresh')
}

async function remove(a: Attachment) {
  await deleteAttachment(a.id)
  ElMessage.success('已删除附件')
  emit('refresh')
}

/* 灯箱 */
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)

function openLightbox(a: Attachment) {
  const imgs = props.attachments.filter(isImage)
  lightboxIndex.value = Math.max(0, imgs.findIndex((i) => i.id === a.id))
  lightboxVisible.value = true
}

const lightboxUrls = computed(() =>
  props.attachments.filter(isImage).map((a) => getAttachmentUrl(a.id)),
)

function onLightboxReady(urlPromise: Promise<string>) {
  return urlPromise
}
</script>

<template>
  <div class="attachment-wall">
    <!-- 拖拽上传区 -->
    <div
      class="dropzone"
      :class="{ over: dragOver, uploading }"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <el-icon :size="22"><UploadFilled /></el-icon>
      <span v-if="!uploading">拖拽文件到此处，或 点击上传（支持多文件，单个 ≤ 20MB）</span>
      <span v-else>上传中…</span>
      <input ref="fileInput" type="file" multiple hidden @change="onPick" />
    </div>

    <!-- 附件网格 -->
    <div v-if="attachments.length" class="att-grid">
      <div v-for="a in attachments" :key="a.id" class="att-item">
        <div class="att-thumb" :class="{ img: isImage(a) }" @click="openLightbox(a)">
          <img v-if="isImage(a)" :src="getAttachmentUrl(a.id)" alt="" @error="($event) => (($event.target as HTMLElement).style.display = 'none')" />
          <el-icon v-else :size="26"><Document /></el-icon>
        </div>
        <div class="att-info">
          <div class="att-name" :title="a.filename">{{ a.filename }}</div>
          <div class="att-meta">{{ a.att_type }} · {{ formatSize(a.size) }}</div>
          <div class="att-ops">
            <el-select
              :model-value="a.att_type"
              size="small"
              style="width: 96px"
              @change="(v: string) => changeType(a, v)"
            >
              <el-option v-for="t in ATTACHMENT_TYPES" :key="t" :label="t" :value="t" />
            </el-select>
            <el-button link type="primary" size="small" @click="preview(a)">预览</el-button>
            <el-popconfirm title="确认删除该附件？" confirm-button-text="删除" cancel-button-text="取消" @confirm="remove(a)">
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="att-empty">暂无附件，可上传 JD 截图、笔试记录或 offer 截图</div>

    <!-- 图片灯箱 -->
    <Lightbox
      v-model:visible="lightboxVisible"
      v-model:index="lightboxIndex"
      :urls="lightboxUrls"
    />
  </div>
</template>

<style scoped>
.dropzone {
  height: 96px;
  border: 1px dashed var(--color-gray-300);
  border-radius: var(--radius-md);
  background: var(--color-gray-50);
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-500);
  font-size: var(--fs-sm);
  cursor: pointer;
  transition: all 120ms ease-out;
  margin-bottom: var(--sp-3);
}

.dropzone.over,
.dropzone:hover {
  border-color: var(--color-primary-500);
  background: var(--color-primary-50);
  color: var(--color-primary-600);
}

.dropzone.uploading {
  pointer-events: none;
  opacity: 0.7;
}

.att-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: var(--sp-3);
}

.att-item {
  display: flex;
  gap: var(--sp-2);
  padding: var(--sp-2);
  border: var(--border-base);
  border-radius: var(--radius-md);
  background: var(--color-gray-0);
}

.att-thumb {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  background: var(--color-gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-400);
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
}

.att-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.att-info {
  min-width: 0;
  flex: 1;
}

.att-name {
  font-size: var(--fs-sm);
  font-weight: 500;
  color: var(--color-gray-800);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.att-meta {
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
  margin: 2px 0 4px;
}

.att-ops {
  display: flex;
  align-items: center;
  gap: 4px;
}

.att-empty {
  font-size: var(--fs-sm);
  color: var(--color-gray-400);
  text-align: center;
  padding: var(--sp-3) 0;
}
</style>
