<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h1>🔐 管理员登录</h1>
      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="管理员账号" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="管理员密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="warning" size="large" :loading="loading" @click="handleLogin" style="width:100%">
            管理员登录
          </el-button>
        </el-form-item>
      </el-form>
      <el-button size="large" @click="$router.push('/login')" style="width:100%">
        返回用户登录
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminLogin } from '../../api/admin'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const { data } = await adminLogin({ username: form.username, password: form.password })
    authStore.token = data.access_token
    authStore.username = data.username
    authStore.isAdmin = data.is_admin
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('isAdmin', data.is_admin)
    router.push('/admin')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.auth-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.auth-card h1 {
  text-align: center;
  color: #E65100;
  font-size: 22px;
  margin-bottom: 30px;
}
</style>
