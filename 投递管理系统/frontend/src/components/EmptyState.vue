<script setup lang="ts">
/** 空状态组件（UI-CP-022）：插图 + 主文案 + 副文案 + 行动按钮 */
defineProps<{
  title: string
  description?: string
  actionText?: string
  icon?: string
}>()

const emit = defineEmits<{ (e: 'action'): void }>()
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="48">
        <component :is="icon || 'Inbox'" />
      </el-icon>
    </div>
    <div class="empty-title">{{ title }}</div>
    <div v-if="description" class="empty-desc">{{ description }}</div>
    <el-button
      v-if="actionText"
      type="primary"
      class="empty-action"
      @click="emit('action')"
    >
      {{ actionText }}
    </el-button>
    <slot />
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64px 24px 48px;
  text-align: center;
}

.empty-icon {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: var(--color-primary-50);
  color: var(--color-primary-500);
  opacity: 0.85;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--sp-4);
}

.empty-title {
  font-size: var(--fs-h3);
  font-weight: 600;
  color: var(--color-gray-800);
}

.empty-desc {
  margin-top: var(--sp-2);
  font-size: var(--fs-body);
  color: var(--color-gray-500);
  max-width: 360px;
}

.empty-action {
  margin-top: var(--sp-5);
}
</style>
