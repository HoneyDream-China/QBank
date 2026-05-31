<template>
  <div class="navbar">
    <div class="nav-left">
      <span class="nav-title">宝宝定制刷题系统</span>
      <span class="nav-user">👤 {{ authStore.username }}</span>
    </div>
    <div class="nav-right">
      <template v-if="currentBankId">
        <el-button size="small" @click="switchMode('seq')" :type="currentMode === 'seq' ? 'primary' : ''">顺序刷题</el-button>
        <el-button size="small" @click="switchMode('random')" :type="currentMode === 'random' ? 'primary' : ''">模拟考试</el-button>
        <el-button size="small" @click="switchMode('wrong')" :type="currentMode === 'wrong' ? 'primary' : ''">错题复习</el-button>
        <el-button size="small" @click="$router.push(`/history/${currentBankId}`)">随机记录</el-button>
        <el-button size="small" @click="$router.push('/banks')">切换题库</el-button>
      </template>
      <el-button v-if="authStore.isAdmin" size="small" type="warning" @click="$router.push('/admin')">管理后台</el-button>
      <el-button size="small" type="danger" @click="handleLogout">退出登录</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const currentBankId = computed(() => route.params.bankId || '')
const currentMode = computed(() => route.query.mode || 'seq')

function switchMode(mode) {
  router.push(`/quiz/${currentBankId.value}?mode=${mode}`)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  flex-wrap: wrap;
  gap: 8px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-title {
  font-size: 18px;
  font-weight: bold;
  color: #1976D2;
}

.nav-user {
  font-size: 14px;
  color: #666;
}

.nav-right {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
