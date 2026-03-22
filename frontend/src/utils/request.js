import axios from 'axios'
import router from '../router'
import { useUserStore } from '../stores/user'

const request = axios.create({ baseURL: '/api', timeout: 15000 })

request.interceptors.request.use(config => {
  const userStore = useUserStore()
  userStore.hydrate()
  if (userStore.token) config.headers.Authorization = `Bearer ${userStore.token}`
  return config
})

let isRedirecting = false

request.interceptors.response.use(
  res => res.data.code === 200 ? res.data : Promise.reject(new Error(res.data.message || '请求失败')),
  err => {
    if (err.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      if (!isRedirecting && router.currentRoute.value.path !== '/login') {
        isRedirecting = true
        router.replace('/login').finally(() => { isRedirecting = false })
      }
    }
    return Promise.reject(err)
  }
)

export default request
