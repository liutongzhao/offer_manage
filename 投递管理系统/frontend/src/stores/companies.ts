import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CompanyWithCount } from '@/types'
import { getCompanies } from '@/api/companies'

export const useCompaniesStore = defineStore('companies', () => {
  const items = ref<CompanyWithCount[]>([])
  const loading = ref(false)

  async function fetchAll(keyword?: string) {
    loading.value = true
    try {
      const list = await getCompanies({ keyword, with_count: true })
      items.value = list as CompanyWithCount[]
    } finally {
      loading.value = false
    }
  }

  return { items, loading, fetchAll }
})
