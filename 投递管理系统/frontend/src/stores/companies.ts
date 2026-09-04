import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Company } from '@/types'
import { getCompanies } from '@/api/companies'

export const useCompaniesStore = defineStore('companies', () => {
  const items = ref<Company[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      items.value = await getCompanies()
    } finally {
      loading.value = false
    }
  }

  return { items, loading, fetchAll }
})
