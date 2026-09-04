import { client, unwrap } from './client'
import type { Company, CompanyCreate, CompanyUpdate, CompanyWithCount } from '@/types'

export function getCompanies(params: { keyword?: string; with_count?: boolean } = {}) {
  const sp = new URLSearchParams()
  if (params.keyword) sp.append('keyword', params.keyword)
  if (params.with_count !== undefined) sp.append('with_count', String(params.with_count))
  const q = sp.toString()
  return unwrap<CompanyWithCount[] | Company[]>(
    client.get(`/companies${q ? `?${q}` : ''}`),
  )
}

export const getCompany = (id: number) =>
  unwrap<Company>(client.get(`/companies/${id}`))

export const createCompany = (data: CompanyCreate) =>
  unwrap<Company>(client.post('/companies', data))

export const updateCompany = (id: number, data: CompanyUpdate) =>
  unwrap<Company>(client.patch(`/companies/${id}`, data))

export const deleteCompany = (id: number) =>
  unwrap<unknown>(client.delete(`/companies/${id}`))
