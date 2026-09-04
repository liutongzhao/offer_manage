import { client, unwrap } from './client'
import type { Issue, IssueCreate, IssueUpdate } from '@/types'

export function getIssues(
  params: { category?: string; related_application_id?: number } = {},
) {
  const sp = new URLSearchParams()
  if (params.category) sp.append('category', params.category)
  if (params.related_application_id != null)
    sp.append('related_application_id', String(params.related_application_id))
  const q = sp.toString()
  return unwrap<Issue[]>(client.get(`/issues${q ? `?${q}` : ''}`))
}

export const getIssue = (id: number) =>
  unwrap<Issue>(client.get(`/issues/${id}`))

export const createIssue = (data: IssueCreate) =>
  unwrap<Issue>(client.post('/issues', data))

export const updateIssue = (id: number, data: IssueUpdate) =>
  unwrap<Issue>(client.patch(`/issues/${id}`, data))

export const deleteIssue = (id: number) =>
  unwrap<unknown>(client.delete(`/issues/${id}`))
