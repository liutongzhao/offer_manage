<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { Application, ApplicationCreate, CompanyWithCount } from '@/types'
import {
  CHANNELS,
  COMPANY_SCALES,
  STATUS_LIST,
  TYPE_LIST,
} from '@/constants/enums'
import { createCompany, getCompanies } from '@/api/companies'
import { createApplication, updateApplication } from '@/api/applications'

/** 新增/编辑投递抽屉（PG-010，5 分组表单） */
const props = defineProps<{
  visible: boolean
  editing?: Application | null
  defaultCompanyId?: number | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'saved', app: Application): void
}>()

const saving = ref(false)
const formRef = ref()
const companyKeyword = ref('')
const companyOptions = ref<CompanyWithCount[]>([])
/** 值为 company id 或 "new:<名称>" */
const companyIdOrNew = ref<number | string>('')

interface FormModel {
  type: string
  position: string
  status: string
  channel: string
  city: string
  referrer: string
  apply_date: string | null
  deadline: string | null
  salary: string
  interview_stage: string
  result_date: string | null
  jd_url: string
  requirements: string
  tailor_notes: string
  notes: string
  tags: string[]
}

const emptyForm = (): FormModel => ({
  type: '后端开发',
  position: '',
  status: '待投递',
  channel: '',
  city: '',
  referrer: '',
  apply_date: null,
  deadline: null,
  salary: '',
  interview_stage: '',
  result_date: null,
  jd_url: '',
  requirements: '',
  tailor_notes: '',
  notes: '',
  tags: [],
})

const form = reactive<FormModel>(emptyForm())
const newCompanyName = ref('')

const rules = {
  position: [{ required: true, message: '请填写岗位名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择投递类型', trigger: 'change' }],
}

watch(
  () => props.visible,
  async (v) => {
    if (!v) return
    await loadCompanies()
    if (props.editing) {
      Object.assign(form, emptyForm(), {
        type: props.editing.type,
        position: props.editing.position,
        status: props.editing.status,
        channel: props.editing.channel ?? '',
        city: props.editing.city ?? '',
        referrer: props.editing.referrer ?? '',
        apply_date: props.editing.apply_date,
        deadline: props.editing.deadline,
        salary: props.editing.salary ?? '',
        interview_stage: props.editing.interview_stage ?? '',
        result_date: props.editing.result_date,
        jd_url: props.editing.jd_url ?? '',
        requirements: props.editing.requirements ?? '',
        tailor_notes: props.editing.tailor_notes ?? '',
        notes: props.editing.notes ?? '',
        tags: [...props.editing.tag_names],
      })
      companyIdOrNew.value = props.editing.company_id
      newCompanyName.value = ''
    } else {
      Object.assign(form, emptyForm())
      companyIdOrNew.value = props.defaultCompanyId ?? ''
      newCompanyName.value = ''
    }
  },
)

async function loadCompanies() {
  try {
    const list = await getCompanies({ with_count: false })
    companyOptions.value = list as CompanyWithCount[]
  } catch {
    companyOptions.value = []
  }
}

const filteredCompanyOptions = computed(() => {
  const kw = companyKeyword.value.trim().toLowerCase()
  if (!kw) return companyOptions.value
  return companyOptions.value.filter(
    (c) => c.name.toLowerCase().includes(kw) || (c.alias || '').toLowerCase().includes(kw),
  )
})

const selectedTagName = ref('')

function addTag() {
  const t = selectedTagName.value.trim()
  if (t && !form.tags.includes(t)) form.tags.push(t)
  selectedTagName.value = ''
}

function removeTag(t: string) {
  form.tags = form.tags.filter((x) => x !== t)
}

async function onSave() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    // 解析公司：已有 id 或新建
    let companyId: number
    if (typeof companyIdOrNew.value === 'number') {
      companyId = companyIdOrNew.value
    } else {
      const name = newCompanyName.value.trim()
      if (!name) {
        ElMessage.warning('请选择已有公司或填写新公司名称')
        saving.value = false
        return
      }
      const created = await createCompany({ name })
      companyId = created.id
    }

    const payload: ApplicationCreate = {
      company_id: companyId,
      type: form.type,
      position: form.position.trim(),
      status: form.status,
      channel: form.channel || null,
      city: form.city || null,
      referrer: form.referrer || null,
      apply_date: form.apply_date,
      deadline: form.deadline,
      salary: form.salary || null,
      interview_stage: form.interview_stage || null,
      result_date: form.result_date,
      jd_url: form.jd_url || null,
      requirements: form.requirements || null,
      tailor_notes: form.tailor_notes || null,
      notes: form.notes || null,
      tag_names: form.tags,
    }

    let saved: Application
    if (props.editing) {
      saved = await updateApplication(props.editing.id, payload)
      ElMessage.success('已保存修改')
    } else {
      saved = await createApplication(payload)
      ElMessage.success(`已新增投递：${form.position}`)
    }
    emit('update:visible', false)
    emit('saved', saved)
  } catch {
    /* 失败时抽屉保持打开，不丢数据 */
  } finally {
    saving.value = false
  }
}

function onClose() {
  emit('update:visible', false)
}
</script>

<template>
  <el-drawer
    :model-value="visible"
    :title="editing ? '编辑投递' : '新增投递'"
    size="640px"
    :close-on-click-modal="false"
    @update:model-value="onClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="app-form">
      <div class="group-title">基本信息</div>
      <el-form-item label="公司" required>
        <el-select
          v-if="typeof companyIdOrNew === 'number' || companyIdOrNew === ''"
          v-model="companyIdOrNew"
          filterable
          allow-create
          default-first-option
          placeholder="输入公司名搜索，或直接新建"
          style="width: 100%"
        >
          <el-option
            v-for="c in filteredCompanyOptions"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
          <template #footer>
            <el-button size="small" text type="primary" @click="companyIdOrNew = 'new'">
              + 新建公司
            </el-button>
          </template>
        </el-select>
        <div v-else class="new-company-row">
          <el-input v-model="newCompanyName" placeholder="新公司名称" />
          <el-button text @click="companyIdOrNew = ''">返回选择已有公司</el-button>
        </div>
      </el-form-item>
      <div class="form-row">
        <el-form-item label="投递类型" prop="type" class="grow">
          <el-select v-model="form.type">
            <el-option v-for="t in TYPE_LIST" :key="t.value" :label="t.value" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="当前状态" class="grow">
          <el-select v-model="form.status">
            <el-option v-for="s in STATUS_LIST" :key="s.value" :label="s.value" :value="s.value" />
          </el-select>
        </el-form-item>
      </div>
      <el-form-item label="岗位名称" prop="position">
        <el-input v-model="form.position" placeholder="如：Java 后端开发工程师" />
      </el-form-item>
      <div class="form-row">
        <el-form-item label="工作城市" class="grow">
          <el-input v-model="form.city" placeholder="如：杭州 / 远程" />
        </el-form-item>
        <el-form-item label="投递渠道" class="grow">
          <el-select v-model="form.channel" clearable placeholder="选择渠道">
            <el-option v-for="c in CHANNELS" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
      </div>
      <div class="form-row">
        <el-form-item label="内推人" class="grow">
          <el-input v-model="form.referrer" placeholder="姓名 / 来源" />
        </el-form-item>
        <el-form-item label="薪资范围" class="grow">
          <el-input v-model="form.salary" placeholder="如：25K×15" />
        </el-form-item>
      </div>
      <div class="form-row">
        <el-form-item label="投递日期" class="grow">
          <el-date-picker v-model="form.apply_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="截止日期" class="grow">
          <el-date-picker v-model="form.deadline" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </div>
      <div class="form-row">
        <el-form-item label="面试轮次" class="grow">
          <el-input v-model="form.interview_stage" placeholder="如：一面 / 二面 / HR面" />
        </el-form-item>
        <el-form-item label="结果日期" class="grow">
          <el-date-picker v-model="form.result_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </div>

      <div class="group-title">岗位信息</div>
      <el-form-item label="JD 链接">
        <el-input v-model="form.jd_url" placeholder="岗位详情页地址" />
      </el-form-item>
      <el-form-item label="招聘要求">
        <el-input v-model="form.requirements" type="textarea" :rows="3" placeholder="学历/技能/经验要求原文" />
      </el-form-item>
      <el-form-item label="针对性修改说明">
        <el-input v-model="form.tailor_notes" type="textarea" :rows="2" placeholder="这次简历改了什么、为什么改" />
      </el-form-item>

      <div class="group-title">标签与备注</div>
      <el-form-item label="标签">
        <div class="tags-editor">
          <el-tag
            v-for="t in form.tags"
            :key="t"
            closable
            type="info"
            effect="plain"
            @close="removeTag(t)"
          >{{ t }}</el-tag>
          <el-input
            v-model="selectedTagName"
            size="small"
            placeholder="输入标签，回车添加"
            style="width: 180px"
            @keyup.enter="addTag"
          />
        </div>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.notes" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="onClose">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">
          {{ saving ? '保存中…' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<style scoped>
.group-title {
  font-size: var(--fs-sm);
  color: var(--color-gray-500);
  margin: var(--sp-5) 0 var(--sp-3);
  padding-top: var(--sp-3);
  border-top: var(--border-light);
}

.group-title:first-child {
  border-top: none;
  margin-top: 0;
  padding-top: 0;
}

.form-row {
  display: flex;
  gap: var(--sp-3);
}

.form-row .grow {
  flex: 1;
}

.tags-editor {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-2);
  align-items: center;
}

.new-company-row {
  display: flex;
  gap: var(--sp-2);
  width: 100%;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--sp-2);
}
</style>
