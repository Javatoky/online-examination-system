<template>
  <div class="page">
    <h2 class="page-title">组卷管理</h2>

    <p v-if="error" class="panel error">{{ error }}</p>

    <div class="panel">
      <h3>生成试卷</h3>
      <div class="grid-form">
        <select v-model="draft.course_id" @change="loadCourseQuestions">
          <option value="" disabled>选择课程</option>
          <option v-for="c in courses" :key="c.course_id" :value="c.course_id">
            {{ c.course_name }}
          </option>
        </select>
        <input v-model.trim="draft.paper_name" placeholder="试卷名称" />
        <input v-model.number="draft.duration" type="number" min="1" placeholder="考试时长（分钟）" />
        <span class="muted">已选 {{ selectedCount }} 题，总分 {{ draftTotal }}</span>
        <button :disabled="!canCreate" @click="createPaper">生成试卷</button>
      </div>

      <table v-if="draft.course_id" class="picker">
        <thead>
          <tr><th>选择</th><th>ID</th><th>题型</th><th>题干</th><th>章节</th><th>难度</th><th>分值</th></tr>
        </thead>
        <tbody>
          <tr v-for="q in courseQuestions" :key="q.question_id">
            <td><input type="checkbox" :value="q.question_id" v-model="selected" /></td>
            <td>{{ q.question_id }}</td>
            <td>{{ q.question_type }}</td>
            <td class="ellipsis">{{ q.content }}</td>
            <td>{{ q.chapter }}</td>
            <td>{{ q.difficulty }}</td>
            <td>
              <input v-model.number="scores[q.question_id]" type="number" min="1" class="score-input" />
            </td>
          </tr>
          <tr v-if="!courseQuestions.length">
            <td colspan="7" class="muted">该课程暂无试题，请先在「试题管理」中录入</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h3>我的试卷</h3>
      <table>
        <thead>
          <tr><th>ID</th><th>名称</th><th>课程</th><th>题量</th><th>总分</th><th>时长</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in papers" :key="p.paper_id">
            <td>{{ p.paper_id }}</td>
            <td>{{ p.paper_name }}</td>
            <td>{{ p.course_name }}</td>
            <td>{{ p.question_count }}</td>
            <td>{{ p.total_score }}</td>
            <td>{{ p.duration }} 分钟</td>
            <td>
              <button class="ghost" @click="preview(p)">预览</button>
              <button class="ghost danger" @click="removePaper(p)">删除</button>
            </td>
          </tr>
          <tr v-if="!papers.length">
            <td colspan="7" class="muted">暂无试卷</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="detail" class="panel">
      <h3>试卷预览：{{ detail.paper_name }}（总分 {{ detail.total_score }}）</h3>
      <table>
        <thead>
          <tr><th>题序</th><th>题型</th><th>题干</th><th>选项</th><th>答案</th><th>分值</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in detail.items" :key="item.question_id">
            <td>{{ item.seq }}</td>
            <td>{{ item.question_type }}</td>
            <td>{{ item.content }}</td>
            <td>{{ item.options || '—' }}</td>
            <td>{{ item.answer }}</td>
            <td>{{ item.score }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import api from '@/api'

const courses = ref([])
const papers = ref([])
const courseQuestions = ref([])
const error = ref('')

const draft = reactive({ course_id: '', paper_name: '', duration: 60 })
const selected = ref([])
const scores = reactive({})
const detail = ref(null)

const selectedCount = computed(() => selected.value.length)
const draftTotal = computed(() =>
  selected.value.reduce((sum, id) => sum + (Number(scores[id]) || 0), 0)
)
const canCreate = computed(
  () => draft.course_id && draft.paper_name && draft.duration > 0 && selected.value.length > 0
)

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

async function loadPapers() {
  const res = await api.get('/papers')
  papers.value = res.data
}

async function loadCourseQuestions() {
  selected.value = []
  const res = await api.get('/questions', { params: { course_id: draft.course_id } })
  courseQuestions.value = res.data
  res.data.forEach((q) => {
    scores[q.question_id] = 10
  })
}

function createPaper() {
  run(async () => {
    const items = selected.value.map((id, index) => ({
      question_id: id,
      seq: index + 1,
      score: Number(scores[id]) || 0
    }))
    await api.post('/papers', { ...draft, items })
    draft.course_id = ''
    draft.paper_name = ''
    draft.duration = 60
    selected.value = []
    courseQuestions.value = []
    await loadPapers()
  })
}

function preview(p) {
  run(async () => {
    const res = await api.get(`/papers/${p.paper_id}`)
    detail.value = res.data
  })
}

function removePaper(p) {
  if (!window.confirm(`确认删除试卷「${p.paper_name}」？`)) return
  run(async () => {
    await api.delete(`/papers/${p.paper_id}`)
    if (detail.value?.paper_id === p.paper_id) detail.value = null
    await loadPapers()
  })
}

onMounted(() =>
  run(async () => {
    await loadCourses()
    await loadPapers()
  })
)
</script>

<style scoped>
.grid-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}

.picker {
  margin-top: 10px;
}

.score-input {
  width: 70px;
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
