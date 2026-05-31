<template>
  <div class="analysis" v-if="visible">
    <div class="result-line" :class="isCorrect ? 'correct' : 'wrong'">
      {{ isCorrect ? '回答正确！' : '回答错误！' }}
    </div>
    <div class="correct-answer">
      <strong>正确答案：</strong>
      {{ Array.isArray(correctAnswer) ? correctAnswer.map(i => labels[i]).join('、') : labels[correctAnswer] }}
    </div>
    <div class="analysis-text" v-if="analysis">
      <strong>解析：</strong>{{ analysis }}
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: Boolean,
  isCorrect: Boolean,
  correctAnswer: [Number, Array],
  analysis: String,
})

const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
</script>

<style scoped>
.analysis {
  background: #FFF9C4;
  border-radius: 8px;
  padding: 16px 20px;
  margin-top: 16px;
}

.result-line {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}

.result-line.correct { color: #2E7D32; }
.result-line.wrong { color: #C62828; }

.correct-answer {
  margin-bottom: 8px;
  color: #333;
}

.analysis-text {
  color: #555;
  line-height: 1.6;
}
</style>
