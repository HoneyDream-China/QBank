import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, register as registerApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const isAdmin = ref(localStorage.getItem('isAdmin') === 'true')

  async function login(usernameInput, password) {
    const { data } = await loginApi({ username: usernameInput, password })
    token.value = data.access_token
    username.value = data.username
    isAdmin.value = data.is_admin
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('isAdmin', data.is_admin)
  }

  async function register(usernameInput, password) {
    await registerApi({ username: usernameInput, password })
  }

  function logout() {
    token.value = ''
    username.value = ''
    isAdmin.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('isAdmin')
  }

  return { token, username, isAdmin, login, register, logout }
})
