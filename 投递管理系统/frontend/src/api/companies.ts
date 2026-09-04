import { client, unwrap } from './client'
import type { Company, CompanyCreate, CompanyUpdate } from '@/types'

export const getCompanies = () => unwrap(client.get('/companies'))
export const getCompany = (id: number) =>
  unwrap<Company>(client.get(`/companies/${id}`))
export const createCompany = (data: CompanyCreate) =>
  unwrap<Company>(client.post('/companies', data))
export const updateCompany = (id: number, data: CompanyUpdate) =>
  unwrap<Company>(client.patch(`/companies/${id}`, data))
export const deleteCompany = (id: number) =>
  unwrap<unknown>(client.delete(`/companies/${id}`))
