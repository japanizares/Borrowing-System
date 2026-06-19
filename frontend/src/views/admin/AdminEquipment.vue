<template>
  <div class="space-y-5 fade-up">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h2 class="text-xl font-extrabold text-navy">Manage Equipment</h2>
      <button @click="openAdd" class="btn-lime text-sm py-2 px-4">＋ Add Equipment</button>
    </div>

    <!-- Toolbar -->
    <div class="card p-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-[200px]">
        <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-charcoal/30 text-sm">🔍</span>
        <input v-model="search" placeholder="Search..." class="input-field pl-9" @input="doSearch" />
      </div>
      <select v-model="catFilter" class="input-field w-auto" @change="doSearch">
        <option value="">All Categories</option>
        <option v-for="c in categories" :key="c">{{ c }}</option>
      </select>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex justify-center py-10">
        <div class="w-8 h-8 border-2 border-navy border-t-transparent rounded-full spin"></div>
      </div>
      <div v-else-if="!items.length" class="text-center py-14 text-charcoal/30">
        <div class="text-5xl mb-3">📦</div><p>No equipment found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-navy/[0.03] border-b border-navy/[0.06]">
            <tr>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Name</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Category</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Condition</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Stock</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Status</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-navy/[0.04]">
            <tr v-for="e in filtered" :key="e.id" class="hover:bg-navy/[0.02] transition">
              <td class="px-4 py-3">
                <p class="font-bold text-navy">{{ e.name }}</p>
                <p v-if="e.description" class="text-xs text-charcoal/40 truncate max-w-[180px]">{{ e.description }}</p>
              </td>
              <td class="px-4 py-3">
                <span class="text-xs font-bold bg-navy/8 text-navy px-2 py-1 rounded-lg">{{ e.category }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-charcoal/60">{{ e.condition }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-16 h-1.5 bg-navy/8 rounded-full overflow-hidden">
                    <div :style="{ width: (e.available_quantity/e.total_quantity*100)+'%' }"
                      :class="e.available_quantity===0?'bg-red-400':e.available_quantity<e.total_quantity?'bg-lime-dark':'bg-lime'"
                      class="h-full rounded-full"></div>
                  </div>
                  <span class="text-xs font-bold text-charcoal/60">{{ e.available_quantity }}/{{ e.total_quantity }}</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <span :class="e.available_quantity > 0 ? 'badge-available' : 'badge-unavailable'" class="badge">
                  {{ e.available_quantity > 0 ? 'Available' : 'Unavailable' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-1">
                  <button @click="openEdit(e)" class="btn-icon text-navy hover:bg-navy/8" title="Edit">✏️</button>
                  <button @click="confirmDel(e)" class="btn-icon text-red-400 hover:bg-red-50" title="Delete">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Add/Edit Modal -->
  <Transition name="modal">
    <div v-if="modal" class="fixed inset-0 bg-charcoal/50 flex items-center justify-center z-50 p-4"
      @click.self="modal=false">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between px-6 pt-6">
          <h2 class="text-lg font-extrabold text-navy">{{ editItem ? 'Edit Equipment' : 'Add Equipment' }}</h2>
          <button @click="modal=false" class="btn-icon">✕</button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="input-label">Name *</label>
            <input v-model="form.name" class="input-field" placeholder="e.g. Basketball" />
          </div>
          <div>
            <label class="input-label">Category *</label>
            <select v-model="form.category" class="input-field">
              <option v-for="c in CATEGORIES" :key="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="input-label">Description</label>
            <textarea v-model="form.description" rows="2" class="input-field" placeholder="Optional..."></textarea>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="input-label">Total Quantity *</label>
              <input v-model.number="form.total_quantity" type="number" min="0" class="input-field" />
            </div>
            <div>
              <label class="input-label">Condition</label>
              <select v-model="form.condition" class="input-field">
                <option>Excellent</option><option>Good</option><option>Fair</option><option>Poor</option>
              </select>
            </div>
          </div>
          <div v-if="formErr" class="bg-red-50 border border-red-200 text-red-600 text-sm px-3 py-2.5 rounded-xl">
            ⚠️ {{ formErr }}
          </div>
          <div class="flex gap-3 pt-2">
            <button @click="modal=false" class="btn-ghost flex-1">Cancel</button>
            <button @click="handleSave" :disabled="saving" class="btn-lime flex-1">
              {{ saving ? 'Saving…' : (editItem ? 'Save Changes' : 'Add Equipment') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>

  <!-- Delete confirm -->
  <Transition name="modal">
    <div v-if="delTarget" class="fixed inset-0 bg-charcoal/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <h3 class="font-extrabold text-navy text-lg mb-2">Delete Equipment?</h3>
        <p class="text-charcoal/60 text-sm mb-5">
          Remove <strong>{{ delTarget.name }}</strong> from the catalog?
        </p>
        <div class="flex gap-3">
          <button @click="delTarget=null" class="btn-ghost flex-1">Cancel</button>
          <button @click="handleDelete" class="btn-danger flex-1">Delete</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const CATEGORIES = ['Ball Sports','Racket Sports','Fitness','Outdoor','Equipment','Other']

const items     = ref([])
const loading   = ref(true)
const search    = ref('')
const catFilter = ref('')
const modal     = ref(false)
const editItem  = ref(null)
const delTarget = ref(null)
const saving    = ref(false)
const formErr   = ref('')

const emptyForm = () => ({ name:'', category: CATEGORIES[0], description:'', total_quantity: 1, condition:'Good' })
const form = ref(emptyForm())

const categories = computed(() => [...new Set(items.value.map(e => e.category))])
const filtered   = computed(() => {
  return items.value.filter(e => {
    const s = !search.value || e.name.toLowerCase().includes(search.value.toLowerCase())
    const c = !catFilter.value || e.category === catFilter.value
    return s && c
  })
})

async function doSearch() {
  loading.value = true
  try {
    const p = {}
    if (search.value)    p.search   = search.value
    if (catFilter.value) p.category = catFilter.value
    items.value = (await api.getEquipment(p)).data
  } finally { loading.value = false }
}

function openAdd()    { form.value = emptyForm(); editItem.value = null; formErr.value = ''; modal.value = true }
function openEdit(e)  {
  editItem.value = e
  form.value = { name: e.name, category: e.category, description: e.description || '', total_quantity: e.total_quantity, condition: e.condition || 'Good' }
  formErr.value = ''
  modal.value = true
}
function confirmDel(e){ delTarget.value = e }

async function handleSave() {
  if (!form.value.name.trim())     { formErr.value = 'Name is required'; return }
  if (!form.value.category.trim()) { formErr.value = 'Category is required'; return }
  saving.value = true; formErr.value = ''
  try {
    if (editItem.value) await api.updateEquipment(editItem.value.id, form.value)
    else                await api.addEquipment(form.value)
    modal.value = false
    await doSearch()
  } catch (e) {
    formErr.value = e.response?.data?.message || 'Failed to save'
  } finally { saving.value = false }
}

async function handleDelete() {
  try { await api.deleteEquipment(delTarget.value.id); delTarget.value = null; await doSearch() }
  catch (e) { alert(e.response?.data?.message || 'Cannot delete') }
}

onMounted(doSearch)
</script>

<style scoped>
.modal-enter-active,.modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from,.modal-leave-to { opacity: 0; transform: scale(0.97); }
</style>