<script setup lang="ts">
import { computed } from 'vue'
import { STATUS_MAP, STATUS_LIST } from '@/constants/enums'

/**
 * 状态标签（UI-CP-009 核心组件）：
 * 浅底深字 + 左侧色点双编码，规格见界面设计方案 §4.3。
 */
const props = withDefaults(
  defineProps<{
    status: string
    size?: 'M' | 'S'
    selectable?: boolean
    selected?: boolean
  }>(),
  { size: 'M', selectable: false, selected: false },
)

const meta = computed(() => STATUS_MAP[props.status] ?? {
  value: props.status,
  key: 'unknown',
  dot: 'var(--color-gray-400)',
  bg: 'var(--color-gray-100)',
  text: 'var(--color-gray-600)',
})

const emit = defineEmits<{ (e: 'select', status: string): void }>()

function onClick() {
  if (props.selectable) emit('select', props.status)
}

const statusOptions = STATUS_LIST
</script>

<template>
  <span
    class="status-tag"
    :class="[`status-tag--${meta.key}`, size, { selectable, selected }]"
    :style="{ background: meta.bg, color: meta.text }"
    @click.stop="onClick"
  >
    <i class="status-tag__dot" :style="{ background: meta.dot }" />
    <span class="status-tag__text">{{ meta.value }}</span>
  </span>
</template>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 8px;
  border-radius: var(--radius-full);
  border: 1px solid transparent;
  white-space: nowrap;
  transition: all 120ms ease-out;
  vertical-align: middle;
}

.status-tag.S {
  height: 20px;
  padding: 0 6px;
}

.status-tag__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 6px;
  flex-shrink: 0;
}

.status-tag__text {
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
}

.status-tag.S .status-tag__text {
  font-weight: 400;
}

.status-tag.selectable {
  cursor: pointer;
}

.status-tag.selectable:hover {
  filter: brightness(0.97);
}

.status-tag.selected {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 1px var(--color-primary-500);
}
</style>
