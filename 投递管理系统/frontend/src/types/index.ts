/** 统一响应信封，与后端 ApiResponse 对齐。 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/** 分页数据，与后端 ApplicationListData 对齐。 */
export interface PageData<T> {
  total: number
  items: T[]
}

/** 公司 */
export interface Company {
  id: number
  name: string
  alias: string | null
  city: string | null
  industry: string | null
  scale: string | null
  website: string | null
  notes: string | null
  created_at: string | null
}

export interface CompanyWithCount extends Company {
  application_count: number
}

export interface CompanyCreate {
  name: string
  alias?: string | null
  city?: string | null
  industry?: string | null
  scale?: string | null
  website?: string | null
  notes?: string | null
}

export type CompanyUpdate = Partial<CompanyCreate>

/** 投递记录（对齐 backend/app/schemas/application.py） */
export interface Application {
  id: number
  company_id: number
  company_name: string | null
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
  interview_stage: string | null
  result_date: string | null
  notes: string | null
  archived: boolean
  tag_names: string[]
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
  interview_stage?: string | null
  result_date?: string | null
  notes?: string | null
  tag_names?: string[]
}

export type ApplicationUpdate = Partial<ApplicationCreate> & {
  /** 归档状态（仅更新接口支持） */
  archived?: boolean
}

/** 投递列表筛选参数 */
export interface ApplicationFilters {
  type?: string
  status?: string
  channel?: string
  city?: string
  company_id?: number
  keyword?: string
  tag?: string
  apply_date_from?: string
  apply_date_to?: string
  deadline_from?: string
  deadline_to?: string
  archived?: boolean
  include_deleted?: boolean
  sort_by?: string
  order?: string
  skip?: number
  limit?: number
}

/** 统一时间线条目（对齐 backend TimelineItem） */
export interface TimelineItem {
  kind: 'status' | 'field' | 'create' | 'communication' | 'attachment' | 'resume' | 'issue'
  time: string
  id: number | null
  application_id: number | null
  event_type?: string | null
  field_name?: string | null
  old_value?: string | null
  new_value?: string | null
  source?: string | null
  contact?: string | null
  method?: string | null
  content?: string | null
  my_action?: string | null
  filename?: string | null
  att_type?: string | null
  title?: string | null
  description?: string | null
}

/** 简历资产 */
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

/** 问题记录 */
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

/** 沟通记录 */
export interface Communication {
  id: number
  application_id: number
  contact: string | null
  method: string
  content: string
  my_action: string | null
  occurred_at: string | null
  created_at: string | null
}

export interface CommunicationCreate {
  content: string
  contact?: string | null
  method?: string
  my_action?: string | null
  occurred_at?: string | null
}

export type CommunicationUpdate = Partial<CommunicationCreate>

/** 投递链接 */
export interface ApplicationLink {
  id: number
  application_id: number
  name: string
  url: string
  link_type: string
  is_invalid: boolean
  created_at: string | null
}

export interface LinkCreate {
  url: string
  name?: string | null
  link_type?: string
}

export interface LinkUpdate {
  url?: string
  name?: string | null
  link_type?: string
  is_invalid?: boolean
}

/** 附件 */
export interface Attachment {
  id: number
  application_id: number
  filename: string
  object_key: string
  size: number | null
  content_type: string | null
  att_type: string
  uploaded_at: string | null
}

/** 标签 */
export interface Tag {
  id: number
  name: string
  scope: string
  color: string | null
  usage_count?: number
}

/** 统计（对齐 backend SummaryOut） */
export interface AnalyticsSummary {
  total: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  by_channel: Record<string, number>
  issues_total: number
  week_count: number
  interviewing: number
  offered: number
  conversion_rate: number
}

export interface FunnelStage {
  stage: string
  count: number
  percent: number
}

export interface TrendPoint {
  period: string
  count: number
}

export interface TodoItem {
  application_id: number
  company_name: string | null
  position: string
  status: string
  deadline: string
  days_left: number
}

export interface TodosOut {
  expired: TodoItem[]
  due_soon: TodoItem[]
}

export interface RecentEventItem {
  kind: string
  time: string
  application_id: number
  company_name: string | null
  position: string | null
  summary: string
}

export interface ImportFailure {
  row: number
  error: string
}

export interface ImportResult {
  success_count: number
  fail_count: number
  failures: ImportFailure[]
}

export interface BackupInfo {
  object_key: string
  size: number | null
  last_modified: string | null
}
