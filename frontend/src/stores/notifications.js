import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useNotificationStore = defineStore('notification', () => {
  const items       = ref([])
  const unreadCount = ref(0)

  async function fetchAll(userId) {
    const res = await api.getNotifications(userId)
    items.value = res.data
  }

  async function fetchUnreadCount(userId) {
    const res = await api.getUnreadCount(userId)
    unreadCount.value = res.data.count
  }

  async function markAllRead(userId) {
    await api.markNotifsRead(userId)
    items.value.forEach(n => n.is_read = 1)
    unreadCount.value = 0
  }

  return { items, unreadCount, fetchAll, fetchUnreadCount, markAllRead }
})