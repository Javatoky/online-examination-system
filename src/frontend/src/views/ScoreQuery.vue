<template>
  <div class="page">
    <h2 class="page-title">成绩查询</h2>

    <div v-if="isTeacher" class="panel toolbar">
      <input v-model.trim="filters.course_id" placeholder="课程号" />
      <input v-model.trim="filters.class" placeholder="班级" />
      <input v-model.trim="filters.student_name" placeholder="学生姓名（支持模糊）" />
      <button @click="load">查询</button>
    </div>

    <div class="panel">
      <p v-if="error" class="error">{{ error }}</p>
      <p v-else-if="!rows.length" class="muted">暂无成绩记录</p>
      <table v-else>
        <thead>
          <tr>
            <th>学号</th>
            <th>姓名</th>
            <th>班级</th>
            <th>课程</th>
            <th>试卷</th>
            <th>得分</th>
            <th>提交时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.submission_id">
            <td>{{ row.student_id }}</td>
            <td>{{ row.student_name }}</td>
            <td>{{ row.class }}</td>
            <td>{{ row.course_name }}</td>
            <td>{{ row.paper_name }}</td>
            <td>{{ row.score }} / {{ row.total_score }}</td>
            <td>{{ row.submit_time }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const isTeacher = computed(() => auth.role === 'teacher')

const filters = reactive({ course_id: '', class: '', student_name: '' })
const rows = ref([])
const error = ref('')

async function load() {
  error.value = ''
  try {
    if (isTeacher.value) {
      const res = await api.get('/scores', { params: filters })
      rows.value = res.data
    } else {
      const res = await api.get('/scores/mine')
      rows.value = res.data
    }
  } catch (e) {
    error.value = e.message
    rows.value = []
  }
}

onMounted(load)
</script>
