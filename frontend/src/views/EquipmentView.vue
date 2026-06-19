<template>
  <div class="space-y-5 fade-up">
    <h2 class="text-xl font-extrabold text-navy">Equipment Catalog</h2>

    <div class="card p-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-[200px]">
        <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-charcoal/30 text-sm">🔍</span>
        <input v-model="search" placeholder="Search equipment..."
          class="input-field pl-9" @input="doSearch" />
      </div>
      <select v-model="catFilter" class="input-field w-auto" @change="doSearch">
        <option value="">All Categories</option>
        <option v-for="c in categories" :key="c">{{ c }}</option>
      </select>
      <label class="flex items-center gap-2 text-sm font-semibold text-charcoal/60 cursor-pointer">
        <input type="checkbox" v-model="availOnly" @change="doSearch"
          class="w-4 h-4 accent-lime-dark rounded" />
        Available only
      </label>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-2 border-navy border-t-transparent rounded-full spin"></div>
    </div>
    <div v-else-if="!items.length" class="card p-10 text-center text-charcoal/30">
      <div class="text-5xl mb-3">📦</div>
      <p>No equipment found</p>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="e in items" :key="e.id" class="card p-5 flex flex-col gap-3">
        <div class="flex items-start justify-between gap-2">
          <div>
            <p class="font-extrabold text-navy text-[15px]">{{ e.name }}</p>
            <span class="text-[11px] font-bold text-charcoal/40 uppercase tracking-wider">
              {{ e.category }}
            </span>
          </div>
          <span :class="e.available_quantity > 0 ? 'badge-available' : 'badge-unavailable'"
            class="badge flex-shrink-0">
            {{ e.available_quantity > 0 ? 'Available' : 'Unavailable' }}
          </span>
        </div>

        <p v-if="e.description" class="text-xs text-charcoal/50 leading-relaxed">
          {{ e.description }}
        </p>

        <div class="flex items-center gap-2">
          <div class="flex-1 h-1.5 bg-navy/8 rounded-full overflow-hidden">
            <div
              :style="{ width: (e.available_quantity / e.total_quantity * 100) + '%' }"
              :class="e.available_quantity === 0 ? 'bg-charcoal/20'
                    : e.available_quantity < e.total_quantity ? 'bg-lime-dark' : 'bg-lime'"
              class="h-full rounded-full transition-all">
            </div>
          </div>
          <span class="text-xs font-bold text-charcoal/50">
            {{ e.available_quantity }}/{{ e.total_quantity }}
          </span>
        </div>

        <router-link v-if="e.available_quantity > 0"
          :to="{ path: '/borrow', query: { equipment_id: e.id, name: e.name, max: e.available_quantity }}"
          class="btn-lime text-sm py-2">
          Borrow
        </router-link>
        <span v-else class="text-xs text-center text-charcoal/30 font-semibold py-1">
          Not available
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const items     = ref([])
const loading   = ref(true)
const search    = ref('')
const catFilter = ref('')
const availOnly = ref(false)

const categories = computed(() => [...new Set(items.value.map(e => e.category))])

async function doSearch() {
  loading.value = true
  try {
    const params = {}
    if (search.value)    params.search        = search.value
    if (catFilter.value) params.category       = catFilter.value
    if (availOnly.value) params.available_only = 'true'
    const res = await api.getEquipment(params)
    items.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(doSearch)
</script>