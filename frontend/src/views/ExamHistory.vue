<template>
  <div class="page-container">
    <NavBar />
    <div class="card-container" style="margin-top:20px">
      <div class="header-row">
        <h2>模拟考试记录</h2>
        <el-button @click="$router.back()">返回</el-button>
      </div>

      <el-empty v-if="records.length === 0" description="暂无模拟考试记录" />

      <el-timeline v-else>
        <el-timeline-item
          v-for="r in records"
          :key="r.exam_record_id"
          :timestamp="r.time"
          placement="top"
        >
          <el-card>
            <p>得分：<strong :style="{color: scoreColor(r.score)}">{{ r.score }}</strong> 分 (满分 100 分)</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '../components/NavBar.vue'
import { getRandomRecords } from '../api/progress'

const route = useRoute()
const bankId = route.params.bankId
const records = ref([])

onMounted(async () => {
  const { data } = await getRandomRecords(bankId)
  records.value = data
})

function scoreColor(s) {
  if (s >= 80) return '#4CAF50'
  if (s >= 60) return '#FF9800'
  return '#f44336'
}
</script>

<style scoped>
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
