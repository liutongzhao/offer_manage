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
    path: '/companies',
    name: 'companies',
    component: () => import('@/views/CompaniesView.vue'),
    meta: { title: '公司管理' },
  },
  {
    path: '/applications',
    name: 'applications',
    component: () => import('@/views/ApplicationsView.vue'),
    meta: { title: '投递记录' },
  },
  {
    path: '/issues',
    name: 'issues',
    component: () => import('@/views/IssuesView.vue'),
    meta: { title: '问题记录' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
