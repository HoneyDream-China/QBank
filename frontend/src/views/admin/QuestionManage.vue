<template>
  <div>
    <div class="header-row">
      <h3>题目管理 — {{ bankName }}</h3>
      <div style="display:flex;gap:8px">
        <el-button @click="$router.push('/admin/banks')">返回题库列表</el-button>
        <el-button type="primary" @click="openDialog(null)">新增题目</el-button>
      </div>
    </div>

    <el-table :data="questions" border stripe v-loading="loading" max-height="580">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="question_text" label="题目" min-width="280" show-overflow-tooltip />
      <el-table-column label="答案" width="130">
        <template #default="{ row }">{{ formatAnswer(row.answer) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 题目编辑弹窗 -->
    <el-dialog :title="isEdit ? '编辑题目' : '新增题目'" v-model="dialogVisible" width="750px" top="3vh" @close="resetForm">
      <el-form :model="form" label-width="80px">
        <el-form-item label="题型">
          <el-radio-group v-model="qType">
            <el-radio value="single">单选题</el-radio>
            <el-radio value="multi">多选题</el-radio>
            <el-radio value="tf">判断题</el-radio>
            <el-radio value="fill">填空题</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="题目内容">
          <el-input v-model="form.question_text" type="textarea" :rows="2" placeholder="请输入题目内容" />
        </el-form-item>

        <!-- 选择题选项 -->
        <el-form-item label="选项" v-if="qType === 'single' || qType === 'multi'">
          <div v-for="(opt, i) in form.options" :key="i" style="display:flex;gap:8px;margin-bottom:6px;align-items:center">
            <el-tag size="small" style="min-width:28px;text-align:center">{{ labels[i] }}</el-tag>
            <el-input v-model="form.options[i]" :placeholder="`选项 ${labels[i]}`" />
            <el-button size="small" type="danger" :icon="Delete" circle @click="form.options.splice(i, 1)"
              :disabled="form.options.length <= 2 && (qType === 'single' || qType === 'multi')" />
          </div>
          <el-button size="small" @click="form.options.push('')">+ 添加选项</el-button>
        </el-form-item>

        <!-- 选择题 / 判断题 答案 -->
        <el-form-item label="正确答案" v-if="qType !== 'fill'">
          <template v-if="qType === 'single' || qType === 'tf'">
            <el-radio-group v-model="form.singleAnswer">
              <el-radio v-for="(opt, i) in form.options" :key="i" :value="i">{{ labels[i] }}. {{ opt }}</el-radio>
            </el-radio-group>
          </template>
          <template v-if="qType === 'multi'">
            <el-checkbox-group v-model="form.multiAnswer">
              <el-checkbox v-for="(opt, i) in form.options" :key="i" :value="i">{{ labels[i] }}. {{ opt }}</el-checkbox>
            </el-checkbox-group>
          </template>
        </el-form-item>

        <!-- 填空题答案 -->
        <el-form-item label="答案" v-if="qType === 'fill'">
          <el-input v-model="form.fillAnswer" placeholder="填空题的标准答案" />
        </el-form-item>

        <el-form-item label="解析">
          <el-input v-model="form.analysis" type="textarea" :rows="2" placeholder="答案解析（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { getAdminQuestions, getAdminBanks, adminCreateQuestion, adminUpdateQuestion, adminDeleteQuestion } from '../../api/admin'

const route = useRoute()
const bankId = route.params.bankId
const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

const bankName = ref('')
const questions = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const qType = ref('single')
const saving = ref(false)

const defaultForm = () => ({
  question_text: '',
  options: ['', ''],
  singleAnswer: 0,
  multiAnswer: [],
  fillAnswer: '',
  analysis: '',
})

const form = reactive(defaultForm())

function resetForm() {
  Object.assign(form, defaultForm())
  qType.value = 'single'
}

async function fetchAll() {
  loading.value = true
  const [qRes, bRes] = await Promise.all([getAdminQuestions(bankId), getAdminBanks()])
  questions.value = qRes.data
  const bank = bRes.data.find(b => b.id === parseInt(bankId))
  bankName.value = bank?.name || ''
  loading.value = false
}

function formatAnswer(ans) {
  try {
    if (Array.isArray(ans)) return ans.map(i => labels[i]).join(', ')
    if (typeof ans === 'string') return ans
    return labels[ans] ?? String(ans)
  } catch { return String(ans) }
}

function detectQuestionType(q) {
  if (!q.options || q.options.length === 0) return 'fill'
  if (q.options.length === 2 && (q.options[0] === '正确' || q.options[0] === '正确')) return 'tf'
  if (Array.isArray(q.answer)) return 'multi'
  return 'single'
}

function openDialog(q) {
  resetForm()
  if (q) {
    isEdit.value = true
    editId.value = q.id
    form.question_text = q.question_text
    form.options = [...q.options]
    form.analysis = q.analysis || ''
    qType.value = detectQuestionType(q)

    if (qType.value === 'multi') {
      form.multiAnswer = Array.isArray(q.answer) ? [...q.answer] : [q.answer]
    } else if (qType.value === 'fill') {
      form.fillAnswer = typeof q.answer === 'string' ? q.answer : String(q.answer)
    } else {
      form.singleAnswer = typeof q.answer === 'number' ? q.answer : (Array.isArray(q.answer) ? q.answer[0] : 0)
    }
  } else {
    isEdit.value = false
    editId.value = null
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.question_text.trim()) { ElMessage.warning('请输入题目内容'); return }

  let answer
  let options = [...form.options]

  if (qType.value === 'fill') {
    answer = form.fillAnswer
    options = []
  } else if (qType.value === 'tf') {
    options = ['正确', '错误']
    answer = form.singleAnswer
  } else if (qType.value === 'multi') {
    answer = [...form.multiAnswer]
  } else {
    answer = form.singleAnswer
  }

  saving.value = true
  try {
    const payload = {
      question_text: form.question_text,
      options: JSON.stringify(options.filter(o => o.trim() || qType.value === 'fill')),
      answer: JSON.stringify(answer),
      analysis: form.analysis,
    }

    if (isEdit.value) {
      await adminUpdateQuestion(bankId, editId.value, payload)
      ElMessage.success('题目已更新')
    } else {
      await adminCreateQuestion(bankId, payload)
      ElMessage.success('题目已创建')
    }
    dialogVisible.value = false
    fetchAll()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除这道题目吗？', '确认删除', { type: 'warning' })
  } catch { return }
  await adminDeleteQuestion(bankId, row.id)
  ElMessage.success('题目已删除')
  fetchAll()
}

onMounted(fetchAll)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>
