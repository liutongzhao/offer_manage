<script setup lang="ts">
import { onMounted } from 'vue'
import { useCompaniesStore } from '@/stores/companies'

const store = useCompaniesStore()

onMounted(() => {
  store.fetchAll()
})
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="head">
        <span>公司管理</span>
        <el-button type="primary" size="small">新增公司</el-button>
      </div>
    </template>
    <el-table :data="store.items" v-loading="store.loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="公司名称" min-width="160" />
      <el-table-column prop="city" label="城市" width="110" />
      <el-table-column prop="industry" label="行业" width="140" />
      <el-table-column prop="note" label="备注" min-width="160" show-overflow-tooltip />
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
