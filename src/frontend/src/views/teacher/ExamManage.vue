<template>
  <div class="page">
    <h2 class="page-title">考试安排</h2>

    <p v-if="error" class="panel error">{{ error }}</p>

    <form class="panel grid-form" @submit.prevent="createExam">
      <select v-model="form.paper_id" required>
        <option value="" disabled>选择试卷</option>
        <option v-for="p in papers" :key="p.paper_id" :value="p.paper_id">
          {{ p.paper_name }}（{{ p.course_name }}）
        </option>
      </select>
      <input v-model.trim="form.class" placeholder="应考班级" required />
      <label class="dt">
        开始时间
        <input v-model="form.start_time" type="datetime-local" required />
      </label>
      <label class="dt">
        结束时间
        <input v-model="form.end_time" type="datetime-local" required />
      </label>
      <button type="submit">安排考试</button>
    </form>

    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>考试编号</th><th>试卷</th><th>课程</th><th>班级</th>
            <th>开始时间</th><th>结束时间</th><th>时长</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in exams" :key="e.exam_id">
            <td>{{ e.exam_id }}</td>
            <td>{{ e.paper_name }}</td>
            <td>{{ e.course_name }}</td>
            <td>{{ e.class }}</td>
            <td>{{ e.start_time }}</td>
            <td>{{ e.end_time }}</td>
            <td>{{ e.duration }} 分钟</td>
          </tr>
          <tr v-if="!exams.length">
            <td colspan="7" class="muted">暂无考试安排</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import api from '@/api'

const papers = ref([])
const exams = ref([])
const error = ref('')

const form = reactive({ paper_id: '', class: '', start_time: '', end_time: '' })

async function run(task) {
  error.value = ''
  try {
    await task()
  } catch (e) {
    error.value = e.message
  }
}

async function loadPapers() {
  const res = await api.get('/papers')
  papers.value = res.data
}

async function loadExams() {
  const res = await api.get('/exams')
  exams.value = res.data
}

function createExam() {
  run(async () => {
    await api.post('/exams', {
      paper_id: form.paper_id,
      class: form.class,
      start_time: form.start_time.replace('T', ' '),
      end_time: form.end_time.replace('T', ' ')
    })
    Object.assign(form, { paper_id: '', class: '', start_time: '', end_time: '' })
    await loadExams()
  })
}

onMounted(() =>
  run(async () => {
    await loadPapers()
    await loadExams()
  })
)
</script>

<style scoped>
.grid-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
  align-items: end;
}

.dt {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--text-light);
}
</style>
