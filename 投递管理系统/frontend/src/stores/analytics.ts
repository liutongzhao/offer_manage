import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AnalyticsSummary } from '@/types'
import { getSummary } from '@/api/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  const summary = ref<AnalyticsSummary>({
    total: 0,
    by_type: {},
    by_status: {},
    by_channel: {},
    issues_total: 0,
    week_count: 0,
    interviewing: 0,
    offered: 0,
    conversion_rate: 0,
  })
  const loading = ref(false)

  async function fetchSummary() {
    loading.value = true
    try {
      summary.value = await getSummary()
    } finally {
      loading.value = false
    }
  }

  return { summary, loading, fetchSummary }
})
