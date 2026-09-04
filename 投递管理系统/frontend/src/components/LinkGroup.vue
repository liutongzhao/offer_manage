<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { ApplicationLink } from '@/types'
import { LINK_TYPES } from '@/constants/enums'
import {
  createLink,
  deleteLink,
  updateLink,
} from '@/api/links'

/** 链接组（UI-CP-021）：增删 / 标记失效 / 一键打开 / 复制 */
const props = defineProps<{ applicationId: number; links: ApplicationLink[] }>()

const emit = defineEmits<{ (e: 'refresh'): void }>()

const adding = ref(false)
const newName = ref('')
const newUrl = ref('')
const newType = ref('其他')

async function addLink() {
  const url = newUrl.value.trim()
  if (!url) {
    ElMessage.warning('请输入链接地址')
    return
  }
  try {
    await createLink(props.applicationId, {
      url,
      name: newName.value.trim() || undefined,
      link_type: newType.value,
    })
    ElMessage.success('已添加链接')
    adding.value = false
    newName.value = ''
    newUrl.value = ''
    newType.value = '其他'
    emit('refresh')
  } catch {
    /* 错误提示由 client 拦截器统一处理 */
  }
}

async function toggleInvalid(link: ApplicationLink) {
  await updateLink(link.id, { is_invalid: !link.is_invalid })
  emit('refresh')
}

async function removeLink(link: ApplicationLink) {
  await deleteLink(link.id)
  ElMessage.success('已删除链接')
  emit('refresh')
}

function openLink(url: string) {
  window.open(url, '_blank')
}

async function copyLink(link: ApplicationLink) {
  try {
    await navigator.clipboard.writeText(link.url)
    ElMessage.success('链接已复制')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

/** 粘贴 URL 后自动填充名称（取域名） */
function onPasteUrl() {
  if (newName.value.trim()) return
  try {
    const u = new URL(newUrl.value)
    newName.value = u.hostname.replace('www.', '')
  } catch {
    /* 非法 URL 暂不填名称 */
  }
}
</script>

<template>
  <div class="link-group">
    <div v-for="link in links" :key="link.id" class="link-item" :class="{ invalid: link.is_invalid }">
      <el-icon class="link-icon"><Link /></el-icon>
      <el-tooltip :content="link.url" placement="top" :disabled="link.url.length < 40">
        <span class="link-name" @click="!link.is_invalid && openLink(link.url)">{{ link.name }}</span>
      </el-tooltip>
      <el-tag v-if="link.is_invalid" size="small" type="info">已失效</el-tag>
      <span class="link-actions">
        <el-tooltip content="打开">
          <el-button :icon="''" circle size="small" :disabled="link.is_invalid" @click="openLink(link.url)">
            <el-icon><TopRight /></el-icon>
          </el-button>
        </el-tooltip>
        <el-button circle size="small" @click="copyLink(link)"><el-icon><CopyDocument /></el-icon></el-button>
        <el-tooltip :content="link.is_invalid ? '恢复有效' : '标记失效'">
          <el-button circle size="small" @click="toggleInvalid(link)">
            <el-icon><component :is="link.is_invalid ? 'RefreshLeft' : 'CircleClose'" /></el-icon>
          </el-button>
        </el-tooltip>
        <el-popconfirm title="确认删除该链接？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removeLink(link)">
          <template #reference>
            <el-button circle size="small" type="danger" plain><el-icon><Delete /></el-icon></el-button>
          </template>
        </el-popconfirm>
      </span>
    </div>

    <div v-if="!links.length && !adding" class="link-empty">暂无链接</div>

    <!-- 内联添加 -->
    <div v-if="adding" class="link-add-form">
      <el-select v-model="newType" size="small" style="width: 110px">
        <el-option v-for="t in LINK_TYPES" :key="t" :label="t" :value="t" />
      </el-select>
      <el-input v-model="newName" size="small" placeholder="链接名称（可留空自动取域名）" style="flex: 1" />
      <el-input v-model="newUrl" size="small" placeholder="粘贴链接地址，回车保存" style="flex: 2" @paste="onPasteUrl" @keyup.enter="addLink" />
      <el-button type="primary" size="small" @click="addLink">保存</el-button>
      <el-button size="small" @click="adding = false">取消</el-button>
    </div>
    <el-button v-else size="small" text type="primary" @click="adding = true">+ 添加链接</el-button>
  </div>
</template>

<style scoped>
.link-item {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  height: 40px;
  padding: 0 var(--sp-2);
  border-radius: var(--radius-sm);
}

.link-item:hover {
  background: var(--color-gray-50);
}

.link-item.invalid .link-name {
  text-decoration: line-through;
  color: var(--color-gray-400);
}

.link-icon {
  color: var(--color-gray-400);
}

.link-name {
  flex: 1;
  font-size: var(--fs-body);
  color: var(--color-gray-800);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.link-item:not(.invalid) .link-name:hover {
  color: var(--color-primary-600);
  text-decoration: underline;
}

.link-actions {
  display: none;
  gap: 4px;
}

.link-item:hover .link-actions {
  display: inline-flex;
}

.link-empty {
  font-size: var(--fs-body);
  color: var(--color-gray-400);
  padding: var(--sp-2) 0;
}

.link-add-form {
  display: flex;
  gap: var(--sp-2);
  align-items: center;
  margin: var(--sp-2) 0;
  flex-wrap: wrap;
}
</style>
