<template>
  <div class="space-y-6 fade-up">
    <div>
      <h2 class="text-xl font-extrabold text-navy">
        Welcome back, {{ auth.user?.name?.split(' ')[0] }} 👋
      </h2>
      <p class="text-charcoal/40 text-sm mt-0.5">
        Here's your borrowing overview.
      </p>
    </div>

    <!-- Stats -->
    <div v-if="loading" class="flex justify-center py-10">
      <div class="w-8 h-8 border-2 border-navy border-t-transparent rounded-full spin"></div>
    </div>

    <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="stat-tile">
        <div class="stat-tile__icon bg-lime/20">📦</div>
        <div>
          <p class="text-2xl font-extrabold text-navy">{{ stats.total_equipment ?? '—' }}</p>
          <p class="text-xs text-charcoal/40 font-semibold mt-0.5">Total Equipment</p>
        </div>
      </div>
      <div class="stat-tile">
        <div class="stat-tile__icon bg-navy/8">📋</div>
        <div>
          <p class="text-2xl font-extrabold text-navy">{{ myActive }}</p>
          <p class="text-xs text-charcoal/40 font-semibold mt-0.5">My Active Borrows</p>
        </div>
      </div>
      <div class="stat-tile">
        <div class="stat-tile__icon bg-red-500/10">⚠️</div>
        <div>
          <p class="text-2xl font-extrabold text-red-500">{{ myOverdue }}</p>
          <p class="text-xs text-charcoal/40 font-semibold mt-0.5">Overdue</p>
        </div>
      </div>
      <div class="stat-tile">
        <div class="stat-tile__icon bg-lime/20">✅</div>
        <div>
          <p class="text-2xl font-extrabold text-navy">{{ myReturned }}</p>
          <p class="text-xs text-charcoal/40 font-semibold mt-0.5">Returned</p>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="card p-5">
      <h3 class="font-extrabold text-navy mb-4 text-sm uppercase tracking-wider">Quick Actions</h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <router-link to="/equipment"     class="btn-lime py-3 text-sm">🏀 Browse Equipment</router-link>
        <router-link to="/borrow"        class="btn-navy py-3 text-sm">➕ New Borrow</router-link>
        <router-link to="/my-borrowings" class="btn-ghost py-3 text-sm">📋 My Records</router-link>
      </div>
    </div>

    <!-- My recent borrows -->
    <div class="card overflow-hidden">
      <div class="px-5 py-4 border-b border-navy/[0.06] flex items-center justify-between">
        <h3 class="font-extrabold text-navy text-sm">My Recent Borrows</h3>
        <router-link to="/my-borrowings" class="text-xs text-lime-dark font-bold hover:underline">
          View all →
        </router-link>
      </div>
      <div v-if="myRecords.length === 0" class="text-center py-10 text-charcoal/30 text-sm">
        No borrowing records yet
      </div>
      <div v-else class="divide-y divide-navy/[0.04]">
        <div v-for="r in myRecords.slice(0, 5)" :key="r.id"
          class="flex items-center gap-4 px-5 py-3.5">
          <div class="flex-1 min-w-0">
            <p class="font-bold text-navy text-sm truncate">{{ r.equipment_name }}</p>
            <p class="text-xs text-charcoal/40 mt-0.5">
              Qty: {{ r.quantity }} · Due: {{ fmtDate(r.expected_return_at) }}
            </p>
          </div>
          <span :class="badgeClass(r.status)" class="badge">{{ r.status }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth    = useAuthStore()
const loading = ref(true)
const stats   = ref({})
const myRecords = ref([])

const myActive  = computed(() => myRecords.value.filter(r => r.status === 'borrowed').length)
const myOverdue = computed(() => myRecords.value.filter(r => r.status === 'overdue').length)
const myReturned= computed(() => myRecords.value.filter(r => r.status === 'returned').length)

const fmtDate = d => d ? new Date(d).toLocaleDateString('en-PH', { month:'short', day:'numeric', year:'numeric' }) : '—'
const badgeClass = s => ({
  borrowed: 'badge-borrowed',
  returned: 'badge-returned',
  overdue:  'badge-overdue',
}[s] || 'badge-borrowed')

onMounted(async () => {
  try {
    const [statsRes, myRes] = await Promise.all([
      api.getStats(),
      api.getBorrowings({ user_id: auth.user?.user_id }),
    ])
    stats.value    = statsRes.data
    myRecords.value = myRes.data
  } finally {
    loading.value = false
  }
})
</script>