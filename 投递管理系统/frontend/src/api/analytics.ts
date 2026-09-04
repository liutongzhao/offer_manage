import { client, unwrap } from './client'
import type {
  AnalyticsSummary,
  FunnelStage,
  RecentEventItem,
  TodosOut,
  TrendPoint,
} from '@/types'

export const getSummary = () =>
  unwrap<AnalyticsSummary>(client.get('/analytics/summary'))

export const getFunnel = () =>
  unwrap<{ stages: FunnelStage[] }>(client.get('/analytics/funnel'))

export const getTrend = (granularity: 'week' | 'month', months = 6) =>
  unwrap<TrendPoint[]>(
    client.get(`/analytics/trend?granularity=${granularity}&months=${months}`),
  )

export const getTodos = () => unwrap<TodosOut>(client.get('/analytics/todos'))

export const getRecentEvents = (limit = 10) =>
  unwrap<RecentEventItem[]>(client.get(`/analytics/recent-events?limit=${limit}`))
