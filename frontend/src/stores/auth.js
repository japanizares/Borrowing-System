import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // Backend returns: { user_id, name, email, student_id, year_level, department, role }
  const user = ref(JSON.parse(localStorage.getItem('pe_user') || 'null'))

  const isLoggedIn = computed(() => !!user.value)
  const isAdmin    = computed(() => user.value?.role === 'admin')

  function setUser(data) {
    // data is the direct response from /api/login
    user.value = {
      user_id:    data.user_id,
      name:       data.name,
      email:      data.email,
      student_id: data.student_id,
      year_level: data.year_level,
      department: data.department,
      role:       data.role,
    }
    localStorage.setItem('pe_user', JSON.stringify(user.value))
  }

  function load() {
    const saved = localStorage.getItem('pe_user')
    if (saved) user.value = JSON.parse(saved)
  }

  function logout() {
    user.value = null
    localStorage.removeItem('pe_user')
  }

  return { user, isLoggedIn, isAdmin, setUser, load, logout }
})