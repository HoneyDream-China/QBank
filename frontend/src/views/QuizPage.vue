<template>
  <div class="quiz-page">
    <!-- 左侧导航栏 -->
    <QuizSidebar :current-mode="mode" :bank-id="bankId" />

    <!-- 中间答题区 -->
    <main class="quiz-main" v-if="questions.length > 0">
      <div class="question-header">
        <span class="q-counter">第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
        <el-tag v-if="isMulti" type="warning" size="small">多选题</el-tag>
        <el-tag v-else size="small">单选/判断</el-tag>
        <span class="mode-badge" :class="mode">{{ modeLabel }}</span>
      </div>

      <div class="question-text">{{ currentQuestion?.question_text }}</div>

      <div class="options-area">
        <OptionBar
          v-for="(opt, i) in currentQuestion?.options || []"
          :key="i"
          :letter="labels[i]"
          :text="opt"
          :index="i"
          :selected-indices="currentSelection"
          :correct-answer="currentAnswer"
          :submitted="isSubmitted"
          :disabled="isSubmitted"
          @select="toggleOption"
        />
      </div>

      <AnalysisPanel
        :visible="isSubmitted"
        :is-correct="showCorrect"
        :correct-answer="currentAnswer"
        :analysis="currentQuestion?.analysis || ''"
      />

      <div class="quiz-controls">
        <el-button @click="prevQuestion" :disabled="currentIndex === 0" :icon="ArrowLeft">上一题</el-button>

        <el-button
          v-if="!isSubmitted"
          type="primary"
          :disabled="currentSelection.length === 0"
          @click="handleSubmit"
        >
          {{ mode === 'random' ? '🛑 提交试卷' : '✔ 确定答案' }}
        </el-button>

        <el-button v-else-if="mode === 'random'" type="danger" disabled>试卷已提交</el-button>

        <el-button @click="nextQuestion" :disabled="currentIndex >= questions.length - 1">
          下一题 <el-icon style="margin-left:4px"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </main>

    <!-- 右侧答题卡 -->
    <div class="sheet-wrapper" v-if="questions.length > 0">
      <AnswerSheet
        :questions="questions"
        :current-index="currentIndex"
        :selections="selections"
        :status-map="statusMap"
        @jump="jumpTo"
      />
    </div>

    <!-- 空状态 -->
    <main class="quiz-main quiz-empty" v-else-if="loaded">
      <el-empty :description="mode === 'wrong' ? '错题本空空如也，保持得真棒！' : '题库为空'" />
      <el-button type="primary" @click="$router.push('/banks')">返回题库选择</el-button>
    </main>

    <main class="quiz-main quiz-empty" v-else>
      <el-skeleton :rows="8" animated style="padding:40px" />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import QuizSidebar from '../components/QuizSidebar.vue'
import OptionBar from '../components/OptionBar.vue'
import AnswerSheet from '../components/AnswerSheet.vue'
import AnalysisPanel from '../components/AnalysisPanel.vue'
import { getQuestions } from '../api/questions'
import { submitAnswer, submitExam } from '../api/progress'

const route = useRoute()
const bankId = computed(() => route.params.bankId)
const mode = computed(() => route.query.mode || 'seq')
const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

const modeLabel = computed(() => ({
  seq: '顺序刷题', random: '模拟考试', wrong: '错题复习',
}[mode.value] || ''))

const questions = ref([])
const currentIndex = ref(0)
const selections = ref({})
const submitted = ref({})
const answerResults = ref({})
const examResults = ref({})
const examSubmitted = ref(false)
const loaded = ref(false)

const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
const currentAnswer = computed(() => {
  try { return currentQuestion.value?.answer ?? 0 } catch { return 0 }
})
const isMulti = computed(() => Array.isArray(currentAnswer.value))
const currentSelection = computed(() => selections.value[currentQuestion.value?.id] || [])

const isSubmitted = computed(() => {
  if (mode.value === 'random') return examSubmitted.value
  return !!submitted.value[currentQuestion.value?.id]
})

const showCorrect = computed(() => answerResults.value[currentQuestion.value?.id]?.is_correct || false)

// 构建答题卡状态 map: qId → 'correct' | 'wrong'
const statusMap = computed(() => {
  const map = {}
  if (mode.value === 'random') {
    for (const [qId, r] of Object.entries(examResults.value)) {
      map[qId] = r.is_correct ? 'correct' : 'wrong'
    }
  } else {
    for (const [qId, r] of Object.entries(answerResults.value)) {
      map[qId] = r.is_correct ? 'correct' : 'wrong'
    }
  }
  return map
})

watch(mode, () => { loadQuestions() })
onMounted(() => { loadQuestions() })

async function loadQuestions() {
  loaded.value = false
  selections.value = {}
  submitted.value = {}
  answerResults.value = {}
  examResults.value = {}
  examSubmitted.value = false
  currentIndex.value = 0
  try {
    const { data } = await getQuestions(bankId.value, mode.value)
    questions.value = data
  } finally {
    loaded.value = true
  }
}

function toggleOption(index) {
  if (isSubmitted.value) return
  const qId = currentQuestion.value.id
  const cur = [...(selections.value[qId] || [])]
  if (isMulti.value) {
    const pos = cur.indexOf(index)
    pos >= 0 ? cur.splice(pos, 1) : cur.push(index)
  } else {
    cur.splice(0, cur.length, index)
  }
  selections.value[qId] = cur
}

function jumpTo(idx) { currentIndex.value = idx }
function prevQuestion() { if (currentIndex.value > 0) currentIndex.value-- }
function nextQuestion() {
  if (currentIndex.value < questions.value.length - 1) currentIndex.value++
}

async function handleSubmit() {
  if (mode.value === 'random') {
    await handleExamSubmit()
  } else {
    await handleSingleSubmit()
  }
}

async function handleSingleSubmit() {
  const q = currentQuestion.value
  const userAnswer = isMulti.value ? currentSelection.value : currentSelection.value[0]
  const { data } = await submitAnswer({
    question_id: q.id, bank_id: parseInt(bankId.value),
    user_answer: userAnswer, mode: mode.value,
  })
  submitted.value[q.id] = true
  answerResults.value[q.id] = { is_correct: data.is_correct }
}

async function handleExamSubmit() {
  const unanswered = questions.value.filter(q => {
    const sel = selections.value[q.id]
    return !sel || sel.length === 0
  }).length

  if (unanswered > 0) {
    try {
      await ElMessageBox.confirm(
        `当前还剩 ${unanswered} 题未做，确认提交吗？`,
        '交卷确认',
        { confirmButtonText: '确认提交', cancelButtonText: '继续答题', type: 'warning' },
      )
    } catch { return }
  }

  const answers = {}
  questions.value.forEach(q => {
    const sel = selections.value[q.id] || []
    answers[q.id] = Array.isArray(q.answer) ? sel : (sel[0] ?? -1)
  })

  const { data } = await submitExam({ bank_id: parseInt(bankId.value), answers })
  examSubmitted.value = true
  examResults.value = data.results || {}
  currentIndex.value = 0
  ElMessage.success(`交卷完成！得分：${data.score} 分 (满分 ${data.max_score} 分)`)
}
</script>

<style scoped>
.quiz-page {
  display: flex;
  gap: 20px;
  min-height: 100vh;
  padding: 20px;
  background: #f0f2f5;
  max-width: 1400px;
  margin: 0 auto;
}

/* ===== 中间答题区 ===== */
.quiz-main {
  flex: 1;
  min-width: 0;
  padding: 32px 40px;
}

.quiz-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.q-counter {
  font-size: 14px;
  color: #888;
  font-weight: 500;
}

.mode-badge {
  margin-left: auto;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 20px;
  color: #fff;
  font-weight: 500;
}

.mode-badge.seq    { background: #42A5F5; }
.mode-badge.random { background: #66BB6A; }
.mode-badge.wrong  { background: #EF5350; }

.question-text {
  font-size: 18px;
  font-weight: bold;
  line-height: 1.9;
  margin-bottom: 28px;
  color: #1a1a1a;
  padding: 20px 24px;
  background: #fff;
  border-radius: 10px;
  border-left: 4px solid #1976D2;
}

.options-area {
  margin-bottom: 8px;
}

.quiz-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

/* ===== 右侧答题卡 ===== */
.sheet-wrapper {
  width: 240px;
  flex-shrink: 0;
  padding-top: 4px;
}

@media (max-width: 1000px) {
  .quiz-page { flex-direction: column; padding: 12px; }
  .sheet-wrapper { width: 100%; }
  .quiz-main { padding: 20px 16px; }
}
</style>
