<template>
  <aside class="quiz-sidebar">
    <div class="sidebar-title">📚 刷题导航</div>

    <div
      v-for="item in navItems"
      :key="item.key"
      class="nav-item"
      :class="{ active: item.key === currentMode }"
      @click="item.action"
    >
      <span class="nav-icon">{{ item.icon }}</span>
      <span class="nav-label">{{ item.label }}</span>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  currentMode: String,
  bankId: [String, Number],
})

const router = useRouter()

function switchMode(mode) {
  router.push(`/quiz/${props.bankId}?mode=${mode}`)
}

const navItems = [
  { key: 'seq',    icon: '▶',  label: '顺序刷题',  action: () => switchMode('seq') },
  { key: 'random', icon: '🔀', label: '模拟考试',  action: () => switchMode('random') },
  { key: 'wrong',  icon: '📓', label: '错题复习',  action: () => switchMode('wrong') },
  { key: 'history',icon: '📊', label: '随机记录',  action: () => router.push(`/history/${props.bankId}`) },
  { key: 'switch', icon: '🔄', label: '切换题库',  action: () => router.push('/banks') },
]
</script>

<style scoped>
.quiz-sidebar {
  width: 200px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  padding: 16px 0;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  align-self: flex-start;
}

.sidebar-title {
  font-size: 15px;
  font-weight: bold;
  color: #333;
  padding: 0 16px 16px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  margin: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.nav-item:hover {
  transform: scale(1.06);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  background: #f5f7fa;
  color: #333;
}

.nav-item.active {
  background: #e3f2fd;
  color: #1565C0;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(25,118,210,0.15);
}

.nav-icon {
  font-size: 18px;
  width: 26px;
  text-align: center;
}

.nav-label {
  white-space: nowrap;
}
</style>
