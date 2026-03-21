import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('music_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('music_user') || 'null'))
  const isLoggedIn = computed(() => !!token.value)

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

  return { token, userInfo, isLoggedIn, setLogin, logout, updateUser }
})
