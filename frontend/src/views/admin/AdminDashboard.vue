<template>
  <div class="space-y-6 fade-up">
    <h2 class="text-xl font-extrabold text-navy">Admin Overview</h2>

    <div v-if="loading" class="flex justify-center py-10">
      <div class="w-8 h-8 border-2 border-navy border-t-transparent rounded-full spin"></div>
    </div>

    <div v-else>
      <!-- Stats grid -->
      <div class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        <div class="stat-tile col-span-1">
          <div class="stat-tile__icon bg-lime/20">📦</div>
          <div><p class="text-2xl font-extrabold text-navy">{{ s.total_equipment }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Equipment</p></div>
        </div>
        <div class="stat-tile">
          <div class="stat-tile__icon bg-navy/8">👥</div>
          <div><p class="text-2xl font-extrabold text-navy">{{ s.total_students }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Students</p></div>
        </div>
        <div class="stat-tile">
          <div class="stat-tile__icon bg-lime/20">📋</div>
          <div><p class="text-2xl font-extrabold text-navy">{{ s.active_borrowings }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Active Borrows</p></div>
        </div>
        <div class="stat-tile">
          <div class="stat-tile__icon bg-red-500/10">⚠️</div>
          <div><p class="text-2xl font-extrabold text-red-500">{{ s.overdue }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Overdue</p></div>
        </div>
        <div class="stat-tile">
          <div class="stat-tile__icon bg-lime/20">✅</div>
          <div><p class="text-2xl font-extrabold text-navy">{{ s.returned_today }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Returned Today</p></div>
        </div>
        <div class="stat-tile">
          <div class="stat-tile__icon bg-navy/8">📊</div>
          <div><p class="text-2xl font-extrabold text-navy">{{ s.total_borrowings }}</p><p class="text-xs text-charcoal/40 font-semibold mt-0.5">Total Borrows</p></div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Top equipment -->
        <div class="card p-5">
          <h3 class="font-extrabold text-navy text-sm mb-4">🏆 Most Borrowed Equipment</h3>
          <div v-if="s.top_equipment?.length" class="flex flex-col gap-2.5">
            <div v-for="(e, i) in s.top_equipment" :key="e.name" class="flex items-center gap-3">
              <span class="w-5 text-xs font-extrabold text-charcoal/30">{{ i+1 }}</span>
              <div class="flex-1">
                <div class="flex justify-between mb-1">
                  <span class="text-sm font-bold text-navy">{{ e.name }}</span>
                  <span class="text-sm font-extrabold text-lime-dark">{{ e.count }}×</span>
                </div>
                <div class="h-1.5 bg-navy/8 rounded-full overflow-hidden">
                  <div :style="{ width: (e.count / s.top_equipment[0].count * 100) + '%' }"
                    class="h-full bg-lime rounded-full transition-all duration-700"></div>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="text-charcoal/30 text-sm text-center py-4">No data yet</p>
        </div>

        <!-- Recent activity -->
        <div class="card overflow-hidden">
          <div class="px-5 py-4 border-b border-navy/[0.06]">
            <h3 class="font-extrabold text-navy text-sm">Recent Activity</h3>
          </div>
          <div class="divide-y divide-navy/[0.04]">
            <div v-for="r in s.recent_activity" :key="r.id"
              class="flex items-center gap-3 px-5 py-3">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-navy truncate">{{ r.student }}</p>
                <p class="text-xs text-charcoal/40">{{ r.equipment }} × {{ r.qty }}</p>
              </div>
              <span :class="{
                'badge-borrowed': r.status === 'borrowed',
                'badge-returned': r.status === 'returned',
                'badge-overdue':  r.status === 'overdue',
              }" class="badge flex-shrink-0">{{ r.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const s       = ref({})
const loading = ref(true)

onMounted(async () => {
  try { s.value = (await api.getStats()).data }
  finally { loading.value = false }
})
</script>