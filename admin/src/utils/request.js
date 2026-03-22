import axios from 'axios'
import { useUserStore } from '../stores/user'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.request.use(config => {
  const userStore = useUserStore()
  userStore.hydrate()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

let isRedirecting = false

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) {
      return res
    }
    if (res.code === 401) {
      const userStore = useUserStore()
      userStore.logout()
      if (!isRedirecting && router.currentRoute.value.path !== '/login') {
        isRedirecting = true
        router.replace('/login').finally(() => { isRedirecting = false })
      }
    }
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  error => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      if (!isRedirecting && router.currentRoute.value.path !== '/login') {
        isRedirecting = true
        router.replace('/login').finally(() => { isRedirecting = false })
      }
    }
    return Promise.reject(error)
  }
)

export default request
