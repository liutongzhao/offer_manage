/** 统一响应信封，与后端 ApiResponse 对齐。 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 公司（对齐 backend/app/schemas/company.py） */
export interface Company {
  id: number
  name: string
  alias: string | null
  city: string | null
  industry: string | null
  website: string | null
  created_at: string | null
}

export interface CompanyCreate {
  name: string
  alias?: string | null
  city?: string | null
  industry?: string | null
  website?: string | null
}

export type CompanyUpdate = Partial<Omit<CompanyCreate, 'name'>>

/** 投递记录（对齐 backend/app/schemas/application.py） */
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

/** 简历资产（对齐 backend/app/schemas/resume.py） */
export interface Resume {
  id: number
  company: string | null
  application_id: number | null
  filename: string
  object_key: string
  size: number | null
  content_type: string | null
  is_base: boolean
  version: string | null
  uploaded_at: string | null
}

/** 问题记录（对齐 backend/app/schemas/issue.py） */
export interface Issue {
  id: number
  title: string
  category: string
  related_application_id: number | null
  description: string | null
  solution: string | null
  tags: string | null
  recorded_date: string | null
  created_at: string | null
}

export interface IssueCreate {
  title: string
  category?: string
  related_application_id?: number | null
  description?: string | null
  solution?: string | null
  tags?: string | null
  recorded_date?: string | null
}

export type IssueUpdate = Partial<IssueCreate>

/** 看板统计（对齐 backend/app/api/analytics.py summary） */
export interface AnalyticsSummary {
  total: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  issues_total: number
}
