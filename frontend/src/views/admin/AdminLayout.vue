<template>
  <div class="admin-layout">
    <el-container style="min-height:100vh">
      <el-aside width="220px" class="admin-sidebar">
        <div class="sidebar-title">管理后台</div>
        <el-menu :default-active="route.path" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
          <el-menu-item index="/admin">
            <el-icon><DataAnalysis /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/admin/banks">
            <el-icon><Collection /></el-icon>
            <span>题库管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="admin-header">
          <span>👤 {{ authStore.username }} (管理员)</span>
          <el-button size="small" @click="$router.push('/banks')">返回刷题</el-button>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const authStore = useAuthStore()
</script>

<style scoped>
.admin-sidebar { background: #304156; overflow-y: auto; }
.sidebar-title { color: #fff; text-align: center; padding: 20px 0; font-size: 18px; font-weight: bold; }
.admin-header { background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-bottom: 1px solid #e8e8e8; }
</style>
