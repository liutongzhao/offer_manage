<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { Company } from '@/types'
import { COMPANY_SCALES } from '@/constants/enums'
import { createCompany, updateCompany } from '@/api/companies'

/** 新增/编辑公司弹窗（PG-012） */
const props = defineProps<{
  visible: boolean
  editing?: Company | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'saved'): void
}>()

const saving = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  alias: '',
  city: '',
  industry: '',
  scale: '',
  website: '',
  notes: '',
})

const rules = {
  name: [{ required: true, message: '请填写公司名称', trigger: 'blur' }],
}

watch(
  () => props.visible,
  (v) => {
    if (!v) return
    if (props.editing) {
      Object.assign(form, {
        name: props.editing.name,
        alias: props.editing.alias ?? '',
        city: props.editing.city ?? '',
        industry: props.editing.industry ?? '',
        scale: props.editing.scale ?? '',
        website: props.editing.website ?? '',
        notes: props.editing.notes ?? '',
      })
    } else {
      Object.assign(form, {
        name: '',
        alias: '',
        city: '',
        industry: '',
        scale: '',
        website: '',
        notes: '',
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
      await updateCompany(props.editing.id, { ...form })
      ElMessage.success('公司已更新')
    } else {
      await createCompany({ ...form })
      ElMessage.success(`已新增公司：${form.name}`)
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
  <el-dialog
    :model-value="visible"
    :title="editing ? '编辑公司' : '新增公司'"
    width="520px"
    :close-on-click-modal="false"
    @update:model-value="emit('update:visible', $event)"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="公司名称" prop="name">
        <el-input v-model="form.name" placeholder="如：字节跳动" />
      </el-form-item>
      <el-form-item label="别名/英文">
        <el-input v-model="form.alias" placeholder="便于搜索，如 bytedance" />
      </el-form-item>
      <el-form-item label="城市">
        <el-input v-model="form.city" />
      </el-form-item>
      <el-form-item label="所属行业">
        <el-input v-model="form.industry" placeholder="互联网 / 金融 / 制造等" />
      </el-form-item>
      <el-form-item label="公司规模">
        <el-select v-model="form.scale" clearable placeholder="选择规模" style="width: 100%">
          <el-option v-for="s in COMPANY_SCALES" :key="s" :label="s" :value="s" />
        </el-select>
      </el-form-item>
      <el-form-item label="官网">
        <el-input v-model="form.website" placeholder="https://" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.notes" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
    </template>
  </el-dialog>
</template>
