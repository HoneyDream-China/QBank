<template>
  <div class="page-container">
    <NavBar />
    <div class="card-container" style="margin-top:20px">
      <h2 style="margin-bottom:20px;color:#2E7D32">📚 请选择要挑战的题库</h2>

      <el-empty v-if="banks.length === 0" description="暂无可用的题库" />

      <div class="bank-grid">
        <div v-for="bank in banks" :key="bank.id" class="bank-card" @click="goToBank(bank)">
          <div class="bank-icon">📖</div>
          <div class="bank-name">{{ bank.name }}</div>
          <div class="bank-desc">{{ bank.description || '暂无描述' }}</div>
          <div class="bank-stats">共 {{ bank.question_count }} 题</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { getBanks } from '../api/banks'

const router = useRouter()
const banks = ref([])

onMounted(async () => {
  const { data } = await getBanks()
  banks.value = data
})

function goToBank(bank) {
  router.push(`/quiz/${bank.id}?mode=seq`)
}
</script>

<style scoped>
.bank-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.bank-card {
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.bank-card:hover {
  border-color: #4CAF50;
  box-shadow: 0 4px 16px rgba(76,175,80,0.15);
  transform: translateY(-2px);
}

.bank-icon { font-size: 40px; margin-bottom: 12px; }
.bank-name { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 8px; }
.bank-desc { font-size: 13px; color: #999; margin-bottom: 12px; }
.bank-stats { font-size: 13px; color: #4CAF50; }
</style>
