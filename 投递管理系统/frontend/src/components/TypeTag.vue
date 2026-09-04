<script setup lang="ts">
import { computed } from 'vue'
import { TYPE_MAP } from '@/constants/enums'

/** 类型标签（UI-CP-010）：后端=蓝 / 测试=青 / AI=紫 */
const props = defineProps<{ type: string }>()

const meta = computed(() => TYPE_MAP[props.type] ?? {
  value: props.type,
  solid: 'var(--color-gray-400)',
  bg: 'var(--color-gray-100)',
  text: 'var(--color-gray-600)',
})
</script>

<template>
  <span class="type-tag" :style="{ background: meta.bg, color: meta.text }">
    <i class="dot" :style="{ background: meta.solid }" />
    {{ meta.value }}
  </span>
</template>

<style scoped>
.type-tag {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 8px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 5px;
}
</style>
