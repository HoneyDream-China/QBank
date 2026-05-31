<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h1>注册新账号</h1>
      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleRegister">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="账号 (11位以内数字)" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码 (字母/数字/@/.)" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="success" size="large" :loading="loading" @click="handleRegister" style="width:100%">
            确认注册
          </el-button>
        </el-form-item>
      </el-form>
      <el-button size="large" @click="$router.push('/login')" style="width:100%">
        返回登录
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { pattern: /^\d{1,11}$/, message: '账号必须为11位以内的纯数字', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9@.]+$/, message: '密码仅限数字、字母和@、.', trigger: 'blur' },
  ],
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.register(form.username, form.password)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
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
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.auth-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.auth-card h1 {
  text-align: center;
  color: #2E7D32;
  font-size: 22px;
  margin-bottom: 30px;
}
</style>
