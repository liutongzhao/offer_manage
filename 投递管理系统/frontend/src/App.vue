<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

interface NavItem {
  path: string
  title: string
  icon: string
  group: string
}

const navItems: NavItem[] = [
  { path: '/', title: '投递看板', icon: 'DataLine', group: '概览' },
  { path: '/applications', title: '投递记录', icon: 'Promotion', group: '求职主线' },
  { path: '/todos', title: '待办提醒', icon: 'Bell', group: '求职主线' },
  { path: '/companies', title: '公司管理', icon: 'OfficeBuilding', group: '资产库' },
  { path: '/resumes', title: '简历资产', icon: 'Document', group: '资产库' },
  { path: '/issues', title: '问题记录', icon: 'Warning', group: '资产库' },
  { path: '/analytics', title: '数据统计', icon: 'TrendCharts', group: '分析' },
  { path: '/settings', title: '数据与设置', icon: 'Setting', group: '系统' },
]

const groups = ['概览', '求职主线', '资产库', '分析', '系统']

const activePath = computed(() => {
  // 详情页高亮「投递记录」
  if (route.path.startsWith('/applications')) return '/applications'
  return route.path
})
</script>

<template>
  <el-container class="app-shell">
    <el-aside width="212px" class="app-aside">
      <div class="app-logo">
        <el-icon><Opportunity /></el-icon>
        <span>秋招投递管理</span>
      </div>
      <nav class="app-nav">
        <template v-for="g in groups" :key="g">
          <div class="nav-group">{{ g }}</div>
          <RouterLink
            v-for="item in navItems.filter((i) => i.group === g)"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: activePath === item.path }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </RouterLink>
        </template>
      </nav>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <span class="app-crumb">{{ route.meta.title || '秋招投递管理平台' }}</span>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-shell {
  height: 100%;
}

.app-aside {
  background: var(--color-gray-900);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.app-logo {
  height: 56px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #fff;
  font-weight: 600;
  font-size: var(--fs-h3);
  letter-spacing: 1px;
  background: #1d2939;
}

.app-nav {
  padding: var(--sp-3) var(--sp-2);
}

.nav-group {
  font-size: 11px;
  color: #667085;
  text-transform: uppercase;
  padding: var(--sp-3) var(--sp-2) var(--sp-1);
  letter-spacing: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  height: 38px;
  padding: 0 var(--sp-2);
  border-radius: var(--radius-sm);
  color: #cbd5e1;
  font-size: var(--fs-body);
  transition: all 120ms ease-out;
  margin-bottom: 2px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.nav-item.active {
  background: var(--color-primary-500);
  color: #fff;
  font-weight: 500;
}

.app-header {
  display: flex;
  align-items: center;
  height: 56px;
  background: var(--color-gray-0);
  border-bottom: 1px solid var(--color-gray-200);
}

.app-crumb {
  font-size: var(--fs-h3);
  font-weight: 600;
  color: var(--color-gray-900);
}

.app-main {
  padding: var(--sp-6);
  background: var(--color-gray-50);
  overflow-y: auto;
}
</style>
