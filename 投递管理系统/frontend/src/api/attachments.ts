import { client, unwrap } from './client'
import type { Attachment } from '@/types'

export const getAttachments = (applicationId: number) =>
  unwrap<Attachment[]>(
    client.get(`/applications/${applicationId}/attachments`),
  )

export interface UploadAttachmentParams {
  applicationId: number
  file: File
  attType?: string
}

/** 上传附件：multipart/form-data，字段与后端对齐 */
export function uploadAttachment(params: UploadAttachmentParams) {
  const form = new FormData()
  form.append('file', params.file)
  if (params.attType) form.append('att_type', params.attType)
  return unwrap<Attachment>(
    client.post(`/applications/${params.applicationId}/attachments`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  )
}

/** 获取附件预签名访问地址 */
export const getAttachmentUrl = (id: number) =>
  unwrap<string>(client.get(`/attachments/${id}/url`))

/** 修改附件类型标注 */
export const updateAttachmentType = (id: number, attType: string) =>
  unwrap<Attachment>(client.patch(`/attachments/${id}`, { att_type: attType }))

export const deleteAttachment = (id: number) =>
  unwrap<unknown>(client.delete(`/attachments/${id}`))
