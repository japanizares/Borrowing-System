<template>
  <div class="space-y-5 fade-up">
    <h2 class="text-xl font-extrabold text-navy">Manage Users</h2>

    <div class="card overflow-hidden">
      <div v-if="loading" class="flex justify-center py-10">
        <div class="w-8 h-8 border-2 border-navy border-t-transparent rounded-full spin"></div>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-navy/[0.03] border-b border-navy/[0.06]">
            <tr>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Name</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Student ID</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Department</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Role</th>
              <th class="text-left px-4 py-3 text-[11px] font-extrabold text-charcoal/40 uppercase tracking-wider">Status</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-navy/[0.04]">
            <tr v-for="u in users" :key="u.id" class="hover:bg-navy/[0.02] transition">
              <td class="px-4 py-3">
                <p class="font-bold text-navy">{{ u.name }}</p>
                <p class="text-xs text-charcoal/40">{{ u.email }}</p>
              </td>
              <td class="px-4 py-3 text-charcoal/60">{{ u.student_id || '—' }}</td>
              <td class="px-4 py-3 text-charcoal/60 text-xs">{{ u.department || '—' }}</td>
              <td class="px-4 py-3">
                <span :class="u.role==='admin' ? 'badge-overdue' : 'badge-borrowed'" class="badge">
                  {{ u.role }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span :class="u.is_active ? 'badge-returned' : 'badge-unavailable'" class="badge">
                  {{ u.is_active ? 'Active' : 'Disabled' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div v-if="u.role !== 'admin'" class="flex gap-1">
                  <button @click="toggle(u)"
                    :class="u.is_active ? 'text-yellow-600 hover:bg-yellow-50' : 'text-lime-dark hover:bg-lime/10'"
                    class="btn-icon text-xs font-bold px-2"
                    :title="u.is_active ? 'Disable' : 'Enable'">
                    {{ u.is_active ? '🔒' : '🔓' }}
                  </button>
                  <button @click="confirmDel(u)" class="btn-icon text-red-400 hover:bg-red-50" title="Delete">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Delete confirm -->
    <Transition name="modal">
      <div v-if="delTarget" class="fixed inset-0 bg-charcoal/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl">
          <h3 class="font-extrabold text-navy text-lg mb-2">Delete User?</h3>
          <p class="text-charcoal/60 text-sm mb-5">
            Permanently delete <strong>{{ delTarget.name }}</strong>? All their borrowing records will also be removed.
          </p>
          <div class="flex gap-3">
            <button @click="delTarget=null" class="btn-ghost flex-1">Cancel</button>
            <button @click="handleDelete" class="btn-danger flex-1">Delete</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const users     = ref([])
const loading   = ref(true)
const delTarget = ref(null)

async function load() {
  loading.value = true
  try { users.value = (await api.adminGetUsers()).data }
  finally { loading.value = false }
}

async function toggle(u) {
  try { await api.toggleUser(u.id); await load() }
  catch (e) { alert(e.response?.data?.message || 'Failed') }
}

function confirmDel(u) { delTarget.value = u }

async function handleDelete() {
  try { await api.deleteUser(delTarget.value.id); delTarget.value = null; await load() }
  catch (e) { alert(e.response?.data?.message || 'Cannot delete') }
}

onMounted(load)
</script>