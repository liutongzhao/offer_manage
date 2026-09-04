<script setup lang="ts">
import draggable from 'vuedraggable'
import type { Application } from '@/types'
import { STATUS_LIST } from '@/constants/enums'
import StatusTag from './StatusTag.vue'

/** 看板视图（UI-LY-003）：按状态分列，vuedraggable 拖拽改状态 */
const props = defineProps<{ items: Application[] }>()

const emit = defineEmits<{
  (e: 'change-status', appId: number, status: string): void
  (e: 'open', app: Application): void
}>()

const columns = STATUS_LIST.map((s) => ({ status: s.value, meta: s }))

function listFor(status: string): Application[] {
  return props.items.filter((a) => a.status === status)
}

function onChange(evt: unknown, status: string) {
  // vuedraggable 的 added 事件：新卡片从其他列拖入
  const e = evt as { added?: { element: Application } }
  if (e.added?.element) {
    emit('change-status', e.added.element.id, status)
  }
}

function onDragEnterCol(_appId: number, status: string) {
  /* 由 added 事件统一处理 */
}
void onDragEnterCol
</script>

<template>
  <div class="kanban">
    <div v-for="col in columns" :key="col.status" class="kanban-col">
      <div class="col-head" :style="{ '--col-color': col.meta.dot }">
        <span class="col-dot" />
        <span class="col-title">{{ col.status }}</span>
        <span class="col-count num">{{ listFor(col.status).length }}</span>
      </div>
      <draggable
        :list="listFor(col.status)"
        item-key="id"
        group="applications"
        class="col-body"
        ghost-class="drag-ghost"
        drag-class="dragging"
        :animation="200"
        @change="(evt: unknown) => onChange(evt, col.status)"
      >
        <template #item="{ element }">
          <div class="kanban-card" @click="emit('open', element)">
            <div class="card-company">{{ element.company_name || '—' }}</div>
            <div class="card-position">{{ element.position }}</div>
            <div class="card-meta">
              <span>{{ element.city || '—' }}</span>
              <span class="num">{{ element.apply_date || '' }}</span>
            </div>
            <div class="card-badges">
              <span v-if="element.tag_names.length" class="badge">🏷 {{ element.tag_names.length }}</span>
            </div>
          </div>
        </template>
      </draggable>
      <div v-if="!listFor(col.status).length" class="col-empty">暂无</div>
    </div>
  </div>
</template>

<style scoped>
.kanban {
  display: flex;
  gap: var(--sp-4);
  overflow-x: auto;
  padding-bottom: var(--sp-3);
}

.kanban-col {
  width: 280px;
  flex-shrink: 0;
  background: var(--color-gray-100);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
}

.col-head {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  height: 48px;
  padding: 0 var(--sp-3);
  border-top: 3px solid var(--col-color);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  background: var(--color-gray-0);
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--col-color);
}

.col-title {
  font-size: var(--fs-h3);
  font-weight: 600;
  color: var(--color-gray-800);
}

.col-count {
  margin-left: auto;
  font-size: var(--fs-sm);
  color: var(--color-gray-500);
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  padding: 0 8px;
}

.col-body {
  padding: var(--sp-2);
  min-height: 80px;
  flex: 1;
}

.kanban-card {
  background: var(--color-gray-0);
  border: var(--border-base);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xs);
  padding: var(--sp-3);
  margin-bottom: var(--sp-2);
  cursor: grab;
  transition: all 120ms ease-out;
}

.kanban-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.card-company {
  font-size: var(--fs-body-l);
  font-weight: 500;
  color: var(--color-gray-900);
}

.card-position {
  font-size: var(--fs-sm);
  color: var(--color-gray-600);
  margin-top: 2px;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
  margin-top: var(--sp-2);
}

.card-badges {
  margin-top: 4px;
  display: flex;
  gap: var(--sp-2);
}

.badge {
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
}

.col-empty {
  text-align: center;
  color: var(--color-gray-400);
  font-size: var(--fs-sm);
  border: 1px dashed var(--color-gray-300);
  border-radius: var(--radius-md);
  margin: var(--sp-2);
  padding: var(--sp-6) 0;
}

.drag-ghost {
  opacity: 0.6;
  transform: rotate(1.5deg);
}

.dragging {
  box-shadow: var(--shadow-lg);
}
</style>
