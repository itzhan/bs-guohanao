import axios from 'axios'

const request = axios.create({ baseURL: '/api', timeout: 15000 })

request.interceptors.request.use(config => {
  const token = localStorage.getItem('music_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  res => res.data.code === 200 ? res.data : Promise.reject(new Error(res.data.message || '请求失败')),
  err => {
    if (err.response?.status === 401) { localStorage.removeItem('music_token'); localStorage.removeItem('music_user'); window.location.href = '/login' }
    return Promise.reject(err)
  }
)

export default request
