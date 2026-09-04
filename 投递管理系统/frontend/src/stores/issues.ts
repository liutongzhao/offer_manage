import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Issue } from '@/types'
import { getIssues } from '@/api/issues'

export const useIssuesStore = defineStore('issues', () => {
  const items = ref<Issue[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      items.value = await getIssues()
    } finally {
      loading.value = false
    }
  }

  return { items, loading, fetchAll }
})
