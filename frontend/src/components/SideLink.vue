<template>
  <router-link :to="to" class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13.5px] font-semibold transition-all duration-150 relative group"
    :class="isActive ? 'bg-lime text-navy' : 'text-white/55 hover:text-white hover:bg-white/[0.06]'">
    <component :is="icon" />
    {{ label }}
    <span v-if="isActive" class="ml-auto w-1.5 h-1.5 rounded-full bg-navy/40"></span>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps(['to','icon','label'])
const route = useRoute()
const isActive = computed(() => route.path === props.to || (props.to !== '/dashboard' && props.to !== '/admin' && route.path.startsWith(props.to + '/')))
</script>