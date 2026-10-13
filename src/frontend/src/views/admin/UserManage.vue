<template>
  <div class="page">
    <h2 class="page-title">用户管理</h2>

    <div class="panel">
      <div class="tabs">
        <button :class="{ active: tab === 'student' }" @click="tab = 'student'">学生管理</button>
        <button :class="{ active: tab === 'teacher' }" @click="tab = 'teacher'">教师管理</button>
      </div>
    </div>

    <p v-if="error" class="panel error">{{ error }}</p>

    <!-- 学生管理 -->
    <template v-if="tab === 'student'">
      <form class="panel grid-form" @submit.prevent="addStudent">
        <input v-model.trim="studentForm.student_id" placeholder="学号（12位）" required />
        <input v-model.trim="studentForm.student_name" placeholder="姓名" required />
        <select v-model="studentForm.gender" required>
          <option value="" disabled>性别</option>
          <option value="男">男</option>
          <option value="女">女</option>
        </select>
        <input v-model.trim="studentForm.major" placeholder="专业" />
        <input v-model.trim="studentForm.class" placeholder="班级" />
        <input v-model.trim="studentForm.username" placeholder="用户名" required />
        <input v-model="studentForm.password" type="password" placeholder="初始密码" required />
        <button type="submit">添加学生</button>
      </form>

      <div class="panel toolbar">
        <input v-model.trim="studentKeyword" placeholder="按姓名搜索" />
        <button class="ghost" @click="loadStudents">刷新</button>
      </div>

      <div class="panel">
        <table>
          <thead>
            <tr>
              <th>学号</th><th>姓名</th><th>性别</th><th>专业</th><th>班级</th><th>用户名</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.student_id">
              <td>{{ s.student_id }}</td>
              <td>{{ s.student_name }}</td>
              <td>{{ s.gender }}</td>
              <td>{{ s.major }}</td>
              <td>{{ s.class }}</td>
              <td>{{ s.username }}</td>
              <td><button class="ghost danger" @click="removeStudent(s)">删除</button></td>
            </tr>
            <tr v-if="!students.length">
              <td colspan="7" class="muted">暂无学生数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- 教师管理 -->
    <template v-else>
      <form class="panel grid-form" @submit.prevent="addTeacher">
        <input v-model.trim="teacherForm.teacher_id" placeholder="工号（8位）" required />
        <input v-model.trim="teacherForm.teacher_name" placeholder="姓名" required />
        <input v-model.trim="teacherForm.username" placeholder="用户名" required />
        <input v-model="teacherForm.password" type="password" placeholder="初始密码" required />
        <select v-model="teacherForm.course_ids" multiple class="course-select">
          <option v-for="c in courses" :key="c.course_id" :value="c.course_id">
            {{ c.course_name }}（{{ c.course_id }}）
          </option>
        </select>
        <button type="submit">添加教师</button>
      </form>

      <div class="panel toolbar">
        <input v-model.trim="teacherKeyword" placeholder="按姓名搜索" />
        <button class="ghost" @click="loadTeachers">刷新</button>
      </div>

      <div class="panel">
        <table>
          <thead>
            <tr><th>工号</th><th>姓名</th><th>用户名</th><th>教授课程</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="t in teachers" :key="t.teacher_id">
              <td>{{ t.teacher_id }}</td>
              <td>{{ t.teacher_name }}</td>
              <td>{{ t.username }}</td>
              <td>{{ t.courses.map((c) => c.course_name).join('、') || '—' }}</td>
              <td><button class="ghost danger" @click="removeTeacher(t)">删除</button></td>
            </tr>
            <tr v-if="!teachers.length">
              <td colspan="5" class="muted">暂无教师数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import api from '@/api'

const tab = ref('student')
const error = ref('')

const courses = ref([])
const students = ref([])
const teachers = ref([])
const studentKeyword = ref('')
const teacherKeyword = ref('')

const studentForm = reactive({
  student_id: '',
  student_name: '',
  gender: '',
  major: '',
  class: '',
  username: '',
  password: ''
})
const teacherForm = reactive({
  teacher_id: '',
  teacher_name: '',
  username: '',
  password: '',
  course_ids: []
})

function reset(obj) {
  Object.keys(obj).forEach((key) => {
    obj[key] = Array.isArray(obj[key]) ? [] : ''
  })
}

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

async function loadStudents() {
  const res = await api.get('/students', { params: { keyword: studentKeyword.value } })
  students.value = res.data
}

async function loadTeachers() {
  const res = await api.get('/teachers', { params: { keyword: teacherKeyword.value } })
  teachers.value = res.data
}

function addStudent() {
  run(async () => {
    await api.post('/students', { ...studentForm })
    reset(studentForm)
    await loadStudents()
  })
}

function removeStudent(s) {
  if (!window.confirm(`确认删除学生 ${s.student_name}？`)) return
  run(async () => {
    await api.delete(`/students/${s.student_id}`)
    await loadStudents()
  })
}

function addTeacher() {
  run(async () => {
    await api.post('/teachers', { ...teacherForm })
    reset(teacherForm)
    await loadTeachers()
  })
}

function removeTeacher(t) {
  if (!window.confirm(`确认删除教师 ${t.teacher_name}？`)) return
  run(async () => {
    await api.delete(`/teachers/${t.teacher_id}`)
    await loadTeachers()
  })
}

onMounted(() =>
  run(async () => {
    await loadCourses()
    await loadStudents()
    await loadTeachers()
  })
)
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 10px;
}

.tabs button {
  background: #f0f2f5;
  color: var(--text);
}

.tabs button.active {
  background: var(--primary);
  color: #fff;
}

.grid-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  align-items: center;
}

.course-select {
  height: 76px;
}

.danger {
  border-color: #f56c6c;
  color: #f56c6c;
}
</style>
