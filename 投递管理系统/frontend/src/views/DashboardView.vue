<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import StatCard from '@/components/StatCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getSummary, getTrend, getTodos, getRecentEvents } from '@/api/analytics'
import type { AnalyticsSummary, RecentEventItem, TodoItem, TrendPoint } from '@/types'
import { STATUS_LIST } from '@/constants/enums'
import { formatShortTime } from '@/utils/format'

/** 投递看板（PG-001）：统计卡 + 状态分布 + 趋势 + 待办 + 近期动态 */
const router = useRouter()

const summary = ref<AnalyticsSummary | null>(null)
const todos = ref<TodosOut>({ expired: [], due_soon: [] })
const recent = ref<RecentEventItem[]>([])
const loading = ref(true)
const trendData = ref<TrendPoint[]>([])
const trendGranularity = ref<'week' | 'month'>('week')

const statusPieRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

let statusChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

/** 状态色（与设计令牌一致，ECharts 需要具体色值） */
const COLOR_MAP: Record<string, string> = {
  待投递: '#64748b',
  已投递: '#2f6fed',
  笔试中: '#7c5cff',
  面试中: '#f59e0b',
  已Offer: '#12b76a',
  已挂: '#f04438',
  已拒绝: '#98a2b3',
  爽约: '#475467',
}

async function load() {
  loading.value = true
  try {
    summary.value = await getSummary()
    todos.value = await getTodos()
    recent.value = await getRecentEvents(10)
    trendData.value = await getTrend(trendGranularity.value)
    renderCharts()
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  if (statusPieRef.value && summary.value) {
    statusChart = statusChart || echarts.init(statusPieRef.value)
    const data = Object.entries(summary.value.by_status).map(([name, value]) => ({
      name,
      value,
      itemStyle: { color: COLOR_MAP[name] ?? '#98a2b3' },
    }))
    statusChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', right: 0, top: 'center', textStyle: { fontSize: 12 } },
      series: [
        {
          type: 'pie',
          radius: ['45%', '72%'],
          center: ['38%', '50%'],
          label: { show: false },
          data,
        },
      ],
    })
  }
  if (trendChartRef.value) {
    trendChart = trendChart || echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, top: 20, bottom: 28 },
      xAxis: { type: 'category', data: trendData.value.map((p) => p.period), axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [
        {
          type: 'line',
          data: trendData.value.map((p) => p.count),
          smooth: true,
          areaStyle: { opacity: 0.12 },
          itemStyle: { color: '#2f6fed' },
        },
      ],
    })
  }
}

watch(trendGranularity, async (g) => {
  trendData.value = await getTrend(g)
  renderCharts()
})

onMounted(() => {
  load()
  window.addEventListener('resize', () => {
    statusChart?.resize()
    trendChart?.resize()
  })
})

function goApplications(status?: string) {
  router.push(status ? { path: '/applications', query: { status } } : '/applications')
}

function openApp(id: number) {
  router.push(`/applications/${id}`)
}

function allTodos(): TodoItem[] {
  return [...todos.value.expired, ...todos.value.due_soon]
}

function inProgress(): number {
  if (!summary.value) return 0
  const ended =
    (summary.value.by_status['已挂'] ?? 0) +
    (summary.value.by_status['已拒绝'] ?? 0) +
    (summary.value.by_status['爽约'] ?? 0)
  return summary.value.total - ended
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>投递看板</h1>
    </div>

    <div v-loading="loading">
      <!-- 统计卡 4 连 -->
      <div class="stat-row">
        <div @click="goApplications()"><StatCard label="投递总数" :value="summary?.total ?? 0" hint="全部投递记录" color="var(--color-primary-500)" /></div>
        <StatCard label="进行中" :value="inProgress()" hint="尚未出结果" color="var(--color-info-solid)" />
        <div @click="goApplications('面试中')"><StatCard label="面试中" :value="summary?.interviewing ?? 0" hint="点击查看面试中的投递" color="var(--color-warning-solid)" /></div>
        <div @click="goApplications('已Offer')"><StatCard label="已 Offer" :value="summary?.offered ?? 0" :hint="`转化率 ${summary?.conversion_rate ?? 0}%`" color="var(--color-success-solid)" /></div>
      </div>

      <div class="mid-row">
        <div class="charts-col">
          <div class="app-card">
            <div class="card-title">状态分布</div>
            <div v-if="summary && summary.total" ref="statusPieRef" class="chart" style="height: 280px" />
            <EmptyState
              v-else-if="!loading"
              title="还没有投递记录"
              description="创建第一条投递，开始追踪你的秋招进度"
              icon="Promotion"
            >
              <el-button type="primary" @click="goApplications()">去新增</el-button>
            </EmptyState>
          </div>
          <div class="app-card">
            <div class="card-title">
              <span>投递趋势</span>
              <el-radio-group v-model="trendGranularity" size="small">
                <el-radio-button value="week">按周</el-radio-button>
                <el-radio-button value="month">按月</el-radio-button>
              </el-radio-group>
            </div>
            <div ref="trendChartRef" class="chart" style="height: 240px" />
          </div>
        </div>

        <div class="todo-col">
          <div class="app-card">
            <div class="card-title">
              <span>待办与提醒</span>
              <el-button link type="primary" size="small" @click="router.push('/todos')">全部 ▸</el-button>
            </div>
            <EmptyState
              v-if="!allTodos().length"
              title="当前没有待办事项"
              description="临近的面试与截止日期会出现在这里"
              icon="Bell"
            />
            <div
              v-for="t in allTodos()"
              :key="t.application_id"
              class="todo-row"
              @click="openApp(t.application_id)"
            >
              <span class="urgency-dot" :class="t.days_left < 0 ? 'red' : t.days_left <= 1 ? 'amber' : 'blue'" />
              <div class="todo-info">
                <div class="todo-title">{{ t.company_name }} · {{ t.position }}</div>
                <div class="todo-sub">
                  {{ t.days_left < 0 ? `已过期 ${-t.days_left} 天` : t.days_left === 0 ? '今天截止' : `${t.days_left} 天后截止` }}
                  · {{ t.deadline }}
                </div>
              </div>
            </div>
          </div>

          <div class="app-card">
            <div class="card-title">近期动态</div>
            <div v-if="!recent.length" class="todo-sub" style="padding: 12px 0">暂无动态</div>
            <div v-for="(e, i) in recent" :key="i" class="recent-row" @click="openApp(e.application_id)">
              <span class="recent-time num">{{ formatShortTime(e.time) }}</span>
              <span class="recent-text">{{ e.company_name }} · {{ e.summary }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--sp-4);
  cursor: default;
}

.stat-row > div {
  cursor: pointer;
}

.mid-row {
  display: grid;
  grid-template-columns: 8fr 4fr;
  gap: var(--sp-4);
  margin-top: var(--sp-4);
  align-items: start;
}

.charts-col {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
}

.todo-col {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
}

.todo-row {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-1);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.todo-row:hover {
  background: var(--color-primary-50);
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

.todo-title {
  font-size: var(--fs-body);
  font-weight: 500;
  color: var(--color-gray-800);
}

.todo-sub {
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
}

.recent-row {
  display: flex;
  gap: var(--sp-2);
  padding: 6px var(--sp-1);
  font-size: var(--fs-sm);
  color: var(--color-gray-600);
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.recent-row:hover {
  background: var(--color-gray-50);
}

.recent-time {
  color: var(--color-gray-400);
  flex-shrink: 0;
  font-size: var(--fs-xs);
  padding-top: 2px;
}

@media (max-width: 1280px) {
  .mid-row {
    grid-template-columns: 1fr;
  }
}
</style>
