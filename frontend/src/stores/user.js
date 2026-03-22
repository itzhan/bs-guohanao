import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userInfo = ref(null)
  const isLoggedIn = computed(() => !!token.value)

  function readStoredUser() {
    try {
      return JSON.parse(localStorage.getItem('music_user') || 'null')
    } catch {
      localStorage.removeItem('music_user')
      return null
    }
  }

  function hydrate() {
    token.value = localStorage.getItem('music_token') || ''
    userInfo.value = readStoredUser()
  }

  function setLogin(t, user) {
    token.value = t
    userInfo.value = user
    localStorage.setItem('music_token', t)
    localStorage.setItem('music_user', JSON.stringify(user))
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('music_token')
    localStorage.removeItem('music_user')
  }

  function updateUser(user) {
    userInfo.value = user
    localStorage.setItem('music_user', JSON.stringify(user))
  }

  hydrate()

  return { token, userInfo, isLoggedIn, hydrate, setLogin, logout, updateUser }
})
