import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterPage.vue'),
  },
  {
    path: '/admin/login',
    redirect: '/login',
  },
  {
    path: '/banks',
    name: 'BankSelection',
    component: () => import('../views/BankSelection.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/quiz/:bankId',
    name: 'Quiz',
    component: () => import('../views/QuizPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/history/:bankId',
    name: 'ExamHistory',
    component: () => import('../views/ExamHistory.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/admin/Dashboard.vue') },
      { path: 'banks', name: 'BankManage', component: () => import('../views/admin/BankManage.vue') },
      { path: 'banks/:bankId/questions', name: 'QuestionManage', component: () => import('../views/admin/QuestionManage.vue') },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/banks',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const isAdmin = localStorage.getItem('isAdmin') === 'true'

  // 需要管理员 → 未登录则跳登录页
  if (to.meta.requiresAdmin && !token) {
    next('/login')
    return
  }

  // 需要管理员 → 非管理员跳用户页
  if (to.meta.requiresAdmin && !isAdmin) {
    next('/banks')
    return
  }

  // 需要登录但无 token
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 已登录访问登录/注册 → 管理员去 /admin，用户去 /banks
  if ((to.path === '/login' || to.path === '/register') && token) {
    next(isAdmin ? '/admin' : '/banks')
    return
  }

  next()
})

export default router
