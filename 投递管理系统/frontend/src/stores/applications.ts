import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Application } from '@/types'
import { getApplications } from '@/api/applications'

export const useApplicationsStore = defineStore('applications', () => {
  const items = ref<Application[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      items.value = await getApplications()
    } finally {
      loading.value = false
    }
  }

  return { items, loading, fetchAll }
})
