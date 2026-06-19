<template>
  <div class="space-y-5 fade-up">
    <h2 class="text-xl font-extrabold text-navy">My Borrowing Records</h2>

    <div class="card p-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-[180px]">
        <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-charcoal/30 text-sm">🔍</span>
        <input v-model="search" placeholder="Search equipment..." class="input-field pl-9" />
      </div>
      <select v-model="statusFilter" class="input-field w-auto">
        <option value="all">All Status</option>
        <option value="borrowed">Borrowed</option>
        <option value="returned">Returned</option>
        <option value="overdue">Overdue</option>
      </select>
    </div>

    <div class="card overflow-hidden">
      <div v-if="loading" class="flex justify-center py-10">
        <div class="w-7 h-7 border-2 border-navy border-t-transparent rounded-full spin"></div>
      </div>
      <div v-else-if="!filtered.length" class="text-center py-12 text-charcoal/30 text-sm">
        No records found
      </div>
      <div v-else class="divide-y divide-navy/[0.04]">
        <div v-for="r in filtered" :key="r.id" class="flex items-start gap-4 px-5 py-4">
          <div class="flex-1 min-w-0">
            <p class="font-extrabold text-navy text-sm">{{ r.equipment_name }}</p>
            <p class="text-xs text-charcoal/40 mt-0.5">
              Qty: {{ r.quantity }}
              · Borrowed: {{ fmtDate(r.borrowed_at) }}
              · Due: {{ fmtDate(r.expected_return_at) }}
            </p>
            <p v-if="r.returned_at" class="text-xs text-lime-dark font-semibold mt-0.5">
              ✅ Returned: {{ fmtDate(r.returned_at) }}
            </p>
            <p v-if="r.purpose" class="text-xs text-charcoal/30 mt-0.5 italic">
              "{{ r.purpose }}"
            </p>
          </div>
          <span :class="badgeClass(r.status)" class="badge flex-shrink-0 mt-0.5">
            {{ r.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth   = useAuthStore()
const records = ref([])
const loading = ref(true)
const search  = ref('')
const statusFilter = ref('all')

const fmtDate = d => d ? new Date(d).toLocaleDateString('en-PH',
  { month:'short', day:'numeric', year:'numeric' }) : '—'

const badgeClass = s => ({
  borrowed: 'badge-borrowed',
  returned: 'badge-returned',
  overdue:  'badge-overdue',
}[s] || 'badge-borrowed')

const filtered = computed(() => records.value.filter(r => {
  const matchSearch = !search.value ||
    r.equipment_name?.toLowerCase().includes(search.value.toLowerCase())
  const matchStatus = statusFilter.value === 'all' || r.status === statusFilter.value
  return matchSearch && matchStatus
}))

onMounted(async () => {
  try {
    const res = await api.getBorrowings({ user_id: auth.user?.user_id })
    records.value = res.data
  } finally {
    loading.value = false
  }
})
</script>