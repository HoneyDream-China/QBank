<template>
  <div class="sheet">
    <h4>答题卡</h4>
    <div class="sheet-grid">
      <div
        v-for="(item, i) in items"
        :key="i"
        class="sheet-item"
        :class="getClass(i)"
        @click="$emit('jump', i)"
      >
        {{ i + 1 }}
      </div>
    </div>
    <div class="sheet-legend">
      <span><i class="dot current"></i> 当前</span>
      <span><i class="dot correct"></i> 正确</span>
      <span><i class="dot wrong"></i> 错误</span>
      <span><i class="dot answered"></i> 已答</span>
      <span><i class="dot pending"></i> 未答</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  questions: Array,
  currentIndex: Number,
  selections: Object,
  statusMap: Object,
})

defineEmits(['jump'])

const items = computed(() => props.questions || [])

function getClass(i) {
  if (i === props.currentIndex) return 'current'
  const q = props.questions[i]
  if (!q) return ''
  const qId = String(q.id)
  const st = props.statusMap?.[qId]
  if (st === 'correct') return 'correct'
  if (st === 'wrong') return 'wrong'
  if (props.selections?.[qId] && props.selections[qId].length > 0) return 'answered'
  return ''
}
</script>

<style scoped>
.sheet {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.sheet h4 {
  margin-bottom: 12px;
  color: #333;
  font-size: 15px;
  text-align: center;
}

.sheet-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
}

.sheet-item {
  width: 100%;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: #e8e8e8;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  color: #888;
  transition: all 0.2s;
}

.sheet-item:hover {
  transform: scale(1.08);
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}

.sheet-item.current {
  background: #1976D2;
  color: #fff;
  transform: scale(1.1);
  box-shadow: 0 2px 12px rgba(25,118,210,0.3);
}

.sheet-item.correct {
  background: #4CAF50;
  color: #fff;
}

.sheet-item.wrong {
  background: #F44336;
  color: #fff;
}

.sheet-item.answered {
  background: #FFC107;
  color: #fff;
}

.sheet-legend {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 11px;
  color: #888;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 3px;
  vertical-align: middle;
}

.dot.current { background: #1976D2; }
.dot.correct { background: #4CAF50; }
.dot.wrong  { background: #F44336; }
.dot.answered { background: #FFC107; }
.dot.pending { background: #e8e8e8; border: 1px solid #ccc; }
</style>
