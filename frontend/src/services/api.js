import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'https://borrowing-system-xdy6.onrender.com/api'

const http = axios.create({ baseURL: BASE })

// Attach token kung meron
http.interceptors.request.use(cfg => {
  const user = JSON.parse(localStorage.getItem('pe_user') || 'null')
  // No JWT in this backend - uses session-based user_id
  return cfg
})

export default {
  // ── Auth ──────────────────────────────────────────
  register:      (d)      => http.post('/register', d),
  login:         (d)      => http.post('/login', d),
  getProfile:    (id)     => http.get(`/profile/${id}`),
  updateProfile: (id, d)  => http.put(`/profile/${id}`, d),

  // ── Equipment ──────────────────────────────────────
  getEquipment:     (p)     => http.get('/equipment', { params: p }),
  getCategories: () => http.get('/categories'),
  getEquipmentById: (id)    => http.get(`/equipment/${id}`),
  addEquipment:     (d)     => http.post('/equipment', d),
  updateEquipment:  (id, d) => http.put(`/equipment/${id}`, d),
  deleteEquipment:  (id)    => http.delete(`/equipment/${id}`),

  // ── Borrowings ─────────────────────────────────────
  borrow:          (d)      => http.post('/borrow', d),
  returnEquipment: (id, d)  => http.post(`/return/${id}`, d),
  getBorrowings:   (p)      => http.get('/borrowings', { params: p }),
  getBorrowingById:(id)     => http.get(`/borrowings/${id}`),

  // ── Notifications ──────────────────────────────────
  getNotifications: (uid)   => http.get(`/notifications/${uid}`),
  markNotifsRead:   (uid)   => http.post(`/notifications/${uid}/read`),
  getUnreadCount:   (uid)   => http.get(`/notifications/unread-count/${uid}`),

  // ── Stats & Reports ────────────────────────────────
  getStats:  ()  => http.get('/stats'),
  getReport: (p) => http.get('/reports/borrowings', { params: p }),

  // ── Admin ──────────────────────────────────────────
  adminLogin:    (pw) => http.post('/admin/login', { password: pw }),
  adminGetUsers: ()   => http.get('/admin/users'),
  toggleUser:    (id) => http.post(`/admin/users/${id}/toggle`),
  deleteUser:    (id) => http.delete(`/admin/users/${id}`),
}