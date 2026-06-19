import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useEquipmentStore = defineStore('equipment', () => {
  const items   = ref([])
  const loading = ref(false)
  const error   = ref(null)

  async function fetchAll(params = {}) {
    loading.value = true; error.value = null
    try {
      const res = await api.getEquipment(params)
      items.value = res.data
    } catch (e) {
      error.value = e.response?.data?.message || 'Failed to load equipment'
    } finally {
      loading.value = false
    }
  }

  async function add(data) {
    const res = await api.addEquipment(data)
    await fetchAll()
    return res.data
  }

  async function update(id, data) {
    const res = await api.updateEquipment(id, data)
    await fetchAll()
    return res.data
  }

  async function remove(id) {
    await api.deleteEquipment(id)
    items.value = items.value.filter(i => i.id !== id)
  }

  return { items, loading, error, fetchAll, add, update, remove }
})