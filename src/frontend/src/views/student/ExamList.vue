<template>
  <div class="page">
    <h2 class="page-title">在线考试</h2>

    <div class="panel">
      <p v-if="error" class="error">{{ error }}</p>
      <p v-else-if="!exams.length" class="muted">当前班级暂无考试安排</p>
      <table v-else>
        <thead>
          <tr>
            <th>考试编号</th>
            <th>试卷</th>
            <th>课程</th>
            <th>班级</th>
            <th>开始时间</th>
            <th>结束时间</th>
            <th>时长</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="exam in exams" :key="exam.exam_id">
            <td>{{ exam.exam_id }}</td>
            <td>{{ exam.paper_name }}</td>
            <td>{{ exam.course_name }}</td>
            <td>{{ exam.class }}</td>
            <td>{{ exam.start_time }}</td>
            <td>{{ exam.end_time }}</td>
            <td>{{ exam.duration }} 分钟</td>
            <td>
              <button :disabled="!inWindow(exam)" @click="enter(exam)">进入考试</button>
              <span v-if="!inWindow(exam)" class="muted">（不在考试时间窗口内）</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '@/api'

const router = useRouter()
const exams = ref([])
const error = ref('')

function inWindow(exam) {
  const now = Date.now()
  return now >= new Date(exam.start_time).getTime() && now <= new Date(exam.end_time).getTime()
}

function enter(exam) {
  router.push({ name: 'student-exam-room', params: { id: exam.exam_id } })
}

async function load() {
  error.value = ''
  try {
    const res = await api.get('/exams')
    exams.value = res.data
  } catch (e) {
    error.value = e.message
  }
}

onMounted(load)
</script>
