<template>
  <div class="space-y-5 fade-up">
    <h2 class="text-xl font-extrabold text-navy">All Borrowings</h2>

    <div class="card p-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-[200px]">
        <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-charcoal/30 text-sm">🔍</span>
        <input v-model="search" placeholder="Search student, equipment, ID..."
          class="input-field pl-9" @input="load" />
      </div>
      <select v-model="statusFilter" class="input-field w-auto" @change="load">
        <option value="all">All Status</option>
        <option value="borrowed">Borrowed</option>
        <option value="returned">Returned</option>
        <option value="overdue">Overdue</option>
      </select>
    </div>

    <div class="card overflow-hidden">
      <div v-if="loading" class="flex justify-center py-10">
        <div class="w-8 h-8 border-2 border-navy border-t-transparent rounded-full spin"></div>
      </div>
      <div v-else-if="!records.length" class="text-center py-14 text-charcoal/30">
        <div class="text-5xl mb-3">📋</div><p>No records found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-navy/[0.03] border-b border-navy/[0.06]">
            <tr>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Student</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Equipment</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Qty</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Borrowed</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Due</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Status</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-navy/[0.04]">
            <tr v-for="r in records" :key="r.id" class="hover:bg-navy/[0.02] transition">
              <td class="px-4 py-3">
                <p class="font-bold text-navy text-sm">{{ r.student_name }}</p>
                <p class="text-xs text-charcoal/40">{{ r.student_id }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="font-semibold text-sm">{{ r.equipment_name }}</p>
                <p class="text-xs text-charcoal/40">{{ r.equipment_category }}</p>
              </td>
              <td class="px-4 py-3 font-bold">{{ r.quantity }}</td>
              <td class="px-4 py-3 text-xs text-charcoal/60">{{ fmtDate(r.borrowed_at) }}</td>
              <td class="px-4 py-3 text-xs"
                :class="r.status==='overdue'?'text-red-500 font-bold':r.status==='returned'?'text-charcoal/40':''">
                {{ fmtDate(r.expected_return_at) }}
              </td>
              <td class="px-4 py-3">
                <span :class="{
                  'badge-borrowed': r.status==='borrowed',
                  'badge-returned': r.status==='returned',
                  'badge-overdue':  r.status==='overdue',
                }" class="badge">{{ r.status }}</span>
              </td>
              <td class="px-4 py-3">
                <button v-if="r.status !== 'returned'" @click="confirmReturn(r)"
                  class="text-xs btn-ghost py-1.5 px-3 text-lime-dark border-lime-dark/30">
                  ↩️ Return
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Return modal -->
    <Transition name="modal">
      <div v-if="returnTarget" class="fixed inset-0 bg-charcoal/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl">
          <h3 class="font-extrabold text-navy text-lg mb-2">Process Return</h3>
          <p class="text-charcoal/60 text-sm mb-4">
            <strong>{{ returnTarget.student_name }}</strong> returning
            <strong>{{ returnTarget.quantity }}× {{ returnTarget.equipment_name }}</strong>
          </p>
          <div class="space-y-3 mb-5">
            <div>
              <label class="input-label">Condition on Return</label>
              <select v-model="retForm.condition" class="input-field">
                <option>Excellent</option><option>Good</option><option>Fair</option><option>Poor</option>
              </select>
            </div>
            <div>
              <label class="input-label">Notes (optional)</label>
              <textarea v-model="retForm.notes" rows="2" class="input-field" placeholder="Any damage or issues..."></textarea>
            </div>
          </div>
          <div class="flex gap-3">
            <button @click="returnTarget=null" class="btn-ghost flex-1">Cancel</button>
            <button @click="handleReturn" :disabled="processing" class="btn-lime flex-1">
              {{ processing ? 'Processing…' : 'Confirm Return' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth   = useAuthStore()
const records = ref([])
const loading = ref(true)
const search  = ref('')
const statusFilter = ref('all')
const returnTarget = ref(null)
const processing   = ref(false)
const retForm = ref({ condition: 'Good', notes: '' })

const fmtDate = d => d ? new Date(d).toLocaleDateString('en-PH',
  { month:'short', day:'numeric', year:'numeric' }) : '—'

async function load() {
  loading.value = true
  try {
    const p = { limit: 200 }
    if (search.value)                  p.search = search.value
    if (statusFilter.value !== 'all')  p.status = statusFilter.value
    records.value = (await api.getBorrowings(p)).data
  } finally { loading.value = false }
}

function confirmReturn(r) {
  returnTarget.value = r
  retForm.value = { condition: 'Good', notes: '' }
}

async function handleReturn() {
  processing.value = true
  try {
    await api.returnEquipment(returnTarget.value.id, {
      condition_on_return: retForm.value.condition,
      notes:               retForm.value.notes,
      admin_id:            auth.user?.user_id,
    })
    returnTarget.value = null
    await load()
  } catch (e) {
    alert(e.response?.data?.message || 'Failed to process return')
  } finally { processing.value = false }
}

onMounted(load)
</script>