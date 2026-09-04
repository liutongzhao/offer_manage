import { client, unwrap } from './client'
import type { ApplicationLink, LinkCreate, LinkUpdate } from '@/types'

export const getLinks = (applicationId: number) =>
  unwrap<ApplicationLink[]>(client.get(`/applications/${applicationId}/links`))

export const createLink = (applicationId: number, data: LinkCreate) =>
  unwrap<ApplicationLink>(
    client.post(`/applications/${applicationId}/links`, data),
  )

export const updateLink = (id: number, data: LinkUpdate) =>
  unwrap<ApplicationLink>(client.patch(`/links/${id}`, data))

export const deleteLink = (id: number) =>
  unwrap<unknown>(client.delete(`/links/${id}`))
