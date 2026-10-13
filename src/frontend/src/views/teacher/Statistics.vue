<template>
  <div class="page">
    <h2 class="page-title">成绩统计与分析</h2>

    <div class="panel toolbar">
      <select v-model="filters.course_id">
        <option value="">选择课程</option>
        <option v-for="c in courses" :key="c.course_id" :value="c.course_id">
          {{ c.course_name }}
        </option>
      </select>
      <input v-model.trim="filters.class" placeholder="班级（可选）" />
      <button @click="loadScores">成绩统计</button>
      <button class="ghost" @click="loadKnowledge">卷面分析</button>
    </div>

    <p v-if="error" class="panel error">{{ error }}</p>

    <div v-if="scores" class="panel">
      <h3>成绩统计</h3>
      <div class="stats">
        <div class="stat"><span class="label">参考人数</span><span class="value">{{ scores.count }}</span></div>
        <div class="stat"><span class="label">平均分</span><span class="value">{{ scores.average }}</span></div>
        <div class="stat"><span class="label">最高分</span><span class="value">{{ scores.max }}</span></div>
        <div class="stat"><span class="label">最低分</span><span class="value">{{ scores.min }}</span></div>
        <div class="stat"><span class="label">及格率</span><span class="value">{{ scores.pass_rate }}%</span></div>
        <div class="stat"><span class="label">优秀率</span><span class="value">{{ scores.excellent_rate }}%</span></div>
      </div>
      <table>
        <thead><tr><th>分数段</th><th>人数</th></tr></thead>
        <tbody>
          <tr v-for="d in scores.distribution" :key="d.range">
            <td>{{ d.range }}</td>
            <td>{{ d.count }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="knowledge" class="panel">
      <h3>卷面分析（按{{ knowledge.dimension === 'chapter' ? '章节' : '知识点' }}）</h3>
      <table>
        <thead><tr><th>名称</th><th>得分率</th><th>错误率</th></tr></thead>
        <tbody>
          <tr v-for="item in knowledge.items" :key="item.name">
            <td>{{ item.name }}</td>
            <td>{{ item.score_rate }}%</td>
            <td>{{ item.error_rate }}%</td>
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
const scores = ref(null)
const knowledge = ref(null)
const error = ref('')

const filters = reactive({ course_id: '', class: '' })

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

function loadScores() {
  run(async () => {
    if (!filters.course_id) throw new Error('请先选择课程')
    const params = { course_id: filters.course_id }
    if (filters.class) params.class = filters.class
    const res = await api.get('/stats/scores', { params })
    scores.value = res.data
  })
}

function loadKnowledge() {
  run(async () => {
    if (!filters.course_id) throw new Error('请先选择课程')
    const params = { course_id: filters.course_id, dimension: 'chapter' }
    if (filters.class) params.class = filters.class
    const res = await api.get('/stats/knowledge', { params })
    knowledge.value = res.data
  })
}

onMounted(() => run(loadCourses))
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.stat {
  background: #fafafa;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 12px;
  color: var(--text-light);
}

.value {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary);
}
</style>
