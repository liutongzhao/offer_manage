/** 统一响应信封，与后端 ApiResponse 对齐。 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 公司 */
export interface Company {
  id: number
  name: string
  city: string | null
  website: string | null
  industry: string | null
  size: string | null
  note: string | null
  created_at: string | null
  updated_at: string | null
}

export interface CompanyCreate {
  name: string
  city?: string | null
  website?: string | null
  industry?: string | null
  size?: string | null
  note?: string | null
}

export type CompanyUpdate = Partial<CompanyCreate>

/** 投递记录 */
export interface Application {
  id: number
  company_id: number
  type: string
  position: string
  status: string
  channel: string | null
  apply_date: string | null
  city: string | null
  jd_url: string | null
  resume_id: number | null
  requirements: string | null
  tailor_notes: string | null
  referrer: string | null
  salary: string | null
  deadline: string | null
  notes: string | null
  created_at: string | null
  updated_at: string | null
}

export interface ApplicationCreate {
  company_id: number
  type: string
  position: string
  status?: string
  channel?: string | null
  apply_date?: string | null
  city?: string | null
  jd_url?: string | null
  resume_id?: number | null
  requirements?: string | null
  tailor_notes?: string | null
  referrer?: string | null
  salary?: string | null
  deadline?: string | null
  notes?: string | null
}

export type ApplicationUpdate = Partial<ApplicationCreate>

/** 简历文件 */
export interface Resume {
  id: number
  company_id: number | null
  application_id: number | null
  file_name: string
  original_name: string
  object_key: string
  file_url: string | null
  file_size: number | null
  content_type: string | null
  version: string | null
  note: string | null
  uploaded_at: string | null
}

/** 问题记录 */
export interface Issue {
  id: number
  application_id: number | null
  title: string
  category: string
  content: string | null
  status: string
  resolved_at: string | null
  created_at: string | null
  updated_at: string | null
}

export interface IssueCreate {
  application_id?: number | null
  title: string
  category: string
  content?: string | null
  status?: string
}

export type IssueUpdate = Partial<IssueCreate> & { resolved_at?: string | null }

/** 看板统计 */
export interface AnalyticsSummary {
  total: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  issues_total: number
}
