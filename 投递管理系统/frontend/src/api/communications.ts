import { client, unwrap } from './client'
import type { Communication, CommunicationCreate, CommunicationUpdate } from '@/types'

export const getCommunications = (applicationId: number) =>
  unwrap<Communication[]>(
    client.get(`/applications/${applicationId}/communications`),
  )

export const createCommunication = (
  applicationId: number,
  data: CommunicationCreate,
) =>
  unwrap<Communication>(
    client.post(`/applications/${applicationId}/communications`, data),
  )

export const updateCommunication = (id: number, data: CommunicationUpdate) =>
  unwrap<Communication>(client.patch(`/communications/${id}`, data))

export const deleteCommunication = (id: number) =>
  unwrap<unknown>(client.delete(`/communications/${id}`))
