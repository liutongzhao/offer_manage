import { client, unwrap } from './client'
import type { Resume } from '@/types'

export const getResumes = () => unwrap(client.get('/resumes'))
export const getResume = (id: number) =>
  unwrap<Resume>(client.get(`/resumes/${id}`))
export const deleteResume = (id: number) =>
  unwrap<unknown>(client.delete(`/resumes/${id}`))

/** 上传简历：multipart/form-data，与后端 upload 路由对齐。 */
export const uploadResume = (form: FormData) =>
  unwrap<Resume>(client.post('/resumes/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }))
