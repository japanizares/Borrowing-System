<template>
  <div class="space-y-5 fade-up max-w-2xl">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-extrabold text-navy">Notifications</h2>
      <button v-if="items.length" @click="markAll"
        class="text-xs font-bold text-lime-dark hover:underline">
        Mark all read
      </button>
    </div>

    <div class="card overflow-hidden">
      <div v-if="loading" class="flex justify-center py-10">
        <div class="w-7 h-7 border-2 border-navy border-t-transparent rounded-full spin"></div>
      </div>
      <div v-else-if="!items.length" class="text-center py-12 text-charcoal/30 text-sm">
        No notifications yet
      </div>
      <div v-else class="divide-y divide-navy/[0.04]">
        <div
          v-for="n in items" :key="n.id"
          :class="n.is_read ? 'opacity-60' : 'bg-lime/5'"
          class="flex items-start gap-4 px-5 py-4 transition">
          <div class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
            :class="n.is_read ? 'bg-navy/15' : 'bg-lime-dark pulse-lime'">
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-navy">{{ n.title }}</p>
            <p class="text-xs text-charcoal/50 mt-0.5">{{ n.message }}</p>
            <p class="text-[11px] text-charcoal/30 mt-1">{{ fmtDate(n.created_at) }}</p>
          </div>
          <span v-if="n.type" :class="{
            'badge-borrowed': n.type === 'info',
            'badge-overdue':  n.type === 'warning',
            'badge-returned': n.type === 'success',
          }" class="badge text-[10px] flex-shrink-0">{{ n.type }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth    = useAuthStore()
const items   = ref([])
const loading = ref(true)

const fmtDate = d => d ? new Date(d).toLocaleString('en-PH',
  { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' }) : ''

async function markAll() {
  await api.markNotifsRead(auth.user?.user_id)
  items.value.forEach(n => n.is_read = 1)
}

onMounted(async () => {
  try {
    const res = await api.getNotifications(auth.user?.user_id)
    items.value = res.data
  } finally { loading.value = false }
})
</script>