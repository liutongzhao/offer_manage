import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: '投递看板' },
  },
  {
    path: '/applications',
    name: 'applications',
    component: () => import('@/views/ApplicationsView.vue'),
    meta: { title: '投递记录' },
  },
  {
    path: '/applications/:id',
    name: 'applicationDetail',
    component: () => import('@/views/ApplicationDetailView.vue'),
    meta: { title: '投递详情' },
  },
  {
    path: '/todos',
    name: 'todos',
    component: () => import('@/views/TodoView.vue'),
    meta: { title: '待办提醒' },
  },
  {
    path: '/companies',
    name: 'companies',
    component: () => import('@/views/CompaniesView.vue'),
    meta: { title: '公司管理' },
  },
  {
    path: '/resumes',
    name: 'resumes',
    component: () => import('@/views/ResumeLibraryView.vue'),
    meta: { title: '简历资产' },
  },
  {
    path: '/issues',
    name: 'issues',
    component: () => import('@/views/IssuesView.vue'),
    meta: { title: '问题记录' },
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('@/views/AnalyticsView.vue'),
    meta: { title: '数据统计' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { title: '数据与设置' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
