<template>
  <div class="space-y-5 fade-up">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h2 class="text-xl font-extrabold text-navy">Reports & Analytics</h2>
      <button @click="exportCSV" class="btn-lime text-sm py-2 px-4">⬇️ Export CSV</button>
    </div>

    <!-- Filters -->
    <div class="card p-4 flex flex-wrap gap-3">
      <div>
        <label class="input-label">From</label>
        <input v-model="filters.from" type="date" class="input-field" @change="load" />
      </div>
      <div>
        <label class="input-label">To</label>
        <input v-model="filters.to" type="date" class="input-field" @change="load" />
      </div>
      <div>
        <label class="input-label">Status</label>
        <select v-model="filters.status" class="input-field" @change="load">
          <option value="all">All</option>
          <option value="borrowed">Borrowed</option>
          <option value="returned">Returned</option>
          <option value="overdue">Overdue</option>
        </select>
      </div>
      <div class="flex items-end">
        <button @click="resetFilters" class="btn-ghost text-sm py-2.5">Reset</button>
      </div>
    </div>

    <!-- Summary cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="stat-tile">
        <div class="stat-tile__icon bg-navy/8">📊</div>
        <div><p class="text-2xl font-extrabold text-navy">{{ records.length }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Total Records</p></div>
      </div>
      <div class="stat-tile">
        <div class="stat-tile__icon bg-lime/20">📋</div>
        <div><p class="text-2xl font-extrabold text-navy">{{ count('borrowed') }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Active</p></div>
      </div>
      <div class="stat-tile">
        <div class="stat-tile__icon bg-lime/20">✅</div>
        <div><p class="text-2xl font-extrabold text-navy">{{ count('returned') }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Returned</p></div>
      </div>
      <div class="stat-tile">
        <div class="stat-tile__icon bg-red-500/10">⚠️</div>
        <div><p class="text-2xl font-extrabold text-red-500">{{ count('overdue') }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Overdue</p></div>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex justify-center py-10">
        <div class="w-8 h-8 border-2 border-navy border-t-transparent rounded-full spin"></div>
      </div>
      <div v-else-if="!records.length" class="text-center py-14 text-charcoal/30">No data for this period</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-navy/[0.03] border-b border-navy/[0.06]">
            <tr>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Student</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">ID</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Equipment</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Qty</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Borrowed</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Due</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Returned</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-navy/[0.04]">
            <tr v-for="r in records" :key="r.id" class="hover:bg-navy/[0.02] transition">
              <td class="px-4 py-3 font-bold text-navy">{{ r.student_name }}</td>
              <td class="px-4 py-3 text-xs text-charcoal/50">{{ r.student_id }}</td>
              <td class="px-4 py-3">{{ r.equipment_name }}</td>
              <td class="px-4 py-3 font-bold">{{ r.quantity }}</td>
              <td class="px-4 py-3 text-xs text-charcoal/60">{{ fmtDate(r.borrowed_at) }}</td>
              <td class="px-4 py-3 text-xs" :class="r.status==='overdue'?'text-red-500 font-bold':''">{{ fmtDate(r.expected_return_at) }}</td>
              <td class="px-4 py-3 text-xs text-lime-dark">{{ r.returned_at ? fmtDate(r.returned_at) : '—' }}</td>
              <td class="px-4 py-3">
                <span :class="{
                  'badge-borrowed': r.status==='borrowed',
                  'badge-returned': r.status==='returned',
                  'badge-overdue':  r.status==='overdue',
                }" class="badge">{{ r.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const records = ref([])
const loading = ref(true)
const filters = ref({ from: '', to: '', status: 'all' })

const count    = s => records.value.filter(r => r.status === s).length
const fmtDate  = d => d ? new Date(d).toLocaleDateString('en-PH', { month:'short', day:'numeric', year:'numeric' }) : '—'

async function load() {
  loading.value = true
  try {
    const p = {}
    if (filters.value.from)           p.from   = filters.value.from
    if (filters.value.to)             p.to     = filters.value.to
    if (filters.value.status !== 'all') p.status = filters.value.status
    records.value = (await api.getReport(p)).data
  } finally { loading.value = false }
}

function resetFilters() { filters.value = { from:'', to:'', status:'all' }; load() }

function exportCSV() {
  const headers = ['ID','Student','Student ID','Department','Equipment','Category','Qty','Purpose','Borrowed At','Due At','Returned At','Status']
  const rows = records.value.map(r => [
    r.id, r.student_name, r.student_id, r.department, r.equipment_name,
    r.equipment_category, r.quantity, r.purpose || '',
    r.borrowed_at, r.expected_return_at, r.returned_at || '', r.status
  ])
  const csv = [headers, ...rows].map(row => row.map(v => `"${String(v).replace(/"/g,'""')}"`).join(',')).join('\n')
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  const a = document.createElement('a')
  a.href = url
  a.download = `pe-report-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(load)
</script>