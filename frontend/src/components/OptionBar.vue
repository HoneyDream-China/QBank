<template>
  <div
    class="option-bar"
    :class="{ selected: isSelected, correct: showCorrect, wrong: showWrong, disabled: disabled }"
    @click="handleClick"
  >
    <span class="option-letter">{{ letter }}</span>
    <span class="option-text">{{ text }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  letter: String,
  text: String,
  index: Number,
  selectedIndices: Array,
  correctAnswer: [Number, Array],
  submitted: Boolean,
  disabled: Boolean,
})

const emit = defineEmits(['select'])

const isSelected = computed(() => props.selectedIndices.includes(props.index))
const showCorrect = computed(() => {
  if (!props.submitted) return false
  if (Array.isArray(props.correctAnswer)) return props.correctAnswer.includes(props.index)
  return props.correctAnswer === props.index
})
const showWrong = computed(() => {
  if (!props.submitted || showCorrect.value) return false
  return isSelected.value
})

function handleClick() {
  if (!props.disabled) emit('select', props.index)
}
</script>

<style scoped>
.option-bar {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  margin-bottom: 8px;
  border-radius: 8px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.15s;
  border: 2px solid transparent;
}

.option-bar:hover:not(.disabled) {
  background: #e3f2fd;
}

.option-bar.selected {
  background: #bbdefb;
  border-color: #1976D2;
}

.option-bar.correct {
  background: #c8e6c9;
  border-color: #4CAF50;
}

.option-bar.wrong {
  background: #ffcdd2;
  border-color: #f44336;
}

.option-bar.disabled {
  cursor: default;
  opacity: 0.85;
}

.option-letter {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 16px;
  flex-shrink: 0;
}

.correct .option-letter { background: #4CAF50; color: #fff; }
.wrong .option-letter { background: #f44336; color: #fff; }
.selected .option-letter { background: #1976D2; color: #fff; }

.option-text { font-size: 15px; line-height: 1.5; }
</style>
