<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTodos } from '@/api/analytics'
import type { TodosOut, TodoItem } from '@/types'
import EmptyState from '@/components/EmptyState.vue'
import StatusTag from '@/components/StatusTag.vue'

/** 待办提醒（PG-004）：已逾期 / 7 天内截止 分组列表 */
const router = useRouter()

const todos = ref<TodosOut>({ expired: [], due_soon: [] })
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    todos.value = await getTodos()
  } finally {
    loading.value = false
  }
}

onMounted(load)

const all = computed<TodoItem[]>(() => [...todos.value.expired, ...todos.value.due_soon])

function urgencyClass(t: TodoItem): string {
  if (t.days_left < 0) return 'red'
  if (t.days_left <= 1) return 'amber'
  return 'blue'
}

function urgencyText(t: TodoItem): string {
  if (t.days_left < 0) return `已过期 ${-t.days_left} 天`
  if (t.days_left === 0) return '今天截止'
  return `${t.days_left} 天后截止`
}

function open(t: TodoItem) {
  router.push(`/applications/${t.application_id}`)
}
</script>

<template>
  <div class="page todos-page">
    <div class="page-header">
      <h1>待办提醒</h1>
      <div class="spacer" />
      <el-button @click="load">刷新</el-button>
    </div>

    <div v-loading="loading">
      <EmptyState
        v-if="!all.length && !loading"
        title="当前没有待办事项"
        description="临近的面试与截止日期会出现在这里"
        icon="Bell"
      />

      <!-- 已逾期 -->
      <div v-if="todos.expired.length" class="group">
        <div class="group-head">
          <span class="g-title red">已逾期</span>
          <span class="g-count num">{{ todos.expired.length }}</span>
        </div>
        <div v-for="t in todos.expired" :key="t.application_id" class="todo-card" @click="open(t)">
          <span class="urgency-dot red" />
          <div class="todo-main">
            <div class="todo-title">{{ t.company_name }} · {{ t.position }}</div>
            <div class="todo-sub num">{{ t.deadline }} · 截止日期已过 {{ -t.days_left }} 天</div>
          </div>
          <StatusTag :status="t.status" size="S" />
          <el-button type="primary" size="small" plain>去处理</el-button>
        </div>
      </div>

      <!-- 7 天内截止 -->
      <div v-if="todos.due_soon.length" class="group">
        <div class="group-head">
          <span class="g-title amber">7 天内截止</span>
          <span class="g-count num">{{ todos.due_soon.length }}</span>
        </div>
        <div v-for="t in todos.due_soon" :key="t.application_id" class="todo-card" @click="open(t)">
          <span class="urgency-dot" :class="urgencyClass(t)" />
          <div class="todo-main">
            <div class="todo-title">{{ t.company_name }} · {{ t.position }}</div>
            <div class="todo-sub num">{{ t.deadline }} · {{ urgencyText(t) }}</div>
          </div>
          <StatusTag :status="t.status" size="S" />
          <el-button type="primary" size="small" plain>去处理</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.todos-page {
  max-width: 900px;
}

.group {
  margin-bottom: var(--sp-6);
}

.group-head {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  height: 40px;
}

.g-title {
  font-size: var(--fs-sm);
  font-weight: 500;
}

.g-title.red {
  color: var(--color-error-text);
}

.g-title.amber {
  color: var(--color-warning-text);
}

.g-count {
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
  background: var(--color-gray-100);
  border-radius: var(--radius-full);
  padding: 0 8px;
}

.todo-card {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  background: var(--color-gray-0);
  border: var(--border-base);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xs);
  padding: var(--sp-3) var(--sp-4);
  margin-bottom: var(--sp-2);
  cursor: pointer;
  transition: all 120ms ease-out;
}

.todo-card:hover {
  box-shadow: var(--shadow-md);
}

.urgency-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.urgency-dot.red {
  background: var(--color-error-solid);
}

.urgency-dot.amber {
  background: var(--color-warning-solid);
}

.urgency-dot.blue {
  background: var(--color-primary-500);
}

.todo-main {
  flex: 1;
  min-width: 0;
}

.todo-title {
  font-size: var(--fs-body-l);
  font-weight: 500;
  color: var(--color-gray-900);
}

.todo-sub {
  font-size: var(--fs-sm);
  color: var(--color-gray-500);
  margin-top: 2px;
}
</style>
