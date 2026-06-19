<template>
  <!-- Mobile overlay -->
  <Transition name="fade">
    <div v-if="mobileOpen" class="fixed inset-0 bg-charcoal/50 z-40 lg:hidden" @click="mobileOpen=false"></div>
  </Transition>

  <!-- Mobile toggle -->
  <button @click="mobileOpen=true" class="fixed top-4 left-4 z-30 lg:hidden w-10 h-10 bg-navy rounded-xl flex items-center justify-center text-white shadow-card-lg">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
  </button>

  <aside
    class="fixed top-0 left-0 h-screen w-64 bg-navy flex flex-col z-50 transition-transform duration-200 lg:translate-x-0"
    :class="mobileOpen ? 'translate-x-0' : '-translate-x-full'"
  >
    <!-- Brand -->
    <div class="px-5 py-6 flex items-center gap-3 border-b border-white/[0.06]">
      <div class="w-10 h-10 bg-lime rounded-xl flex items-center justify-center flex-shrink-0 relative">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0B2545" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="9"/>
          <path d="M12 3a9 9 0 000 18M3 12h18M5.6 5.6c2 2 2 10.8 0 12.8M18.4 5.6c-2 2-2 10.8 0 12.8"/>
        </svg>
      </div>
      <div class="min-w-0">
        <p class="text-white font-extrabold text-[15px] leading-tight tracking-tight">PE Equipment</p>
        <p class="text-lime text-[11px] font-bold uppercase tracking-widest leading-tight">Borrowing System</p>
      </div>
      <button @click="mobileOpen=false" class="ml-auto lg:hidden text-white/40 hover:text-white">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto px-3 py-5 space-y-0.5">
      <template v-if="auth.isAdmin">
        <p class="px-3 text-[10px] font-bold text-white/30 uppercase tracking-widest mb-2">Administration</p>
        <SideLink to="/admin"            :icon="iconGrid"  label="Dashboard"/>
        <SideLink to="/admin/equipment"  :icon="iconBall"  label="Equipment"/>
        <SideLink to="/admin/borrowings" :icon="iconList"  label="Borrowings"/>
        <SideLink to="/admin/users"      :icon="iconUsers" label="Users"/>
        <SideLink to="/admin/reports"    :icon="iconChart" label="Reports"/>
      </template>
      <template v-else>
        <p class="px-3 text-[10px] font-bold text-white/30 uppercase tracking-widest mb-2">Menu</p>
        <SideLink to="/dashboard"     :icon="iconHome"  label="Overview"/>
        <SideLink to="/equipment"     :icon="iconBall"  label="Equipment"/>
        <SideLink to="/borrow"        :icon="iconList"  label="Borrow Item"/>
        <SideLink to="/my-borrowings" :icon="iconFolder" label="My Records"/>
      </template>
    </nav>

    <!-- User card -->
    <div class="p-3 border-t border-white/[0.06]">
      <div class="bg-white/[0.05] rounded-xl p-3 flex items-center gap-3">
        <div class="w-9 h-9 bg-lime rounded-lg flex items-center justify-center text-navy font-extrabold text-sm flex-shrink-0">
          {{ auth.user?.name?.charAt(0)?.toUpperCase() || 'U' }}
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-white text-xs font-bold truncate">{{ auth.user?.name }}</p>
          <p class="text-white/40 text-[11px] capitalize">{{ auth.user?.role }}</p>
        </div>
        <button @click="doLogout" class="text-white/40 hover:text-lime transition-colors flex-shrink-0" title="Log out">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SideLink from './SideLink.vue'

const auth   = useAuthStore()
const router = useRouter()
const mobileOpen = ref(false)

const doLogout = () => { auth.logout(); router.push('/auth') }

// Inline icon render functions (no external icon lib needed)
const svgBase = (paths) => ({ render: () => h('svg', { width:18, height:18, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' }, paths) })

const iconGrid  = svgBase([h('rect',{x:3,y:3,width:7,height:7,rx:1.5}),h('rect',{x:14,y:3,width:7,height:7,rx:1.5}),h('rect',{x:14,y:14,width:7,height:7,rx:1.5}),h('rect',{x:3,y:14,width:7,height:7,rx:1.5})])
const iconHome  = svgBase([h('path',{d:'M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z'}),h('polyline',{points:'9 22 9 12 15 12 15 22'})])
const iconBall  = svgBase([h('circle',{cx:12,cy:12,r:9}),h('path',{d:'M12 3a9 9 0 000 18M3 12h18M5.6 5.6c2 2 2 10.8 0 12.8M18.4 5.6c-2 2-2 10.8 0 12.8'})])
const iconList  = svgBase([h('path',{d:'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2'}),h('rect',{x:9,y:3,width:6,height:4,rx:2}),h('path',{d:'M9 12h6M9 16h4'})])
const iconUsers = svgBase([h('path',{d:'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2'}),h('circle',{cx:9,cy:7,r:4}),h('path',{d:'M23 21v-2a4 4 0 00-3-3.87'}),h('path',{d:'M16 3.13a4 4 0 010 7.75'})])
const iconChart = svgBase([h('line',{x1:18,y1:20,x2:18,y2:10}),h('line',{x1:12,y1:20,x2:12,y2:4}),h('line',{x1:6,y1:20,x2:6,y2:14})])
const iconFolder= svgBase([h('path',{d:'M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z'})])

defineExpose({})
</script>

<style scoped>
.fade-enter-active,.fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,.fade-leave-to { opacity: 0; }
</style>