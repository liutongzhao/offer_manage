<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { TimelineItem } from '@/types'
import { EVENT_KIND_META } from '@/constants/enums'
import { formatShortTime } from '@/utils/format'

/**
 * 统一时间线（UI-CP-020 核心组件）：
 * 状态事件+沟通+附件+简历+问题混排；字段变更类默认折叠成一行摘要可展开。
 */
const props = defineProps<{ items: TimelineItem[]; loading?: boolean }>()

const emit = defineEmits<{
  (e: 'open-attachment', item: TimelineItem): void
  (e: 'open-issue', item: TimelineItem): void
}>()

const filter = ref<'all' | 'status' | 'communication' | 'attachment' | 'issue'>('all')

const filtered = computed(() => {
  if (filter.value === 'all') return props.items
  if (filter.value === 'status')
    return props.items.filter((i) => i.kind === 'status' || i.kind === 'field' || i.kind === 'create')
  if (filter.value === 'attachment')
    return props.items.filter((i) => i.kind === 'attachment' || i.kind === 'resume')
  return props.items.filter((i) => i.kind === filter.value)
})

/** 字段变更分组折叠：同一时刻的多条 field 事件折叠成一行 */
interface DisplayGroup {
  key: string
  time: string
  kind: string
  main: TimelineItem
  fields: TimelineItem[]
}

const groups = computed<DisplayGroup[]>(() => {
  const out: DisplayGroup[] = []
  let pending: DisplayGroup | null = null
  for (const item of filtered.value) {
    if (item.kind === 'field') {
      const t = item.time.slice(0, 16)
      if (pending && pending.time === t) {
        pending.fields.push(item)
      } else {
        pending = { key: `${item.kind}-${item.id}-${t}`, time: item.time, kind: 'field', main: item, fields: [item] }
        out.push(pending)
      }
    } else {
      pending = null
      out.push({ key: `${item.kind}-${item.id}-${item.time}`, time: item.time, kind: item.kind, main: item, fields: [] })
    }
  }
  return out
})

const expanded = ref<Set<string>>(new Set())

function toggleExpand(g: DisplayGroup) {
  if (expanded.value.has(g.key)) expanded.value.delete(g.key)
  else expanded.value.add(g.key)
}

function isImage(filename: string | null | undefined): boolean {
  return /\.(png|jpe?g|gif|webp|bmp)$/i.test(filename || '')
}

function kindLabel(kind: string): string {
  return EVENT_KIND_META[kind]?.label ?? kind
}

function kindColor(kind: string): string {
  return EVENT_KIND_META[kind]?.color ?? 'var(--color-gray-400)'
}

function copyAction(g: DisplayGroup) {
  const text = g.main.my_action || ''
  if (!text) return
  ElMessage.info(`待办动作：${text}（请到待办页跟进）`)
}
</script>

<template>
  <div class="timeline-wrap">
    <div class="tl-filter">
      <el-radio-group v-model="filter" size="small">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="status">状态变更</el-radio-button>
        <el-radio-button value="communication">沟通</el-radio-button>
        <el-radio-button value="attachment">附件</el-radio-button>
        <el-radio-button value="issue">问题</el-radio-button>
      </el-radio-group>
    </div>

    <el-empty v-if="!groups.length && !loading" description="暂无记录" :image-size="80" />
    <el-skeleton v-else-if="loading" :rows="5" animated />

    <ul v-else class="tl-list">
      <li v-for="g in groups" :key="g.key" class="tl-item">
        <span class="tl-dot" :style="{ background: kindColor(g.kind) }" />
        <div class="tl-body">
          <div class="tl-head">
            <span class="tl-type">{{ kindLabel(g.kind) }}</span>
            <span class="tl-time num">{{ formatShortTime(g.time) }}</span>
          </div>

          <!-- 字段变更：多条折叠 -->
          <template v-if="g.kind === 'field' && g.fields.length > 1">
            <div class="tl-detail summary-row" @click="toggleExpand(g)">
              <span>修改了 {{ g.fields.length }} 个字段</span>
              <el-icon class="expand-icon" :class="{ open: expanded.has(g.key) }">
                <ArrowDown />
              </el-icon>
            </div>
            <div v-if="expanded.has(g.key)" class="tl-detail field-list">
              <div v-for="(f, fi) in g.fields" :key="f.id ?? fi" class="field-line">
                <b>{{ f.field_name }}：</b>
                <span class="old-val">{{ f.old_value ?? '空' }}</span>
                <el-icon class="arrow"><Right /></el-icon>
                <span class="new-val">{{ f.new_value ?? '空' }}</span>
              </div>
            </div>
          </template>

          <!-- 状态/单字段变更 -->
          <div v-else-if="g.kind === 'status' || (g.kind === 'field' && g.fields.length === 1)" class="tl-detail">
            <template v-if="g.kind === 'status'">
              <span class="old-val">{{ g.main.old_value ?? '空' }}</span>
              <el-icon class="arrow"><Right /></el-icon>
              <b class="new-val">{{ g.main.new_value ?? '空' }}</b>
              <span v-if="g.main.source" class="tl-source">来源：{{ g.main.source }}</span>
            </template>
            <template v-else>
              <b>{{ g.main.field_name }}：</b>
              <span class="old-val">{{ g.main.old_value ?? '空' }}</span>
              <el-icon class="arrow"><Right /></el-icon>
              <span class="new-val">{{ g.main.new_value ?? '空' }}</span>
              <span v-if="g.main.source" class="tl-source">来源：{{ g.main.source }}</span>
            </template>
          </div>

          <!-- 创建记录 -->
          <div v-else-if="g.kind === 'create'" class="tl-detail">创建投递记录</div>

          <!-- 沟通记录 -->
          <template v-else-if="g.kind === 'communication'">
            <div class="tl-detail">
              <span v-if="g.main.contact"><b>{{ g.main.contact }}</b> · </span>{{ g.main.method }}
            </div>
            <div class="tl-detail">{{ g.main.content }}</div>
            <div v-if="g.main.my_action" class="tl-detail action-row">
              <span class="action-text">我方动作：{{ g.main.my_action }}</span>
              <el-button link type="primary" size="small" @click="copyAction(g)">转待办</el-button>
            </div>
          </template>

          <!-- 附件 -->
          <div v-else-if="g.kind === 'attachment' || g.kind === 'resume'" class="tl-detail">
            <el-icon class="file-icon"><Paperclip /></el-icon>
            <span class="file-name">{{ g.main.filename }}</span>
            <el-tag v-if="g.main.att_type" size="small" type="info" effect="plain">{{ g.main.att_type }}</el-tag>
            <el-button
              v-if="isImage(g.main.filename)"
              link
              type="primary"
              size="small"
              @click="emit('open-attachment', g.main)"
            >查看</el-button>
          </div>

          <!-- 问题 -->
          <div v-else-if="g.kind === 'issue'" class="tl-detail issue-line" @click="emit('open-issue', g.main)">
            <span>{{ g.main.title }}</span>
            <span v-if="g.main.description" class="issue-desc">｜{{ g.main.description.slice(0, 40) }}</span>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.tl-filter {
  margin-bottom: var(--sp-4);
}

.tl-list {
  list-style: none;
  margin: 0;
  padding: 0;
  position: relative;
}

.tl-item {
  position: relative;
  padding: 0 0 24px 24px;
}

/* 轴线 */
.tl-item::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 14px;
  bottom: 0;
  width: 2px;
  background: var(--color-gray-200);
}

.tl-item:last-child::before {
  display: none;
}

.tl-dot {
  position: absolute;
  left: 0;
  top: 5px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--color-gray-0);
  box-shadow: 0 0 0 1px var(--color-gray-200);
}

.tl-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--sp-2);
}

.tl-type {
  font-size: var(--fs-sm);
  font-weight: 500;
  color: var(--color-gray-700);
}

.tl-time {
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
}

.tl-detail {
  margin-top: 6px;
  font-size: var(--fs-body);
  color: var(--color-gray-700);
  line-height: 22px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.tl-detail + .tl-detail {
  margin-top: 2px;
}

.tl-source {
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
}

.old-val {
  color: var(--color-gray-400);
  text-decoration: line-through;
}

.new-val {
  color: var(--color-gray-800);
  font-weight: 500;
}

.arrow {
  font-size: 12px;
  color: var(--color-gray-400);
}

.summary-row {
  cursor: pointer;
  color: var(--color-gray-500);
  user-select: none;
}

.expand-icon {
  transition: transform 200ms;
}

.expand-icon.open {
  transform: rotate(180deg);
}

.field-list {
  display: block;
  background: var(--color-gray-50);
  border-radius: var(--radius-sm);
  padding: var(--sp-2) var(--sp-3);
  margin-top: var(--sp-2);
}

.field-line {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  padding: 2px 0;
}

.file-name {
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.issue-line {
  cursor: pointer;
}

.issue-line:hover {
  color: var(--color-primary-600);
}

.issue-desc {
  color: var(--color-gray-500);
  font-size: var(--fs-sm);
}

.action-row {
  justify-content: space-between;
}

.action-text {
  color: var(--color-gray-500);
  font-size: var(--fs-sm);
}
</style>
