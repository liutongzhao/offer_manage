<script setup lang="ts">
import { ref, watch } from 'vue'

/** 图片灯箱（PG-017）：全屏黑底、左右切换、计数器、Esc 关闭 */
const props = defineProps<{
  visible: boolean
  urls: string[]
  index: number
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'update:index', v: number): void
}>()

const current = ref(props.index)
watch(
  () => props.visible,
  (v) => {
    if (v) current.value = props.index
  },
)
watch(
  () => props.index,
  (v) => {
    current.value = v
  },
)

function close() {
  emit('update:visible', false)
}

function prev() {
  if (current.value > 0) emit('update:index', current.value - 1)
}

function next() {
  if (current.value < props.urls.length - 1) emit('update:index', current.value + 1)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowLeft') prev()
  if (e.key === 'ArrowRight') next()
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="lightbox-mask" tabindex="0" @click.self="close" @keydown="onKeydown">
      <span v-if="current > 0" class="nav-btn left" @click="prev">‹</span>
      <img class="lightbox-img" :src="urls[current]" alt="附件预览" @click.stop />
      <span v-if="current < urls.length - 1" class="nav-btn right" @click="next">›</span>
      <div class="lightbox-counter num">{{ current + 1 }} / {{ urls.length }}</div>
      <span class="close-btn" @click="close">✕</span>
    </div>
  </Teleport>
</template>

<style scoped>
.lightbox-mask {
  position: fixed;
  inset: 0;
  background: rgba(16, 24, 40, 0.8);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-img {
  max-width: 86vw;
  max-height: 86vh;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xl);
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 48px;
  color: #fff;
  cursor: pointer;
  user-select: none;
  padding: 0 20px;
  line-height: 1;
}

.nav-btn.left {
  left: 12px;
}

.nav-btn.right {
  right: 12px;
}

.lightbox-counter {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  font-size: var(--fs-sm);
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 28px;
  color: #fff;
  font-size: 22px;
  cursor: pointer;
}
</style>
