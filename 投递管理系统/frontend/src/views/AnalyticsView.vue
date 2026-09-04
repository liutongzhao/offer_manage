<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getFunnel, getSummary, getTrend } from '@/api/analytics'
import type { AnalyticsSummary, FunnelStage, TrendPoint } from '@/types'
import { TYPE_LIST } from '@/constants/enums'
import EmptyState from '@/components/EmptyState.vue'

/** 数据统计（PG-008）：转化漏斗 + 类型分布 + 渠道分布 + 时间趋势（周/月切换） */
const router = useRouter()

const summary = ref<AnalyticsSummary | null>(null)
const stages = ref<FunnelStage[]>([])
const trendData = ref<TrendPoint[]>([])
const granularity = ref<'week' | 'month'>('week')
const loading = ref(true)
const hasData = ref(false)

const funnelRef = ref<HTMLElement>()
const typePieRef = ref<HTMLElement>()
const channelBarRef = ref<HTMLElement>()
const trendRef = ref<HTMLElement>()

let charts: echarts.ECharts[] = []

const TYPE_COLORS: Record<string, string> = {
  后端开发: '#2f6fed',
  测试开发: '#0ba5a5',
  AI开发: '#7c5cff',
}

async function load() {
  loading.value = true
  try {
    const [s, f, t] = await Promise.all([
      getSummary(),
      getFunnel(),
      getTrend(granularity.value),
    ])
    summary.value = s
    stages.value = f.stages
    trendData.value = t
    hasData.value = s.total > 0
    renderCharts()
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  for (const c of charts) c.dispose()
  charts = []

  if (funnelRef.value && stages.value.length) {
    const chart = echarts.init(funnelRef.value)
    const max = stages.value[0]?.count || 1
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      grid: { left: 80, right: 60, top: 10, bottom: 10 },
      xAxis: { show: false },
      yAxis: {
        type: 'category',
        data: stages.value.map((s) => s.stage),
        axisLabel: { fontSize: 13, color: '#344054' },
      },
      series: [
        {
          type: 'bar',
          data: stages.value.map((s, i) => ({
            value: s.count,
            label: {
              show: true,
              position: 'right',
              formatter: `${s.count}（${s.percent}%）`,
              color: '#475467',
              fontSize: 12,
            },
            itemStyle: {
              color: echarts.color.interpolate('#2f6fed', '#9dbefd')(1 - i / Math.max(stages.value.length - 1, 1)),
              borderRadius: 4,
            },
          })),
          barWidth: 28,
          showBackground: true,
          backgroundStyle: { color: '#f2f4f7', borderRadius: 4 },
        },
      ],
    })
    charts.push(chart)
    void max
  }

  if (typePieRef.value && summary.value && Object.keys(summary.value.by_type).length) {
    const chart = echarts.init(typePieRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0, textStyle: { fontSize: 12 } },
      series: [
        {
          type: 'pie',
          radius: ['40%', '68%'],
          label: { show: false },
          data: Object.entries(summary.value.by_type).map(([name, value]) => ({
            name,
            value,
            itemStyle: { color: TYPE_COLORS[name] ?? '#98a2b3' },
          })),
        },
      ],
    })
    charts.push(chart)
  }

  if (channelBarRef.value && summary.value && Object.keys(summary.value.by_channel).length) {
    const chart = echarts.init(channelBarRef.value)
    const entries = Object.entries(summary.value.by_channel)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 70, right: 30, top: 10, bottom: 24 },
      xAxis: { type: 'value', minInterval: 1 },
      yAxis: {
        type: 'category',
        data: entries.map(([k]) => k),
        axisLabel: { fontSize: 12, color: '#344054' },
      },
      series: [
        {
          type: 'bar',
          data: entries.map(([, v]) => v),
          itemStyle: { color: '#2f6fed', borderRadius: 4 },
          barWidth: 20,
        },
      ],
    })
    charts.push(chart)
  }

  if (trendRef.value && trendData.value.length) {
    const chart = echarts.init(trendRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, top: 20, bottom: 28 },
      xAxis: { type: 'category', data: trendData.value.map((p) => p.period), axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [
        {
          type: 'bar',
          data: trendData.value.map((p) => p.count),
          itemStyle: { color: '#2f6fed', borderRadius: [4, 4, 0, 0] },
        },
      ],
    })
    charts.push(chart)
  }
}

watch(granularity, load)

onMounted(() => {
  load()
  window.addEventListener('resize', () => charts.forEach((c) => c.resize()))
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h1>数据统计</h1>
      <div class="spacer" />
      <el-radio-group v-model="granularity" size="small">
        <el-radio-button value="week">按周</el-radio-button>
        <el-radio-button value="month">按月</el-radio-button>
      </el-radio-group>
    </div>

    <div v-loading="loading">
      <EmptyState
        v-if="!hasData && !loading"
        title="还没有数据"
        description="至少记录 1 条投递后，这里会生成分析"
        icon="TrendCharts"
      />

      <template v-else>
        <!-- 转化漏斗 -->
        <div class="app-card">
          <div class="card-title">转化漏斗</div>
          <div class="funnel-table">
            <div v-for="s in stages" :key="s.stage" class="funnel-row">
              <span class="funnel-stage">{{ s.stage }}</span>
              <div class="funnel-bar-wrap">
                <div class="funnel-bar" :style="{ width: Math.max(s.percent, 2) + '%' }" />
              </div>
              <span class="funnel-num num">{{ s.count }}（{{ s.percent }}%）</span>
            </div>
          </div>
          <div ref="funnelRef" style="height: 1px" />
        </div>

        <div class="chart-row">
          <div class="app-card">
            <div class="card-title">类型分布</div>
            <div ref="typePieRef" class="chart" style="height: 260px" />
          </div>
          <div class="app-card">
            <div class="card-title">渠道分布</div>
            <div ref="channelBarRef" class="chart" style="height: 260px" />
          </div>
        </div>

        <div class="app-card">
          <div class="card-title">投递量时间趋势</div>
          <div ref="trendRef" class="chart" style="height: 260px" />
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.page-header .spacer {
  flex: 1;
}

.funnel-table {
  padding: var(--sp-3) 0;
}

.funnel-row {
  display: flex;
  align-items: center;
  gap: var(--sp-4);
  padding: var(--sp-2) 0;
}

.funnel-stage {
  width: 56px;
  font-size: var(--fs-body);
  font-weight: 500;
  color: var(--color-gray-800);
  text-align: right;
  flex-shrink: 0;
}

.funnel-bar-wrap {
  flex: 1;
  background: var(--color-gray-100);
  border-radius: var(--radius-sm);
  height: 24px;
  overflow: hidden;
}

.funnel-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-300));
  border-radius: var(--radius-sm);
  transition: width 400ms ease-out;
}

.funnel-num {
  width: 130px;
  font-size: var(--fs-sm);
  color: var(--color-gray-600);
  flex-shrink: 0;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-4);
  margin-top: var(--sp-4);
}

.app-card {
  margin-bottom: var(--sp-4);
}
</style>
