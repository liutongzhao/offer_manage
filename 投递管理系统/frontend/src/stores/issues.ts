import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Issue } from '@/types'
import { getIssues } from '@/api/issues'

export const useIssuesStore = defineStore('issues', () => {
  const items = ref<Issue[]>([])
  const loading = ref(false)

  async function fetchAll(params: { category?: string; related_application_id?: number } = {}) {
    loading.value = true
    try {
      items.value = await getIssues(params)
    } finally {
      loading.value = false
    }
  }

  return { items, loading, fetchAll }
})
