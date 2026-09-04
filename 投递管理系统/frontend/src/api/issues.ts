import { client, unwrap } from './client'
import type { Issue, IssueCreate, IssueUpdate } from '@/types'

export const getIssues = () => unwrap(client.get('/issues'))
export const getIssue = (id: number) =>
  unwrap<Issue>(client.get(`/issues/${id}`))
export const createIssue = (data: IssueCreate) =>
  unwrap<Issue>(client.post('/issues', data))
export const updateIssue = (id: number, data: IssueUpdate) =>
  unwrap<Issue>(client.patch(`/issues/${id}`, data))
export const deleteIssue = (id: number) =>
  unwrap<unknown>(client.delete(`/issues/${id}`))
