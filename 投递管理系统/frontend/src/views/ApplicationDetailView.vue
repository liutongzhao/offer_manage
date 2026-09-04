<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type {
  Application,
  ApplicationLink,
  Attachment,
  Issue,
  Resume,
  TimelineItem,
} from '@/types'
import { getApplication, getTimeline, updateApplication } from '@/api/applications'
import { getCommunications, createCommunication } from '@/api/communications'
import { getAttachments } from '@/api/attachments'
import { getResumes, getResumeUrl, updateResume } from '@/api/resumes'
import { getIssues } from '@/api/issues'
import { setApplicationTags } from '@/api/applications'
import { COMMUNICATION_METHODS, LINK_TYPES, STATUS_LIST, TERMINAL_STATUSES } from '@/constants/enums'
import StatusTag from '@/components/StatusTag.vue'
import TypeTag from '@/components/TypeTag.vue'
import EventTimeline from '@/components/EventTimeline.vue'
import LinkGroup from '@/components/LinkGroup.vue'
import AttachmentWall from '@/components/AttachmentWall.vue'
import ApplicationFormDrawer from '@/components/ApplicationFormDrawer.vue'
import IssueFormDrawer from '@/components/IssueFormDrawer.vue'
import { formatDateTime } from '@/utils/format'
import { getLinks } from '@/api/links'

/** 投递详情（PG-003 核心价值页）：全字段 + 时间线 + 状态卡 + 素材区 */
const route = useRoute()
const router = useRouter()

const appId = computed(() => Number(route.params.id))
const app = ref<Application | null>(null)
const timeline = ref<TimelineItem[]>([])
const links = ref<ApplicationLink[]>([])
const attachments = ref<Attachment[]>([])
const resumes = ref<Resume[]>([])
const allResumes = ref<Resume[]>([])
const linkResumeId = ref<number | null>(null)
const relatedIssues = ref<Issue[]>([])
const loading = ref(true)
const notFound = ref(false)

async function loadAll() {
  loading.value = true
  notFound.value = false
  try {
    app.value = await getApplication(appId.value)
    const [tl, ls, atts, iss] = await Promise.all([
      getTimeline(appId.value),
      getLinks(appId.value),
      getAttachments(appId.value),
      getIssues({ related_application_id: appId.value }),
    ])
    timeline.value = tl
    links.value = ls
    attachments.value = atts
    relatedIssues.value = iss as Issue[]
    // 全部简历资产（用于展示本投递关联项 + 关联选择器）
    allResumes.value = await getResumes()
    resumes.value = allResumes.value.filter((r) => r.application_id === appId.value)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
watch(appId, () => {
  if (route.name === 'applicationDetail') loadAll()
})

/* 状态变更（含终态补充信息） */
const statusDropdownVisible = ref(false)

async function changeStatus(status: string) {
  if (!app.value || app.value.status === status) return
  try {
    await updateApplication(app.value.id, { status })
    ElMessage.success(
      TERMINAL_STATUSES.includes(status) ? `已更新为：${status}（已记录结果）` : `已更新为：${status}`,
    )
    loadAll()
  } catch {
    /* 拦截器已提示 */
  }
}

/* 沟通记录内联表单 */
const commFormVisible = ref(false)
const commForm = ref({
  content: '',
  contact: '',
  method: '微信',
  my_action: '',
  occurred_at: '' as string | null,
})
const savingComm = ref(false)

function openCommForm() {
  commFormVisible.value = true
  commForm.value = {
    content: '',
    contact: '',
    method: '微信',
    my_action: '',
    occurred_at: new Date().toISOString().slice(0, 16),
  }
}

async function saveComm() {
  if (!commForm.value.content.trim()) {
    ElMessage.warning('请填写沟通内容')
    return
  }
  savingComm.value = true
  try {
    await createCommunication(appId.value, {
      content: commForm.value.content,
      contact: commForm.value.contact || null,
      method: commForm.value.method,
      my_action: commForm.value.my_action || null,
      occurred_at: commForm.value.occurred_at
        ? new Date(commForm.value.occurred_at).toISOString()
        : null,
    })
    ElMessage.success('已记录沟通')
    commFormVisible.value = false
    loadAll()
  } catch {
    /* 拦截器已提示 */
  } finally {
    savingComm.value = false
  }
}

/* 编辑 */
const editVisible = ref(false)

/* 标签编辑 */
const tagEditing = ref(false)
const tagInput = ref('')

async function saveTags() {
  if (!app.value) return
  const names = tagInput.value
    .split(/[,，、]/)
    .map((s) => s.trim())
    .filter(Boolean)
  await setApplicationTags(app.value.id, names)
  ElMessage.success('标签已更新')
  tagEditing.value = false
  loadAll()
}

/* 问题 */
const issueFormVisible = ref(false)

/* 简历预览 */
async function previewResume(r: Resume) {
  const url = await getResumeUrl(r.id)
  window.open(url, '_blank')
}

/** 把已有简历关联到本投递 */
async function linkResume() {
  if (linkResumeId.value == null) return
  try {
    await updateResume(linkResumeId.value, { applicationId: appId.value })
    ElMessage.success('简历已关联到本投递')
    linkResumeId.value = null
    allResumes.value = await getResumes()
    resumes.value = allResumes.value.filter((r) => r.application_id === appId.value)
  } catch {
    ElMessage.error('关联失败，请重试')
  }
}

/** 解除简历与本投递的关联 */
async function unlinkResume(r: Resume) {
  try {
    await updateResume(r.id, { applicationId: null })
    ElMessage.success('已解除关联')
    allResumes.value = await getResumes()
    resumes.value = allResumes.value.filter((x) => x.application_id === appId.value)
  } catch {
    ElMessage.error('操作失败，请重试')
  }
}

function openIssue(issueId: number) {
  router.push('/issues')
}
void openIssue
</script>

<template>
  <div class="detail-page">
    <!-- 详情头（sticky） -->
    <div class="detail-head">
      <el-button text @click="router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <template v-if="app">
        <span class="head-title">{{ app.company_name }} · {{ app.position }}</span>
        <StatusTag :status="app.status" />
        <div class="spacer" />
        <el-dropdown trigger="click" @command="changeStatus">
          <el-button size="small">改状态 ▾</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="s in STATUS_LIST" :key="s.value" :command="s.value">
                {{ s.value }}<span v-if="s.value === app.status" style="color: var(--color-gray-400)">（当前）</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button size="small" @click="editVisible = true">编辑</el-button>
      </template>
    </div>

    <div v-if="loading" class="loading-box" v-loading="true" element-loading-text="加载中…" />

    <div v-else-if="notFound" class="app-card" style="text-align: center; padding: 48px">
      <div style="font-size: var(--fs-h3); font-weight: 600">这条投递记录不存在或已被删除</div>
      <el-button type="primary" style="margin-top: 16px" @click="router.push('/applications')">返回列表</el-button>
    </div>

    <div v-else-if="app" class="detail-body">
      <!-- 左主区 -->
      <div class="main-col">
        <div class="app-card">
          <div class="card-title">基本信息</div>
          <div class="desc-grid">
            <div class="desc-item"><span class="k">公司</span>{{ app.company_name || '—' }}</div>
            <div class="desc-item"><span class="k">类型</span><TypeTag :type="app.type" /></div>
            <div class="desc-item"><span class="k">岗位</span>{{ app.position }}</div>
            <div class="desc-item"><span class="k">状态</span>{{ app.status }}<template v-if="app.interview_stage">（{{ app.interview_stage }}）</template></div>
            <div class="desc-item"><span class="k">渠道</span>{{ app.channel || '—' }}</div>
            <div class="desc-item"><span class="k">城市</span>{{ app.city || '—' }}</div>
            <div class="desc-item"><span class="k">投递日期</span><span class="num">{{ app.apply_date || '—' }}</span></div>
            <div class="desc-item"><span class="k">截止日期</span><span class="num">{{ app.deadline || '—' }}</span></div>
            <div class="desc-item"><span class="k">薪资</span>{{ app.salary || '—' }}</div>
            <div class="desc-item"><span class="k">内推人</span>{{ app.referrer || '—' }}</div>
            <div class="desc-item"><span class="k">结果日期</span><span class="num">{{ app.result_date || '—' }}</span></div>
            <div class="desc-item"><span class="k">更新时间</span><span class="num">{{ formatDateTime(app.updated_at) }}</span></div>
          </div>
          <div v-if="app.requirements" class="long-text">
            <span class="k">招聘要求</span>{{ app.requirements }}
          </div>
          <div v-if="app.tailor_notes" class="long-text">
            <span class="k">针对性修改说明</span>{{ app.tailor_notes }}
          </div>
          <div v-if="app.notes" class="long-text"><span class="k">备注</span>{{ app.notes }}</div>

          <div class="tags-row">
            <span class="k">标签</span>
            <template v-if="!tagEditing">
              <el-tag v-for="t in app.tag_names" :key="t" size="small" effect="plain" style="margin-right: 6px">{{ t }}</el-tag>
              <span v-if="!app.tag_names.length" class="muted">无</span>
              <el-button link type="primary" size="small" @click="tagEditing = true; tagInput = app.tag_names.join('、')">编辑</el-button>
            </template>
            <template v-else>
              <el-input v-model="tagInput" size="small" placeholder="多个标签用、分隔，回车保存" style="width: 280px" @keyup.enter="saveTags" />
              <el-button type="primary" size="small" @click="saveTags">保存</el-button>
              <el-button size="small" @click="tagEditing = false">取消</el-button>
            </template>
          </div>
        </div>

        <div class="app-card">
          <div class="card-title">
            <span>时间线</span>
            <el-button type="primary" size="small" @click="openCommForm">+ 记一笔</el-button>
          </div>
          <EventTimeline :items="timeline" :loading="loading" />
        </div>
      </div>

      <!-- 右副区 -->
      <div class="side-col">
        <div class="app-card status-card">
          <div class="card-title">当前状态</div>
          <div class="status-line">
            <StatusTag :status="app.status" />
            <span v-if="app.interview_stage" class="stage-text">{{ app.interview_stage }}</span>
          </div>
          <div class="status-actions">
            <el-dropdown trigger="click" @command="changeStatus">
              <el-button size="small" type="primary" plain>推进状态</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="s in STATUS_LIST" :key="s.value" :command="s.value">{{ s.value }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div class="app-card">
          <div class="card-title">简历</div>
          <template v-if="resumes.length">
            <div v-for="r in resumes" :key="r.id" class="file-row">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ r.filename }}</span>
              <el-tag v-if="r.version" size="small" effect="plain">{{ r.version }}</el-tag>
              <el-tag v-if="r.is_base" size="small" type="warning" effect="plain">初始</el-tag>
              <el-button link type="primary" size="small" @click="previewResume(r)">预览</el-button>
              <el-button link type="danger" size="small" @click="unlinkResume(r)">解除关联</el-button>
            </div>
          </template>
          <template v-else>
            <div class="muted-box">本次投递暂未关联简历</div>
            <div class="link-resume-row">
              <el-select
                v-model="linkResumeId"
                clearable
                filterable
                size="small"
                placeholder="从简历资产中选择"
                style="flex: 1"
              >
                <el-option
                  v-for="r in allResumes"
                  :key="r.id"
                  :label="`${r.is_base ? '★ ' : ''}${r.filename}${r.version ? '（' + r.version + '）' : ''}`"
                  :value="r.id"
                />
              </el-select>
              <el-button type="primary" size="small" :disabled="linkResumeId == null" @click="linkResume">
                关联
              </el-button>
            </div>
          </template>
        </div>

        <div class="app-card">
          <div class="card-title"><span>附件（{{ attachments.length }}）</span></div>
          <AttachmentWall :application-id="app.id" :attachments="attachments" @refresh="loadAll" />
        </div>

        <div class="app-card">
          <div class="card-title"><span>链接（{{ links.length }}）</span></div>
          <LinkGroup :application-id="app.id" :links="links" @refresh="loadAll" />
        </div>

        <div class="app-card">
          <div class="card-title">
            <span>关联问题（{{ relatedIssues.length }}）</span>
            <el-button type="primary" size="small" plain @click="issueFormVisible = true">记一笔</el-button>
          </div>
          <template v-if="relatedIssues.length">
            <div v-for="i in relatedIssues" :key="i.id" class="issue-row" @click="router.push('/issues')">
              <span class="issue-title">{{ i.title }}</span>
              <el-tag size="small" effect="plain">{{ i.category }}</el-tag>
            </div>
          </template>
          <div v-else class="muted-box">暂无关联问题</div>
        </div>
      </div>
    </div>

    <!-- 沟通记录表单 -->
    <el-dialog v-model="commFormVisible" title="记录沟通" width="480px">
      <el-form label-position="top">
        <el-form-item label="沟通时间（可选过去时间）">
          <el-date-picker
            v-model="commForm.occurred_at"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="沟通对象">
              <el-input v-model="commForm.contact" placeholder="HR / 面试官 / 内推人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="沟通方式">
              <el-select v-model="commForm.method" style="width: 100%">
                <el-option v-for="m in COMMUNICATION_METHODS" :key="m" :label="m" :value="m" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="内容摘要" required>
          <el-input v-model="commForm.content" type="textarea" :rows="3" placeholder="对方说了什么" />
        </el-form-item>
        <el-form-item label="我方动作">
          <el-input v-model="commForm.my_action" type="textarea" :rows="2" placeholder="我需要做什么（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="commFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingComm" @click="saveComm">保存</el-button>
      </template>
    </el-dialog>

    <ApplicationFormDrawer v-model:visible="editVisible" :editing="app" @saved="loadAll" />
    <IssueFormDrawer v-model:visible="issueFormVisible" :default-application-id="app?.id ?? null" @saved="loadAll" />
  </div>
</template>

<style scoped>
.detail-page {
  max-width: 1440px;
  margin: -24px;
  padding: 0;
}

.detail-head {
  position: sticky;
  top: -24px;
  z-index: 10;
  height: 64px;
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: 0 var(--sp-6);
  background: var(--color-gray-0);
  border-bottom: 1px solid var(--color-gray-200);
}

.head-title {
  font-size: var(--fs-h3);
  font-weight: 600;
  color: var(--color-gray-900);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 480px;
}

.detail-head .spacer {
  flex: 1;
}

.loading-box {
  height: 300px;
}

.detail-body {
  display: grid;
  grid-template-columns: 7fr 5fr;
  gap: var(--sp-4);
  padding: var(--sp-6);
  align-items: start;
}

.main-col,
.side-col {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
}

.desc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-2) var(--sp-6);
}

.desc-item {
  font-size: var(--fs-body);
  color: var(--color-gray-800);
  padding: 4px 0;
  display: flex;
  align-items: center;
  gap: var(--sp-2);
}

.k {
  display: inline-block;
  min-width: 56px;
  color: var(--color-gray-500);
  font-size: var(--fs-sm);
  flex-shrink: 0;
}

.long-text {
  font-size: var(--fs-body);
  color: var(--color-gray-700);
  padding: 6px 0;
  line-height: 22px;
}

.tags-row {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding-top: var(--sp-2);
  flex-wrap: wrap;
}

.muted {
  color: var(--color-gray-400);
}

.status-line {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
}

.stage-text {
  font-size: var(--fs-body);
  color: var(--color-gray-600);
}

.status-actions {
  margin-top: var(--sp-3);
  display: flex;
  gap: var(--sp-2);
}

.file-row {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) 0;
  border-bottom: var(--border-light);
  font-size: var(--fs-body);
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.muted-box {
  font-size: var(--fs-sm);
  color: var(--color-gray-400);
  padding: var(--sp-2) 0;
}

.link-resume-row {
  display: flex;
  gap: var(--sp-2);
  align-items: center;
  margin-top: var(--sp-1);
}

.issue-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-2) 0;
  border-bottom: var(--border-light);
  cursor: pointer;
}

.issue-row:hover .issue-title {
  color: var(--color-primary-600);
}

.issue-title {
  font-size: var(--fs-body);
  color: var(--color-gray-800);
}

@media (max-width: 1024px) {
  .detail-body {
    grid-template-columns: 1fr;
  }
}
</style>
