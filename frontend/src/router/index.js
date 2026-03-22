import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('../views/home/Index.vue'), meta: { title: '首页' } },
      { path: 'songs', name: 'Songs', component: () => import('../views/song/List.vue'), meta: { title: '音乐库' } },
      { path: 'song/:id', name: 'SongDetail', component: () => import('../views/song/Detail.vue'), meta: { title: '歌曲详情' } },
      { path: 'recommend', name: 'Recommend', component: () => import('../views/recommend/Index.vue'), meta: { title: '个性化推荐', auth: true } },
      { path: 'user', name: 'User', component: () => import('../views/user/Index.vue'), meta: { title: '个人中心', auth: true } },
    ]
  },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { title: '注册' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || ''} - 音乐推荐系统`
  const userStore = useUserStore()
  userStore.hydrate()

  if (to.meta.auth) {
    if (!userStore.token) return next('/login')
  }
  next()
})

export default router
