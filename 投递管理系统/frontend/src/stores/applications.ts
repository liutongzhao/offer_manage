import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Application, ApplicationFilters } from '@/types'
import { getApplications } from '@/api/applications'

export const useApplicationsStore = defineStore('applications', () => {
  const items = ref<Application[]>([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchAll(filters: ApplicationFilters = {}) {
    loading.value = true
    try {
      const data = await getApplications(filters)
      items.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  return { items, total, loading, fetchAll }
})
