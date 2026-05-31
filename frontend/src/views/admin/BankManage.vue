<template>
  <div>
    <div class="header-row">
      <h3>题库管理</h3>
      <div style="display:flex;gap:8px">
        <el-button type="success" @click="showPdfDialog = true">
          <el-icon><Upload /></el-icon> PDF 提取题目
        </el-button>
        <el-button type="primary" @click="openBankDialog(null)">新增题库</el-button>
      </div>
    </div>

    <el-table :data="banks" border stripe v-loading="loading" empty-text="暂无题库">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="题库名称" min-width="150" />
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      <el-table-column prop="question_count" label="题目数" width="100" />
      <el-table-column label="操作" width="320">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="$router.push(`/admin/banks/${row.id}/questions`)">管理题目</el-button>
          <el-button size="small" @click="openBankDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 题库新增/编辑弹窗 -->
    <el-dialog :title="bankDialogTitle" v-model="bankDialogVisible" width="500px">
      <el-form :model="bankForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="bankForm.name" placeholder="题库名称" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="bankForm.description" type="textarea" placeholder="题库描述" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bankDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBankSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- PDF 上传弹窗 -->
    <el-dialog title="PDF 提取题目" v-model="showPdfDialog" width="800px" top="5vh" style="max-height:90vh" @close="resetPdfState">
      <el-steps :active="pdfStep" finish-status="success" style="margin-bottom:24px">
        <el-step title="上传PDF" />
        <el-step title="预览提取结果" />
        <el-step title="导入题库" />
      </el-steps>

      <!-- Step 1: 上传 -->
      <div v-if="pdfStep === 0">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".pdf"
          :on-change="handlePdfChange"
          :on-exceed="() => ElMessage.warning('仅支持上传一个PDF文件')"
          drag
        >
          <el-icon :size="48"><UploadFilled /></el-icon>
          <div style="margin-top:12px">将 PDF 文件拖到此处，或点击上传</div>
          <template #tip>
            <div style="margin-top:8px;color:#999">
              PDF 中应包含格式规范的题目（支持选择题、判断题的自动识别）
            </div>
          </template>
        </el-upload>
        <div style="text-align:center;margin-top:20px">
          <el-button type="primary" :loading="pdfLoading" :disabled="!pdfFile" @click="parsePdf">开始解析</el-button>
        </div>
      </div>

      <!-- Step 2: 预览 -->
      <div v-if="pdfStep === 1" style="max-height:55vh;overflow-y:auto">
        <el-alert :title="`共提取 ${extractedTotal} 道题目（选择题 ${extractedChoices} / 判断题 ${extractedTF}）`"
          type="success" :closable="false" style="margin-bottom:16px" />

        <el-tabs v-if="extractedTotal > 0">
          <el-tab-pane :label="`选择题 (${extractedChoices})`" v-if="extractedChoices > 0">
            <div v-for="(q, i) in extractedData.choice_questions" :key="'c'+i" class="preview-item">
              <strong>{{ i + 1 }}. {{ q.question_text }}</strong>
              <p v-for="(o, oi) in q.options" :key="oi">{{ labels[oi] }}. {{ o }}</p>
              <p class="answer">答案: {{ formatAnswer(q.answer) }}</p>
            </div>
          </el-tab-pane>
          <el-tab-pane :label="`判断题 (${extractedTF})`" v-if="extractedTF > 0">
            <div v-for="(q, i) in extractedData.true_false_questions" :key="'t'+i" class="preview-item">
              <strong>{{ i + 1 }}. {{ q.question_text }}</strong>
              <p class="answer">答案: {{ q.answer === 0 ? '正确' : '错误' }}</p>
            </div>
          </el-tab-pane>
        </el-tabs>

        <el-empty v-else description="未能从PDF中提取到题目，请检查PDF格式" />

        <div style="text-align:center;margin-top:20px">
          <el-button @click="pdfStep = 0">重新上传</el-button>
          <el-button type="primary" :disabled="extractedTotal === 0" @click="pdfStep = 2">选择导入方式</el-button>
        </div>
      </div>

      <!-- Step 3: 导入 -->
      <div v-if="pdfStep === 2">
        <el-form label-width="100px">
          <el-form-item label="导入方式">
            <el-radio-group v-model="importMode">
              <el-radio value="existing">添加到现有题库</el-radio>
              <el-radio value="new">创建新题库</el-radio>
            </el-radio-group>
          </el-form-item>

          <template v-if="importMode === 'existing'">
            <el-form-item label="选择题库">
              <el-select v-model="importTargetBankId" placeholder="请选择题库" style="width:100%">
                <el-option v-for="b in banks" :key="b.id" :label="`${b.name} (${b.question_count}题)`" :value="b.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="题目类型">
              <el-checkbox-group v-model="importTypes">
                <el-checkbox value="choice" :disabled="extractedChoices === 0">选择题 ({{ extractedChoices }})</el-checkbox>
                <el-checkbox value="tf" :disabled="extractedTF === 0">判断题 ({{ extractedTF }})</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </template>

          <template v-if="importMode === 'new'">
            <el-form-item label="题库名称"><el-input v-model="newBankName" placeholder="新题库名称" /></el-form-item>
            <el-form-item label="题库描述"><el-input v-model="newBankDesc" placeholder="可选描述" /></el-form-item>
          </template>
        </el-form>

        <div style="text-align:center;margin-top:20px">
          <el-button @click="pdfStep = 1">返回预览</el-button>
          <el-button type="primary" :loading="importLoading" @click="handleImport">确认导入</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminBanks, adminUpdateBank, adminDeleteBank, uploadPdf, importQuestions, createBankWithQuestions } from '../../api/admin'

const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
const banks = ref([])
const loading = ref(false)

// Bank dialog
const bankDialogVisible = ref(false)
const bankDialogTitle = ref('新增题库')
const editingBankId = ref(null)
const bankForm = reactive({ name: '', description: '' })

// PDF dialog
const showPdfDialog = ref(false)
const pdfStep = ref(0)
const pdfFile = ref(null)
const pdfLoading = ref(false)
const extractedData = ref({ choice_questions: [], true_false_questions: [] })
const importMode = ref('existing')
const importTargetBankId = ref(null)
const importTypes = ref(['choice', 'tf'])
const newBankName = ref('')
const newBankDesc = ref('')
const importLoading = ref(false)

const extractedChoices = computed(() => extractedData.value.choice_questions?.length || 0)
const extractedTF = computed(() => extractedData.value.true_false_questions?.length || 0)
const extractedTotal = computed(() => extractedChoices.value + extractedTF.value)

async function fetchBanks() {
  loading.value = true
  const { data } = await getAdminBanks()
  banks.value = data
  loading.value = false
}

function openBankDialog(bank) {
  if (bank) {
    bankDialogTitle.value = '编辑题库'
    editingBankId.value = bank.id
    bankForm.name = bank.name
    bankForm.description = bank.description
  } else {
    bankDialogTitle.value = '新增题库'
    editingBankId.value = null
    bankForm.name = ''
    bankForm.description = ''
  }
  bankDialogVisible.value = true
}

async function handleBankSave() {
  if (!bankForm.name) { ElMessage.warning('请输入题库名称'); return }
  if (editingBankId.value) {
    await adminUpdateBank(editingBankId.value, bankForm.name, bankForm.description)
    ElMessage.success('题库已更新')
  } else {
    // create via existing API
    const { default: api } = await import('../../api/index')
    await api.post('/banks/', { name: bankForm.name, description: bankForm.description })
    ElMessage.success('题库已创建')
  }
  bankDialogVisible.value = false
  fetchBanks()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除题库「${row.name}」及其所有题目吗？此操作不可撤销。`, '确认删除', { type: 'warning', confirmButtonText: '确定删除' })
  } catch { return }
  await adminDeleteBank(row.id)
  ElMessage.success('题库已删除')
  fetchBanks()
}

function formatAnswer(ans) {
  if (Array.isArray(ans)) return ans.map(i => labels[i]).join(', ')
  return labels[ans] ?? ans
}

// PDF
function handlePdfChange(file) {
  pdfFile.value = file.raw
}

function resetPdfState() {
  pdfStep.value = 0
  pdfFile.value = null
  extractedData.value = { choice_questions: [], true_false_questions: [] }
}

async function parsePdf() {
  if (!pdfFile.value) return
  pdfLoading.value = true
  try {
    const { data } = await uploadPdf(pdfFile.value)
    extractedData.value = data
    pdfStep.value = 1
  } finally {
    pdfLoading.value = false
  }
}

async function handleImport() {
  let questionsToImport = []
  if (importMode.value === 'existing') {
    if (!importTargetBankId.value) { ElMessage.warning('请选择目标题库'); return }
    if (importTypes.value.includes('choice')) questionsToImport.push(...extractedData.value.choice_questions)
    if (importTypes.value.includes('tf')) questionsToImport.push(...extractedData.value.true_false_questions)
    if (questionsToImport.length === 0) { ElMessage.warning('请选择要导入的题目类型'); return }
  } else {
    if (!newBankName.value.trim()) { ElMessage.warning('请输入新题库名称'); return }
    questionsToImport = [
      ...extractedData.value.choice_questions,
      ...extractedData.value.true_false_questions,
    ]
  }

  importLoading.value = true
  try {
    if (importMode.value === 'existing') {
      const { data } = await importQuestions(importTargetBankId.value, questionsToImport)
      ElMessage.success(`成功导入 ${data.imported} 道题目到题库「${data.bank_name}」`)
    } else {
      const { data } = await createBankWithQuestions(newBankName.value, newBankDesc.value, questionsToImport)
      ElMessage.success(`成功创建题库「${data.bank_name}」并导入 ${data.imported} 道题目`)
    }
    showPdfDialog.value = false
    resetPdfState()
    fetchBanks()
  } finally {
    importLoading.value = false
  }
}

onMounted(fetchBanks)
</script>

<style scoped>
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }

.preview-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #fafafa;
  border-radius: 6px;
  border-left: 3px solid #409EFF;
}

.preview-item p {
  margin: 4px 0 4px 12px;
  font-size: 14px;
  color: #555;
}

.preview-item .answer {
  color: #4CAF50;
  font-weight: bold;
}
</style>
