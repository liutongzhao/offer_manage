import { client, unwrap } from './client'
import type { BackupInfo, ImportResult } from '@/types'

/** 导入 CSV（浏览器下载由 api/applications.ts exportUrl + window.open 完成） */

export function importApplications(file: File) {
  const form = new FormData()
  form.append('file', file)
  return unwrap<ImportResult>(
    client.post('/data/import/applications', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  )
}

/** 立即备份 SQLite 库文件到 MinIO */
export const backupDatabase = () =>
  unwrap<BackupInfo>(client.post('/data/backup'))

/** 备份列表 */
export const getBackups = () => unwrap<BackupInfo[]>(client.get('/data/backups'))

/** 从备份恢复（覆盖本地库，恢复后需重启后端） */
export const restoreDatabase = (objectKey: string) =>
  unwrap<{ restored: boolean; object_key: string; message: string }>(
    client.post('/data/restore', { object_key: objectKey }),
  )
