<template>
  <header class="h-16 bg-white border-b border-navy/[0.06] flex items-center justify-between px-4 sm:px-6 lg:px-8 sticky top-0 z-20">
    <div class="ml-12 lg:ml-0">
      <p class="text-[15px] font-extrabold text-navy leading-tight">{{ pageTitle }}</p>
      <p class="text-[11px] text-charcoal/40 font-medium">{{ todayStr }}</p>
    </div>

    <div class="flex items-center gap-3">
      <router-link to="/notifications" class="btn-icon relative">
        <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>
        </svg>
        <span v-if="unread > 0" class="absolute top-0.5 right-0.5 bg-red-500 text-white text-[9px] font-extrabold w-4 h-4 flex items-center justify-center rounded-full ring-2 ring-white">
          {{ unread > 9 ? '9+' : unread }}
        </span>
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const route = useRoute()
const auth  = useAuthStore()
const unread = ref(0)
let timer = null

const titles = {
  '/dashboard': 'Overview', '/equipment': 'Equipment Catalog', '/borrow': 'Borrow Equipment',
  '/my-borrowings': 'My Borrowing Records', '/notifications': 'Notifications',
  '/admin': 'Admin Dashboard', '/admin/equipment': 'Manage Equipment', '/admin/borrowings': 'All Borrowings',
  '/admin/users': 'Manage Users', '/admin/reports': 'Reports & Analytics',
}
const pageTitle = computed(() => titles[route.path] || 'PE Borrowing System')

const todayStr = computed(() => new Date().toLocaleDateString('en-PH', { weekday:'long', month:'long', day:'numeric', year:'numeric' }))

const fetchUnread = async () => {
  if (!auth.user) return
  try { unread.value = (await api.getUnreadCount(auth.user.user_id)).data.count } catch {}
}

onMounted(() => { fetchUnread(); timer = setInterval(fetchUnread, 30000) })
onUnmounted(() => clearInterval(timer))
</script>