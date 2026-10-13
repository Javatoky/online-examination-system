<template>
  <div class="page">
    <h2 class="page-title">欢迎，{{ auth.displayName }}</h2>

    <div class="panel">
      <p class="muted">当前角色：{{ roleLabel }}</p>
      <p>{{ roleDesc }}</p>
    </div>

    <div class="cards">
      <router-link
        v-for="item in shortcuts"
        :key="item.name"
        :to="{ name: item.name }"
        class="card"
      >
        <span class="card-title">{{ item.label }}</span>
        <span class="card-desc">{{ item.desc }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const CONFIG = {
  admin: {
    label: '管理员',
    desc: '负责维护学生与教师的基本信息，以及个人密码。',
    shortcuts: [
      { name: 'admin-users', label: '用户管理', desc: '学生 / 教师信息维护' },
      { name: 'profile', label: '个人信息', desc: '修改用户名与密码' }
    ]
  },
  teacher: {
    label: '教师',
    desc: '负责试题库维护、组卷、考试安排、成绩统计与查询。',
    shortcuts: [
      { name: 'teacher-questions', label: '试题管理', desc: '选择题 / 填空题维护' },
      { name: 'teacher-papers', label: '组卷管理', desc: '选题组卷与预览' },
      { name: 'teacher-exams', label: '考试安排', desc: '指定班级与考试时间' },
      { name: 'teacher-statistics', label: '成绩统计', desc: '平均分 / 及格率 / 卷面分析' },
      { name: 'scores', label: '成绩查询', desc: '按班级 / 姓名查询' }
    ]
  },
  student: {
    label: '学生',
    desc: '参加在线限时考试，查看自动评阅结果与历史成绩。',
    shortcuts: [
      { name: 'student-exams', label: '在线考试', desc: '进入考试并在线答题' },
      { name: 'scores', label: '成绩查询', desc: '查看本人成绩与评阅详情' }
    ]
  }
}

const current = computed(() => CONFIG[auth.role] || { label: '未知', desc: '', shortcuts: [] })
const roleLabel = computed(() => current.value.label)
const roleDesc = computed(() => current.value.desc)
const shortcuts = computed(() => current.value.shortcuts)
</script>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}

.card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 0.2s, transform 0.2s;
}

.card:hover {
  box-shadow: 0 6px 18px rgba(47, 84, 235, 0.15);
  transform: translateY(-2px);
}

.card-title {
  font-size: 15px;
  font-weight: 600;
}

.card-desc {
  font-size: 13px;
  color: var(--text-light);
}
</style>
