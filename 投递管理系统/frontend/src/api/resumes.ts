import { client, unwrap } from './client'
import type { Resume } from '@/types'

export const getResumes = () => unwrap(client.get('/resumes'))
export const deleteResume = (id: number) =>
  unwrap<unknown>(client.delete(`/resumes/${id}`))

/** 获取简历预签名访问地址（后端只提供 /{id}/url，无详情路由） */
export const getResumeUrl = (id: number) =>
  unwrap<string>(client.get(`/resumes/${id}/url`))

export interface UploadResumeParams {
  file: File
  company?: string | null
  applicationId?: number | null
  isBase?: boolean
  version?: string | null
}

/** 上传简历：multipart/form-data，字段与后端 POST /api/v1/resumes 对齐 */
export function uploadResume(params: UploadResumeParams) {
  const form = new FormData()
  form.append('file', params.file)
  if (params.company) form.append('company', params.company)
  if (params.applicationId != null)
    form.append('application_id', String(params.applicationId))
  form.append('is_base', String(params.isBase ?? false))
  if (params.version) form.append('version', params.version)
  return unwrap<Resume>(
    client.post('/resumes', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  )
}
