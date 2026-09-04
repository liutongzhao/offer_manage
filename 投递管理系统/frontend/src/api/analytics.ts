import { client, unwrap } from './client'
import type { AnalyticsSummary } from '@/types'

export const getSummary = () =>
  unwrap<AnalyticsSummary>(client.get('/analytics/summary'))
