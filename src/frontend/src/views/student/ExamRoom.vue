<template>
  <div class="page">
    <div v-if="error" class="panel error">{{ error }}</div>

    <template v-else-if="paper">
      <div class="panel exam-head">
        <h2 class="page-title">{{ paper.paper_name }}</h2>
        <div class="meta">
          <span>总分：{{ paper.total_score }}</span>
          <span>时长：{{ paper.duration }} 分钟</span>
          <span class="countdown" :class="{ urgent: remaining <= 60 }">
            剩余时间：{{ timeText }}
          </span>
        </div>
      </div>

      <div class="panel">
        <div v-for="q in paper.questions" :key="q.question_id" class="question">
          <p class="stem">
            {{ q.seq }}.（{{ q.question_type }}，{{ q.score }} 分）{{ q.content }}
          </p>
          <div v-if="q.question_type === '选择'" class="options">
            <label v-for="opt in parseOptions(q.options)" :key="opt.key" class="option">
              <input
                type="radio"
                :name="`q-${q.question_id}`"
                :value="opt.key"
                v-model="answers[q.question_id]"
              />
              <span>{{ opt.key }}. {{ opt.text }}</span>
            </label>
          </div>
          <input
            v-else
            v-model.trim="answers[q.question_id]"
            placeholder="请输入答案"
            class="fill-input"
          />
        </div>
      </div>

      <div class="panel submit-bar">
        <button :disabled="submitting || submitted" @click="onSubmit">
          {{ submitted ? '已交卷' : submitting ? '提交中…' : '交 卷' }}
        </button>
      </div>
    </template>

    <div v-if="result" class="panel result">
      <h3>评阅结果</h3>
      <p class="score-line">
        本次得分：<strong>{{ result.score }}</strong> / {{ result.total_score }}
      </p>
      <table>
        <thead>
          <tr>
            <th>题号</th>
            <th>题型</th>
            <th>你的答案</th>
            <th>正确答案</th>
            <th>得分</th>
            <th>正误</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in result.details" :key="d.question_id">
            <td>{{ d.question_id }}</td>
            <td>{{ d.question_type }}</td>
            <td>{{ d.student_answer || '—' }}</td>
            <td>{{ d.correct_answer }}</td>
            <td>{{ d.score_obtained }}</td>
            <td :class="d.correct ? 'right' : 'wrong'">{{ d.correct ? '正确' : '错误' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import api from '@/api'

const route = useRoute()
const examId = route.params.id

const paper = ref(null)
const answers = reactive({})
const error = ref('')
const submitting = ref(false)
const submitted = ref(false)
const result = ref(null)

const remaining = ref(0)
let timer = null

const timeText = computed(() => {
  const m = Math.floor(remaining.value / 60)
  const s = remaining.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function parseOptions(options) {
  if (!options) return []
  return options.split('|').map((item) => {
    const [key, ...rest] = item.split('.')
    return { key: key.trim(), text: rest.join('.').trim() }
  })
}

async function load() {
  error.value = ''
  try {
    const res = await api.get(`/exams/${examId}/paper`)
    paper.value = res.data
    startTimer(new Date(res.data.end_time).getTime())
  } catch (e) {
    error.value = e.message
    // 若已交卷，尝试直接展示评阅结果
    try {
      const res = await api.get(`/exams/${examId}/result`)
      result.value = res.data
      submitted.value = true
    } catch {
      /* 保持原始错误提示 */
    }
  }
}

function startTimer(deadline) {
  const tick = () => {
    remaining.value = Math.max(0, Math.floor((deadline - Date.now()) / 1000))
    if (remaining.value <= 0) {
      clearInterval(timer)
      onSubmit(true)
    }
  }
  tick()
  timer = setInterval(tick, 1000)
}

async function onSubmit(auto = false) {
  if (submitted.value || submitting.value) return
  if (!auto && !window.confirm('确认交卷？交卷后不可修改。')) return
  submitting.value = true
  try {
    const payload = paper.value.questions.map((q) => ({
      question_id: q.question_id,
      answer: answers[q.question_id] || ''
    }))
    await api.post(`/exams/${examId}/submit`, { answers: payload })
    submitted.value = true
    clearInterval(timer)
    const res = await api.get(`/exams/${examId}/result`)
    result.value = res.data
    paper.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}

onMounted(load)
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.exam-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.meta {
  display: flex;
  gap: 18px;
  font-size: 13px;
  color: var(--text-light);
}

.countdown {
  color: var(--primary);
  font-weight: 600;
}

.countdown.urgent {
  color: #f56c6c;
}

.question {
  padding: 14px 0;
  border-bottom: 1px dashed var(--border);
}

.question:last-child {
  border-bottom: none;
}

.stem {
  margin: 0 0 10px;
  line-height: 1.6;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.option input {
  width: auto;
}

.fill-input {
  max-width: 320px;
}

.submit-bar {
  text-align: center;
}

.result .score-line {
  font-size: 16px;
}

.right {
  color: #67c23a;
}

.wrong {
  color: #f56c6c;
}
</style>
