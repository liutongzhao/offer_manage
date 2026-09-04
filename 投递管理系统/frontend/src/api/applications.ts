import { client, unwrap } from './client'
import type {
  Application,
  ApplicationCreate,
  ApplicationFilters,
  ApplicationUpdate,
  PageData,
  TimelineItem,
} from '@/types'

/** 构造查询串（跳过空值） */
function qs(params: Record<string, unknown>): string {
  const sp = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') sp.append(k, String(v))
  }
  const s = sp.toString()
  return s ? `?${s}` : ''
}

export function getApplications(filters: ApplicationFilters = {}) {
  return unwrap<PageData<Application>>(
    client.get(`/applications${qs(filters as Record<string, unknown>)}`),
  )
}

export const getApplication = (id: number) =>
  unwrap<Application>(client.get(`/applications/${id}`))

export const createApplication = (data: ApplicationCreate) =>
  unwrap<Application>(client.post('/applications', data))

export const updateApplication = (id: number, data: ApplicationUpdate) =>
  unwrap<Application>(client.patch(`/applications/${id}`, data))

export const deleteApplication = (id: number) =>
  unwrap<unknown>(client.delete(`/applications/${id}`))

export const restoreApplication = (id: number) =>
  unwrap<Application>(client.post(`/applications/${id}/restore`))

/** 整体替换投递标签（自由输入，自动建档） */
export const setApplicationTags = (id: number, names: string[]) =>
  unwrap<Application>(client.put(`/applications/${id}/tags`, { names }))

/** 统一时间线（状态事件+沟通+附件+简历+问题混排） */
export const getTimeline = (id: number, kind?: string) =>
  unwrap<TimelineItem[]>(
    client.get(`/applications/${id}/timeline${kind ? `?kind=${kind}` : ''}`),
  )

/** 导出投递明细 CSV（当前筛选条件随 URL 传递，浏览器直接下载） */
export function exportUrl(filters: ApplicationFilters): string {
  return `/api/v1/data/export/applications.csv${qs(filters as Record<string, unknown>)}`
}
