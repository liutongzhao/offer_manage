import { client, unwrap } from './client'
import type { Application, ApplicationCreate, ApplicationUpdate } from '@/types'

export const getApplications = () => unwrap(client.get('/applications'))
export const getApplication = (id: number) =>
  unwrap<Application>(client.get(`/applications/${id}`))
export const createApplication = (data: ApplicationCreate) =>
  unwrap<Application>(client.post('/applications', data))
export const updateApplication = (id: number, data: ApplicationUpdate) =>
  unwrap<Application>(client.put(`/applications/${id}`, data))
export const deleteApplication = (id: number) =>
  unwrap<unknown>(client.delete(`/applications/${id}`))
