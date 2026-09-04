<script setup lang="ts">
defineProps<{
  label: string
  value: number | string
  hint?: string
}>()
</script>

<template>
  <el-card class="stat-card" shadow="hover">
    <div class="stat-value">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="hint" class="stat-hint">{{ hint }}</div>
  </el-card>
</template>

<style scoped>
.stat-card {
  border-radius: 10px;
}
.stat-value {
  font-size: 30px;
  font-weight: 700;
  color: var(--brand);
  line-height: 1.1;
}
.stat-label {
  margin-top: 6px;
  font-size: 14px;
  color: #4b5563;
}
.stat-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #9ca3af;
}
</style>
