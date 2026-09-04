"""枚举常量集中定义，避免散落硬编码（REQ-NFR-013）。"""

APPLICATION_TYPES = ["后端开发", "测试开发", "AI开发"]

# 顺序即看板列顺序，也是漏斗阶梯的参考顺序
APPLICATION_STATUSES = [
    "待投递",
    "已投递",
    "笔试中",
    "面试中",
    "已Offer",
    "已挂",
    "已拒绝",
    "爽约",
]

# 终态：不再参与待办提醒
TERMINAL_STATUSES = ["已Offer", "已挂", "已拒绝", "爽约"]

CHANNELS = ["官网", "内推", "招聘平台", "邮箱", "宣讲会", "其他"]

ISSUE_CATEGORIES = ["面试", "笔试", "流程", "技术", "HR", "其他"]

ISSUE_MASTERY = ["已掌握", "待复习", "仍不会"]

COMMUNICATION_METHODS = ["微信", "电话", "邮件", "现场", "平台消息", "其他"]

LINK_TYPES = ["投递入口", "JD详情", "笔试链接", "公司官网", "其他"]

ATTACHMENT_TYPES = ["简历", "JD截图", "笔试", "offer", "聊天记录", "证明材料", "其他"]

EVENT_TYPES = ["状态变更", "字段变更", "创建记录"]

EVENT_SOURCES = ["代理录入", "用户操作", "系统自动"]

TAG_SCOPES = ["投递", "问题", "公司"]

COMPANY_SCALES = ["大厂", "中厂", "初创", "其他"]

# 需要留痕的投递字段：属性名 -> 中文展示名（REQ-TRC-005 全字段留痕）
FIELD_LABELS = {
    "type": "投递类型",
    "position": "岗位名称",
    "status": "当前状态",
    "channel": "投递渠道",
    "apply_date": "投递日期",
    "city": "工作城市",
    "jd_url": "JD链接",
    "resume_id": "关联简历",
    "requirements": "招聘要求",
    "tailor_notes": "针对性修改说明",
    "referrer": "内推人",
    "salary": "薪资范围",
    "deadline": "截止日期",
    "notes": "备注",
    "result_date": "结果日期",
    "interview_stage": "面试轮次",
    "archived": "归档状态",
}

# 导入/导出 CSV 列（中文表头 -> 属性名），顺序即导出列顺序
CSV_COLUMNS = [
    ("公司名称", "company_name"),
    ("投递类型", "type"),
    ("岗位名称", "position"),
    ("当前状态", "status"),
    ("投递渠道", "channel"),
    ("工作城市", "city"),
    ("投递日期", "apply_date"),
    ("截止日期", "deadline"),
    ("面试轮次", "interview_stage"),
    ("结果日期", "result_date"),
    ("薪资范围", "salary"),
    ("内推人", "referrer"),
    ("标签", "tags"),
    ("备注", "notes"),
]
