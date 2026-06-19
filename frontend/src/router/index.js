import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', redirect: '/dashboard' },

  {
    path: '/auth',
    component: () => import('@/views/AuthPage.vue')
  },

  // ── Student routes ─────────────────────────────────
  {
    path: '/dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/equipment',
    component: () => import('@/views/EquipmentView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/borrow',
    component: () => import('@/views/BorrowView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-borrowings',
    component: () => import('@/views/MyBorrowings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    component: () => import('@/views/NotificationsView.vue'),
    meta: { requiresAuth: true }
  },

  // ── Admin routes ───────────────────────────────────
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/admin/equipment',
    component: () => import('@/views/admin/AdminEquipment.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/admin/borrowings',
    component: () => import('@/views/admin/AdminBorrowings.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/admin/users',
    component: () => import('@/views/admin/AdminUsers.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/admin/reports',
    component: () => import('@/views/admin/AdminReports.vue'),
    meta: { requiresAuth: true, adminOnly: true }
  },

  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  auth.load()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return next('/auth')
  if (to.meta.adminOnly   && !auth.isAdmin)     return next('/dashboard')
  if (to.path === '/auth'  && auth.isLoggedIn)  return next(auth.isAdmin ? '/admin' : '/dashboard')
  next()
})

export default router