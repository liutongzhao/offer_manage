<script setup lang="ts">
import { onMounted } from 'vue'
import StatCard from '@/components/StatCard.vue'
import { useAnalyticsStore } from '@/stores/analytics'

const analytics = useAnalyticsStore()

onMounted(() => {
  analytics.fetchSummary()
})
</script>

<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="6">
        <StatCard label="投递总数" :value="analytics.summary.total" />
      </el-col>
      <el-col :span="6">
        <StatCard
          label="进行中"
          :value="analytics.summary.by_status['进行中'] || 0"
        />
      </el-col>
      <el-col :span="6">
        <StatCard
          label="已拿 Offer"
          :value="analytics.summary.by_status['已拿Offer'] || 0"
        />
      </el-col>
      <el-col :span="6">
        <StatCard label="问题记录" :value="analytics.summary.issues_total" />
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card header="按类型分布" shadow="never">
          <el-empty
            v-if="!Object.keys(analytics.summary.by_type).length"
            description="暂无数据"
          />
          <ul v-else class="dist-list">
            <li v-for="(v, k) in analytics.summary.by_type" :key="k">
              <span>{{ k }}</span><strong>{{ v }}</strong>
            </li>
          </ul>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="按状态分布" shadow="never">
          <el-empty
            v-if="!Object.keys(analytics.summary.by_status).length"
            description="暂无数据"
          />
          <ul v-else class="dist-list">
            <li v-for="(v, k) in analytics.summary.by_status" :key="k">
              <span>{{ k }}</span><strong>{{ v }}</strong>
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dist-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.dist-list li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
.dist-list li:last-child {
  border-bottom: none;
}
</style>
