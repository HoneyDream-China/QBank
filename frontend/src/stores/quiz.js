import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useQuizStore = defineStore('quiz', () => {
  const mode = ref('seq')
  const questions = ref([])
  const currentIndex = ref(0)
  const selections = ref({})
  const examSubmitted = ref(false)
  const examResults = ref({})
  const wrongResolved = ref(new Set())

  const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
  const totalQuestions = computed(() => questions.value.length)

  function loadQuestions(list, quizMode) {
    questions.value = list
    mode.value = quizMode
    currentIndex.value = 0
    selections.value = {}
    examSubmitted.value = false
    examResults.value = {}
    wrongResolved.value = new Set()
  }

  function setSelection(questionId, selectedIndices) {
    selections.value[questionId] = selectedIndices
  }

  function getSelection(questionId) {
    return selections.value[questionId] || []
  }

  function submitExam(results) {
    examSubmitted.value = true
    examResults.value = results
  }

  return {
    mode, questions, currentIndex, selections, examSubmitted, examResults, wrongResolved,
    currentQuestion, totalQuestions,
    loadQuestions, setSelection, getSelection, submitExam,
  }
})
