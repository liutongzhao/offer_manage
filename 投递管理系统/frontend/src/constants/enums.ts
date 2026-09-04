/**
 * 枚举单点定义（REQ-NFR-013）：状态/类型/渠道/附件类型等
 * 与后端 app/core/constants.py 保持一致，颜色引用 tokens.css 变量。
 */

export interface StatusMeta {
  value: string
  key: string
  dot: string
  bg: string
  text: string
}

/** 投递状态 8 态（顺序即看板列顺序） */
export const STATUS_LIST: StatusMeta[] = [
  { value: '待投递', key: 'pending', dot: 'var(--status-pending-dot)', bg: 'var(--status-pending-bg)', text: 'var(--status-pending-text)' },
  { value: '已投递', key: 'applied', dot: 'var(--status-applied-dot)', bg: 'var(--status-applied-bg)', text: 'var(--status-applied-text)' },
  { value: '笔试中', key: 'written', dot: 'var(--status-written-dot)', bg: 'var(--status-written-bg)', text: 'var(--status-written-text)' },
  { value: '面试中', key: 'interviewing', dot: 'var(--status-interviewing-dot)', bg: 'var(--status-interviewing-bg)', text: 'var(--status-interviewing-text)' },
  { value: '已Offer', key: 'offered', dot: 'var(--status-offered-dot)', bg: 'var(--status-offered-bg)', text: 'var(--status-offered-text)' },
  { value: '已挂', key: 'failed', dot: 'var(--status-failed-dot)', bg: 'var(--status-failed-bg)', text: 'var(--status-failed-text)' },
  { value: '已拒绝', key: 'declined', dot: 'var(--status-declined-dot)', bg: 'var(--status-declined-bg)', text: 'var(--status-declined-text)' },
  { value: '爽约', key: 'noshow', dot: 'var(--status-noshow-dot)', bg: 'var(--status-noshow-bg)', text: 'var(--status-noshow-text)' },
]

export const STATUS_MAP: Record<string, StatusMeta> = Object.fromEntries(
  STATUS_LIST.map((s) => [s.value, s]),
)

export const TERMINAL_STATUSES = ['已Offer', '已挂', '已拒绝', '爽约']

export interface TypeMeta {
  value: string
  solid: string
  bg: string
  text: string
}

/** 投递类型 3 类 */
export const TYPE_LIST: TypeMeta[] = [
  { value: '后端开发', solid: 'var(--color-primary-500)', bg: 'var(--color-primary-100)', text: 'var(--color-primary-600)' },
  { value: '测试开发', solid: 'var(--color-teal-400)', bg: 'var(--color-teal-50)', text: 'var(--color-teal-700)' },
  { value: 'AI开发', solid: 'var(--color-violet-400)', bg: 'var(--color-violet-50)', text: 'var(--color-violet-700)' },
]

export const TYPE_MAP: Record<string, TypeMeta> = Object.fromEntries(
  TYPE_LIST.map((t) => [t.value, t]),
)

export const CHANNELS = ['官网', '内推', '招聘平台', '邮箱', '宣讲会', '其他']

export const ISSUE_CATEGORIES = ['面试', '笔试', '流程', '技术', 'HR', '其他']

export const ISSUE_MASTERY = ['已掌握', '待复习', '仍不会']

export const MASTERY_COLOR: Record<string, string> = {
  已掌握: 'var(--color-success-solid)',
  待复习: 'var(--color-warning-solid)',
  仍不会: 'var(--color-error-solid)',
}

export const COMMUNICATION_METHODS = ['微信', '电话', '邮件', '现场', '平台消息', '其他']

export const LINK_TYPES = ['投递入口', 'JD详情', '笔试链接', '公司官网', '其他']

export const ATTACHMENT_TYPES = ['简历', 'JD截图', '笔试', 'offer', '聊天记录', '证明材料', '其他']

export const COMPANY_SCALES = ['大厂', '中厂', '初创', '其他']

/** 时间线事件类型色（界面设计方案 §4.3 EventTimeline） */
export const EVENT_KIND_META: Record<string, { label: string; color: string }> = {
  status: { label: '状态变更', color: 'var(--color-primary-500)' },
  field: { label: '字段变更', color: 'var(--color-gray-500)' },
  create: { label: '创建记录', color: 'var(--color-primary-500)' },
  communication: { label: '沟通记录', color: 'var(--color-violet-400)' },
  attachment: { label: '附件上传', color: 'var(--color-teal-400)' },
  resume: { label: '简历', color: 'var(--color-teal-400)' },
  issue: { label: '问题记录', color: 'var(--color-amber-400)' },
}
