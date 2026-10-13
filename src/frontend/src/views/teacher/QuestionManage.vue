<template>
  <div class="page">
    <h2 class="page-title">试题管理</h2>

    <p v-if="error" class="panel error">{{ error }}</p>

    <form class="panel grid-form" @submit.prevent="addQuestion">
      <select v-model="form.course_id" required>
        <option value="" disabled>选择课程</option>
        <option v-for="c in courses" :key="c.course_id" :value="c.course_id">
          {{ c.course_name }}
        </option>
      </select>
      <select v-model="form.question_type" required>
        <option value="" disabled>题型</option>
        <option value="选择">选择</option>
        <option value="填空">填空</option>
      </select>
      <input v-model.trim="form.chapter" placeholder="章节" />
      <input v-model.trim="form.knowledge_point" placeholder="知识点" />
      <select v-model.number="form.difficulty">
        <option v-for="n in 5" :key="n" :value="n">难度 {{ n }}</option>
      </select>
      <input v-model.trim="form.content" placeholder="题干" required />
      <input
        v-model.trim="form.options"
        placeholder="选项（选择题）：A.xx|B.xx|C.xx|D.xx"
      />
      <input v-model.trim="form.answer" placeholder="正确答案" required />
      <button type="submit">添加试题</button>
    </form>

    <div class="panel toolbar">
      <select v-model="filters.course_id">
        <option value="">全部课程</option>
        <option v-for="c in courses" :key="c.course_id" :value="c.course_id">
          {{ c.course_name }}
        </option>
      </select>
      <select v-model="filters.question_type">
        <option value="">全部题型</option>
        <option value="选择">选择</option>
        <option value="填空">填空</option>
      </select>
      <select v-model="filters.difficulty">
        <option value="">全部难度</option>
        <option v-for="n in 5" :key="n" :value="n">难度 {{ n }}</option>
      </select>
      <input v-model.trim="filters.keyword" placeholder="题干关键词（模糊）" />
      <button @click="loadQuestions">查询</button>
    </div>

    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>ID</th><th>课程</th><th>章节</th><th>知识点</th><th>题型</th>
            <th>题干</th><th>答案</th><th>难度</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="q in questions" :key="q.question_id">
            <td>{{ q.question_id }}</td>
            <td>{{ q.course_name }}</td>
            <td>{{ q.chapter }}</td>
            <td>{{ q.knowledge_point }}</td>
            <td>{{ q.question_type }}</td>
            <td class="ellipsis">{{ q.content }}</td>
            <td>{{ q.answer }}</td>
            <td>{{ q.difficulty }}</td>
            <td><button class="ghost danger" @click="removeQuestion(q)">删除</button></td>
          </tr>
          <tr v-if="!questions.length">
            <td colspan="9" class="muted">暂无试题</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import api from '@/api'

const courses = ref([])
const questions = ref([])
const error = ref('')

const filters = reactive({ course_id: '', question_type: '', difficulty: '', keyword: '' })
const form = reactive({
  course_id: '',
  question_type: '',
  chapter: '',
  knowledge_point: '',
  difficulty: 1,
  content: '',
  options: '',
  answer: ''
})

async function run(task) {
  error.value = ''
  try {
    await task()
  } catch (e) {
    error.value = e.message
  }
}

async function loadCourses() {
  const res = await api.get('/courses')
  courses.value = res.data
}

async function loadQuestions() {
  const params = { ...filters }
  Object.keys(params).forEach((k) => params[k] === '' && delete params[k])
  const res = await api.get('/questions', { params })
  questions.value = res.data
}

function addQuestion() {
  run(async () => {
    const payload = { ...form }
    if (payload.question_type !== '选择') payload.options = null
    await api.post('/questions', payload)
    Object.assign(form, {
      course_id: '',
      question_type: '',
      chapter: '',
      knowledge_point: '',
      difficulty: 1,
      content: '',
      options: '',
      answer: ''
    })
    await loadQuestions()
  })
}

function removeQuestion(q) {
  if (!window.confirm(`确认删除试题 ${q.question_id}？`)) return
  run(async () => {
    await api.delete(`/questions/${q.question_id}`)
    await loadQuestions()
  })
}

onMounted(() =>
  run(async () => {
    await loadCourses()
    await loadQuestions()
  })
)
</script>

<style scoped>
.grid-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
  align-items: center;
}

.ellipsis {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.danger {
  border-color: #f56c6c;
  color: #f56c6c;
}
</style>
