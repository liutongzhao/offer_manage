<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { Application, Issue } from '@/types'
import { ISSUE_CATEGORIES } from '@/constants/enums'
import { createIssue, updateIssue } from '@/api/issues'
import { getApplications } from '@/api/applications'

/** 新增/编辑问题抽屉（PG-013）：支持关联投递选择器 */
const props = defineProps<{
  visible: boolean
  editing?: Issue | null
  defaultApplicationId?: number | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'saved'): void
}>()

const saving = ref(false)
const formRef = ref()
const appOptions = ref<Application[]>([])

const form = reactive({
  title: '',
  category: '技术',
  related_application_id: null as number | null,
  description: '',
  solution: '',
  tags: '',
  recorded_date: null as string | null,
})

const rules = {
  title: [{ required: true, message: '请填写问题标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

watch(
  () => props.visible,
  async (v) => {
    if (!v) return
    try {
      appOptions.value = (await getApplications({ limit: 200 })).items
    } catch {
      appOptions.value = []
    }
    if (props.editing) {
      Object.assign(form, {
        title: props.editing.title,
        category: props.editing.category,
        related_application_id: props.editing.related_application_id,
        description: props.editing.description ?? '',
        solution: props.editing.solution ?? '',
        tags: props.editing.tags ?? '',
        recorded_date: props.editing.recorded_date,
      })
    } else {
      Object.assign(form, {
        title: '',
        category: '技术',
        related_application_id: props.defaultApplicationId ?? null,
        description: '',
        solution: '',
        tags: '',
        recorded_date: null,
      })
    }
  },
)

async function onSave() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    if (props.editing) {
      await updateIssue(props.editing.id, { ...form })
      ElMessage.success('问题已更新')
    } else {
      await createIssue({ ...form })
      ElMessage.success('已记录问题')
    }
    emit('update:visible', false)
    emit('saved')
  } catch {
    /* 拦截器已提示 */
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <el-drawer
    :model-value="visible"
    :title="editing ? '编辑问题' : '新增问题'"
    size="560px"
    :close-on-click-modal="false"
    @update:model-value="emit('update:visible', $event)"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="一句话，如：Redis 持久化机制" />
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="分类" prop="category">
            <el-select v-model="form.category" style="width: 100%">
              <el-option v-for="c in ISSUE_CATEGORIES" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="记录日期">
            <el-date-picker v-model="form.recorded_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="关联投递">
        <el-select
          v-model="form.related_application_id"
          clearable
          filterable
          placeholder="选择关联的投递记录"
          style="width: 100%"
        >
          <el-option
            v-for="a in appOptions"
            :key="a.id"
            :label="`${a.company_name || '—'} · ${a.position}`"
            :value="a.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="问题描述">
        <el-input v-model="form.description" type="textarea" :rows="4" placeholder="当时怎么问的" />
      </el-form-item>
      <el-form-item label="解决方案 / 正确答案">
        <el-input v-model="form.solution" type="textarea" :rows="4" placeholder="正确答法" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="form.tags" placeholder="多个标签用逗号分隔，如：Redis,八股" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
    </template>
  </el-drawer>
</template>
