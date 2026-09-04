<script setup lang="ts">
import { onMounted } from 'vue'
import { useIssuesStore } from '@/stores/issues'

const store = useIssuesStore()

onMounted(() => {
  store.fetchAll()
})
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="head">
        <span>问题记录</span>
        <el-button type="primary" size="small">新增问题</el-button>
      </div>
    </template>
    <el-table :data="store.items" v-loading="store.loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="related_application_id" label="关联投递" width="110" />
      <el-table-column
        prop="description"
        label="描述"
        min-width="200"
        show-overflow-tooltip
      />
      <el-table-column
        prop="solution"
        label="解决办法"
        min-width="180"
        show-overflow-tooltip
      />
      <el-table-column prop="tags" label="标签" width="140" />
      <el-table-column prop="recorded_date" label="记录日期" width="120" />
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
