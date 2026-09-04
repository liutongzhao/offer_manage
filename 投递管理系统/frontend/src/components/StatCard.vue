<script setup lang="ts">
/** 统计卡（UI-CP-013）：左侧 4px 语义色条 + 大数字 */
defineProps<{
  label: string
  value: number | string
  hint?: string
  color?: string
}>()
</script>

<template>
  <div class="stat-card" :style="{ '--bar': color || 'var(--color-primary-500)' }">
    <div class="stat-value num">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="hint" class="stat-hint">{{ hint }}</div>
  </div>
</template>

<style scoped>
.stat-card {
  background: var(--color-gray-0);
  border: var(--border-base);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xs);
  padding: var(--sp-4) var(--sp-5);
  height: 108px;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--bar);
}

.stat-value {
  font-size: var(--fs-display);
  line-height: 38px;
  font-weight: 600;
  color: var(--color-gray-900);
}

.stat-label {
  margin-top: 4px;
  font-size: var(--fs-body);
  color: var(--color-gray-600);
}

.stat-hint {
  margin-top: 2px;
  font-size: var(--fs-xs);
  color: var(--color-gray-500);
}
</style>
