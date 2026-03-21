import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '管理员登录', noAuth: true }
  },
  {
    path: '/',
    component: () => import('../components/AdminLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/dashboard/Index.vue'), meta: { title: '仪表盘' } },
      { path: 'songs', name: 'Songs', component: () => import('../views/song/Index.vue'), meta: { title: '歌曲管理' } },
      { path: 'artists', name: 'Artists', component: () => import('../views/artist/Index.vue'), meta: { title: '歌手管理' } },
      { path: 'genres', name: 'Genres', component: () => import('../views/genre/Index.vue'), meta: { title: '流派管理' } },
      { path: 'users', name: 'Users', component: () => import('../views/user/Index.vue'), meta: { title: '用户管理' } },
      { path: 'comments', name: 'Comments', component: () => import('../views/comment/Index.vue'), meta: { title: '评论管理' } },
      { path: 'logs', name: 'Logs', component: () => import('../views/log/Index.vue'), meta: { title: '操作日志' } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '管理端'} - 音乐推荐系统`
  if (to.meta.noAuth) return next()
  const userStore = useUserStore()
  if (!userStore.token) return next('/login')
  next()
})

export default router
