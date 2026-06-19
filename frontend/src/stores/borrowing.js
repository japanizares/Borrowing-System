import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useBorrowingStore = defineStore('borrowing', () => {
  const records = ref([])
  const loading = ref(false)

  // Fetch all (admin) or filtered by user_id (student)
  async function fetchAll(params = {}) {
    loading.value = true
    try {
      const res = await api.getBorrowings(params)
      records.value = res.data
    } finally {
      loading.value = false
    }
  }

  // Fetch only current user's borrowings
  async function fetchMine(userId) {
    loading.value = true
    try {
      const res = await api.getBorrowings({ user_id: userId })
      records.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function borrow(data) {
    const res = await api.borrow(data)
    return res.data
  }

  async function processReturn(borrowId, data = {}) {
    const res = await api.returnEquipment(borrowId, data)
    // Update local record status
    const idx = records.value.findIndex(r => r.id === borrowId)
    if (idx !== -1) records.value[idx].status = 'returned'
    return res.data
  }

  const activeBorrows  = () => records.value.filter(r => r.status === 'borrowed')
  const overdueBorrows = () => records.value.filter(r => r.status === 'overdue')

  return { records, loading, fetchAll, fetchMine, borrow, processReturn, activeBorrows, overdueBorrows }
})