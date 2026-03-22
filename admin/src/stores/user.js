import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userInfo = ref(null)

  function readStoredUser() {
    try {
      return JSON.parse(localStorage.getItem('admin_user') || 'null')
    } catch {
      localStorage.removeItem('admin_user')
      return null
    }
  }

  function hydrate() {
    token.value = localStorage.getItem('admin_token') || ''
    userInfo.value = readStoredUser()
  }

  function setLogin(t, user) {
    token.value = t
    userInfo.value = user
    localStorage.setItem('admin_token', t)
    localStorage.setItem('admin_user', JSON.stringify(user))
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
  }

  hydrate()

  return { token, userInfo, hydrate, setLogin, logout }
})
