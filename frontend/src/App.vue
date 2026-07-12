<template>
  <div class="min-h-screen bg-canvas">
    <div v-if="auth.isLoggedIn" class="flex">
      <Sidebar />
      <div class="flex-1 min-w-0 lg:ml-64">
        <Topbar />
        <main class="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
          <router-view v-slot="{ Component }">
            <Transition name="page">
              <component :is="Component" :key="$route.path" />
            </Transition>
          </router-view>
        </main>
      </div>
    </div>
    <router-view v-else />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import Topbar  from '@/components/Topbar.vue'

const auth = useAuthStore()
onMounted(() => auth.load())
</script>

<style>
.page-enter-active,
.page-leave-active  { transition: opacity 0.15s ease; }

.page-leave-active  { position: absolute; width: 100%; }
.page-leave-to      { opacity: 0; }
.page-enter-from    { opacity: 0; }
</style>