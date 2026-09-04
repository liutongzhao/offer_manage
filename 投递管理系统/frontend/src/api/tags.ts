import { client, unwrap } from './client'
import type { Tag } from '@/types'

export const getTags = () => unwrap<Tag[]>(client.get('/tags'))

export const createTag = (name: string, color?: string) =>
  unwrap<Tag>(client.post('/tags', { name, color: color ?? null }))

/** 重命名标签（标签管理，REQ-TAG-002） */
export const renameTag = (id: number, name: string) =>
  unwrap<Tag>(client.patch(`/tags/${id}`, { name }))

/** 删除标签（自动解绑，不影响已关联记录） */
export const deleteTag = (id: number) =>
  unwrap<unknown>(client.delete(`/tags/${id}`))
