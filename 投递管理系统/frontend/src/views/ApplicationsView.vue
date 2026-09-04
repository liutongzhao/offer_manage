<script setup lang="ts">
import { onMounted } from 'vue'
import { useApplicationsStore } from '@/stores/applications'

const store = useApplicationsStore()

onMounted(() => {
  store.fetchAll()
})
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="head">
        <span>投递记录</span>
        <el-button type="primary" size="small">新增投递</el-button>
      </div>
    </template>
    <el-table :data="store.items" v-loading="store.loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="company_id" label="公司ID" width="90" />
      <el-table-column prop="type" label="类型" width="110" />
      <el-table-column prop="position" label="岗位" min-width="160" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column prop="channel" label="渠道" width="110" />
      <el-table-column prop="city" label="城市" width="100" />
      <el-table-column prop="deadline" label="截止" width="120" />
    </el-table>
  </el-card>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
