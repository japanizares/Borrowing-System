<template>
  <div class="max-w-lg mx-auto fade-up">
    <h2 class="text-xl font-extrabold text-navy mb-6">Borrow Equipment</h2>

    <div class="card p-6 space-y-5">
      <div>
        <label class="input-label">Equipment *</label>
        <select v-model="form.equipment_id" class="input-field">
          <option value="">— Select Equipment —</option>
          <option v-for="e in available" :key="e.id" :value="e.id">
            {{ e.name }} (Available: {{ e.available_quantity }})
          </option>
        </select>
      </div>

      <div>
        <label class="input-label">Quantity *</label>
        <input v-model.number="form.quantity" type="number" min="1"
          :max="maxQty" class="input-field" />
        <p v-if="maxQty" class="text-[11px] text-charcoal/40 mt-1">Maximum: {{ maxQty }}</p>
      </div>

      <div>
        <label class="input-label">Return Date & Time *</label>
        <input v-model="form.expected_return_at" type="datetime-local"
          :min="minReturn" class="input-field" />
        <p class="text-[11px] text-charcoal/40 mt-1">Must be a future date</p>
      </div>

      <div>
        <label class="input-label">Purpose / Notes</label>
        <textarea v-model="form.purpose" rows="3" class="input-field"
          placeholder="e.g. For intramurals practice"></textarea>
      </div>

      <div v-if="error"
        class="bg-red-50 border border-red-200 text-red-600 text-sm px-3 py-2.5 rounded-xl">
        ⚠️ {{ error }}
      </div>
      <div v-if="success"
        class="bg-lime/15 border border-lime-dark/30 text-navy text-sm px-3 py-2.5 rounded-xl font-semibold">
        ✅ {{ success }}
      </div>

      <div class="flex gap-3 pt-1">
        <router-link to="/equipment" class="btn-ghost flex-1 py-2.5">Cancel</router-link>
        <button @click="handleSubmit" :disabled="saving" class="btn-lime flex-1 py-2.5">
          <svg v-if="saving" width="15" height="15" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" class="spin">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
          {{ saving ? 'Submitting…' : 'Submit Request' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

// datetime-local minimum = now + 1 hour
const minReturn = computed(() => {
  const d = new Date(Date.now() + 3600000)
  return d.toISOString().slice(0, 16)
})

const defaultReturn = computed(() => {
  const d = new Date(Date.now() + 7 * 86400000)
  return d.toISOString().slice(0, 16)
})

const form = ref({
  equipment_id:       route.query.equipment_id ? Number(route.query.equipment_id) : '',
  quantity:           1,
  expected_return_at: defaultReturn.value,
  purpose:            '',
})

const available = ref([])
const error     = ref('')
const success   = ref('')
const saving    = ref(false)

const maxQty = computed(() =>
  available.value.find(e => e.id === form.value.equipment_id)?.available_quantity || null
)

async function handleSubmit() {
  error.value = ''; success.value = ''
  if (!form.value.equipment_id)      { error.value = 'Please select equipment'; return }
  if (!form.value.quantity || form.value.quantity < 1) { error.value = 'Quantity must be at least 1'; return }
  if (!form.value.expected_return_at){ error.value = 'Please set a return date'; return }

  saving.value = true
  try {
    // Backend expects: user_id, equipment_id, quantity, purpose, expected_return_at
    await api.borrow({
      user_id:            auth.user.user_id,
      equipment_id:       form.value.equipment_id,
      quantity:           form.value.quantity,
      purpose:            form.value.purpose,
      expected_return_at: form.value.expected_return_at,
    })
    success.value = 'Request submitted successfully!'
    setTimeout(() => router.push('/my-borrowings'), 1500)
  } catch (e) {
    error.value = e.response?.data?.message || 'Failed to submit request'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const res = await api.getEquipment({ available_only: 'true' })
  available.value = res.data
})
</script>