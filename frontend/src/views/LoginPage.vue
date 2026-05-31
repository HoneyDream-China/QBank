<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h1>宝宝定制刷题系统</h1>

      <!-- 角色选择 -->
      <div class="role-tabs">
        <div
          class="role-tab"
          :class="{ active: role === 'user' }"
          @click="role = 'user'"
        >
          用户登录
        </div>
        <div
          class="role-tab"
          :class="{ active: role === 'admin' }"
          @click="role = 'admin'"
        >
          管理员登录
        </div>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" :placeholder="role === 'admin' ? '管理员账号' : '账号 (11位以内数字)'" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button
            :type="role === 'admin' ? 'warning' : 'primary'"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width:100%"
          >
            {{ role === 'admin' ? '管理员登录' : '安全登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <el-button v-if="role === 'user'" type="success" size="large" @click="$router.push('/register')" style="width:100%">
        账号注册
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { adminLogin } from '../api/admin'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const role = ref('user')

const form = reactive({ username: '', password: '' })

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (role.value === 'user' && !/^\d{1,11}$/.test(value)) {
          callback(new Error('用户账号必须为11位以内的纯数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    if (role.value === 'admin') {
      // 管理员登录
      const { data } = await adminLogin({ username: form.username, password: form.password })
      authStore.token = data.access_token
      authStore.username = data.username
      authStore.isAdmin = data.is_admin
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('isAdmin', data.is_admin)
      router.push('/admin')
    } else {
      // 用户登录
      await authStore.login(form.username, form.password)
      router.push('/banks')
    }
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px 36px 28px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.auth-card h1 {
  text-align: center;
  color: #1976D2;
  font-size: 22px;
  margin-bottom: 20px;
}

.role-tabs {
  display: flex;
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
}

.role-tab {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  color: #999;
  background: #fafafa;
  transition: all 0.2s;
}

.role-tab.active {
  color: #fff;
}

.role-tab:first-child.active {
  background: #2196F3;
}

.role-tab:last-child.active {
  background: #E65100;
}
</style>
