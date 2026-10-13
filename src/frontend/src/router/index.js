import { createRouter, createWebHashHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
      {
        path: 'admin/users',
        name: 'admin-users',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { roles: ['admin'] }
      },
      {
        path: 'teacher/questions',
        name: 'teacher-questions',
        component: () => import('@/views/teacher/QuestionManage.vue'),
        meta: { roles: ['teacher'] }
      },
      {
        path: 'teacher/papers',
        name: 'teacher-papers',
        component: () => import('@/views/teacher/PaperManage.vue'),
        meta: { roles: ['teacher'] }
      },
      {
        path: 'teacher/exams',
        name: 'teacher-exams',
        component: () => import('@/views/teacher/ExamManage.vue'),
        meta: { roles: ['teacher'] }
      },
      {
        path: 'teacher/statistics',
        name: 'teacher-statistics',
        component: () => import('@/views/teacher/Statistics.vue'),
        meta: { roles: ['teacher'] }
      },
      {
        path: 'student/exams',
        name: 'student-exams',
        component: () => import('@/views/student/ExamList.vue'),
        meta: { roles: ['student'] }
      },
      {
        path: 'student/exam/:id',
        name: 'student-exam-room',
        component: () => import('@/views/student/ExamRoom.vue'),
        meta: { roles: ['student'] }
      },
      {
        path: 'scores',
        name: 'scores',
        component: () => import('@/views/ScoreQuery.vue'),
        meta: { roles: ['teacher', 'student'] }
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/Profile.vue')
      }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn) {
    return { name: 'login' }
  }
  if (to.meta.roles && !to.meta.roles.includes(auth.role)) {
    return { name: 'dashboard' }
  }
  if (to.name === 'login' && auth.isLoggedIn) {
    return { name: 'dashboard' }
  }
  return true
})

export default router
