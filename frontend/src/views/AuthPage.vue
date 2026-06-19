<template>
  <div class="min-h-screen bg-navy flex items-center justify-center p-4 relative overflow-hidden">
    <!-- decorative background shapes -->
    <div class="absolute -top-24 -right-24 w-96 h-96 bg-lime/10 rounded-full blur-3xl"></div>
    <div class="absolute -bottom-32 -left-32 w-96 h-96 bg-lime/5 rounded-full blur-3xl"></div>

    <div class="w-full max-w-md relative z-10">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-lime rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-card-lg">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#0B2545" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 3a9 9 0 000 18M3 12h18M5.6 5.6c2 2 2 10.8 0 12.8M18.4 5.6c-2 2-2 10.8 0 12.8"/>
          </svg>
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">PE Equipment</h1>
        <p class="text-lime text-xs font-bold uppercase tracking-[0.2em] mt-1">Borrowing System</p>
      </div>

      <div class="card p-8">
        <div class="flex bg-canvas rounded-xl p-1 mb-6">
          <button @click="mode='login'" :class="['flex-1 py-2.5 rounded-lg text-sm font-bold transition-all', mode==='login' ? 'bg-navy text-white shadow-card' : 'text-charcoal/40']">Log In</button>
          <button @click="mode='register'" :class="['flex-1 py-2.5 rounded-lg text-sm font-bold transition-all', mode==='register' ? 'bg-navy text-white shadow-card' : 'text-charcoal/40']">Register</button>
        </div>

        <!-- LOGIN -->
        <form v-if="mode==='login'" @submit.prevent="doLogin" class="space-y-4">
          <div>
            <label class="input-label">Email</label>
            <input v-model="lForm.email" type="email" class="input-field" placeholder="your@email.com" required/>
          </div>
          <div>
            <label class="input-label">Password</label>
            <div class="relative">
              <input v-model="lForm.password" :type="showPw ? 'text' : 'password'" class="input-field pr-10" placeholder="••••••••" required/>
              <button type="button" @click="showPw=!showPw" class="absolute right-3 top-1/2 -translate-y-1/2 text-charcoal/30 hover:text-navy transition">
                <svg v-if="!showPw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>
          <div v-if="lError" class="bg-red-50 border border-red-200 text-red-600 text-sm px-3 py-2.5 rounded-xl flex items-center gap-2">⚠️ {{ lError }}</div>
          <button type="submit" class="btn-lime w-full py-3 text-[15px]" :disabled="logging">
            <svg v-if="logging" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
            {{ logging ? 'Signing in…' : 'Sign In' }}
          </button>
          <div class="text-center pt-3 border-t border-navy/[0.06]">
            <p class="text-[11px] text-charcoal/35">Default admin: <span class="font-mono text-navy font-semibold">admin@pe.adnu.edu.ph</span> / <span class="font-mono text-navy font-semibold">pe_admin_2024</span></p>
          </div>
        </form>

        <!-- REGISTER -->
        <form v-else @submit.prevent="doRegister" class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div class="col-span-2">
              <label class="input-label">Full Name *</label>
              <input v-model="rForm.name" class="input-field" placeholder="Juan Dela Cruz" required/>
            </div>
            <div class="col-span-2">
              <label class="input-label">Email *</label>
              <input v-model="rForm.email" type="email" class="input-field" placeholder="your@email.com" required/>
            </div>
            <div>
              <label class="input-label">Student ID</label>
              <input v-model="rForm.student_id" class="input-field" placeholder="2024-00001"/>
            </div>
            <div>
              <label class="input-label">Year Level</label>
              <select v-model="rForm.year_level" class="input-field">
                <option value="">— Select —</option>
                <option v-for="y in ['1st Year','2nd Year','3rd Year','4th Year']" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="input-label">Department</label>
              <input v-model="rForm.department" class="input-field" placeholder="e.g. College of Engineering"/>
            </div>
            <div>
              <label class="input-label">Password *</label>
              <input v-model="rForm.password" type="password" class="input-field" placeholder="Min 6 chars" required/>
            </div>
            <div>
              <label class="input-label">Confirm *</label>
              <input v-model="rForm.confirmPw" type="password" class="input-field" placeholder="Repeat" required/>
            </div>
          </div>
          <div v-if="rError" class="bg-red-50 border border-red-200 text-red-600 text-sm px-3 py-2.5 rounded-xl flex items-center gap-2">⚠️ {{ rError }}</div>
          <div v-if="rSuccess" class="bg-lime/15 border border-lime-dark/30 text-navy text-sm px-3 py-2.5 rounded-xl flex items-center gap-2 font-semibold">✅ {{ rSuccess }}</div>
          <button type="submit" class="btn-lime w-full py-3 text-[15px]" :disabled="registering">
            {{ registering ? 'Creating Account…' : 'Create Account' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const auth   = useAuthStore()
const mode   = ref('login')
const showPw = ref(false)

const lForm   = ref({ email:'', password:'' })
const lError  = ref('')
const logging = ref(false)

const rForm = ref({ name:'', email:'', student_id:'', year_level:'', department:'', password:'', confirmPw:'' })
const rError = ref('')
const rSuccess = ref('')
const registering = ref(false)

const doLogin = async () => {
  lError.value=''; logging.value=true
  try {
    const r = await api.login({ email: lForm.value.email, password: lForm.value.password })
    auth.setUser(r.data)
    router.push(r.data.role === 'admin' ? '/admin' : '/dashboard')
  } catch(e) {
    lError.value = e.response?.data?.message || 'Login failed'
  } finally { logging.value=false }
}

const doRegister = async () => {
  rError.value=''; rSuccess.value=''
  if (rForm.value.password !== rForm.value.confirmPw) { rError.value='Passwords do not match'; return }
  if (rForm.value.password.length < 6) { rError.value='Password must be at least 6 characters'; return }
  registering.value=true
  try {
    await api.register({ name:rForm.value.name, email:rForm.value.email, student_id:rForm.value.student_id, year_level:rForm.value.year_level, department:rForm.value.department, password:rForm.value.password })
    rSuccess.value='Account created! You can now log in.'
    rForm.value={ name:'', email:'', student_id:'', year_level:'', department:'', password:'', confirmPw:'' }
    setTimeout(() => mode.value='login', 1500)
  } catch(e) {
    rError.value = e.response?.data?.message || 'Registration failed'
  } finally { registering.value=false }
}
</script>