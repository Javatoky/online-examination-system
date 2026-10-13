<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-title">在线考试系统</span>
        <span class="brand-sub">数据库原理实践</span>
      </div>
      <nav>
        <router-link
          v-for="item in menus"
          :key="item.name"
          :to="{ name: item.name }"
          class="nav-item"
          active-class="active"
        >
          {{ item.label }}
        </router-link>
      </nav>
    </aside>

    <div class="main">
      <header class="topbar">
        <span class="role-tag">{{ roleLabel }}</span>
        <span class="user">{{ auth.displayName }}</span>
        <button class="ghost" @click="onLogout">退出登录</button>
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const MENUS = {
  admin: [
    { name: 'dashboard', label: '首页' },
    { name: 'admin-users', label: '用户管理' },
    { name: 'profile', label: '个人信息' }
  ],
  teacher: [
    { name: 'dashboard', label: '首页' },
    { name: 'teacher-questions', label: '试题管理' },
    { name: 'teacher-papers', label: '组卷管理' },
    { name: 'teacher-exams', label: '考试安排' },
    { name: 'teacher-statistics', label: '成绩统计' },
    { name: 'scores', label: '成绩查询' },
    { name: 'profile', label: '个人信息' }
  ],
  student: [
    { name: 'dashboard', label: '首页' },
    { name: 'student-exams', label: '在线考试' },
    { name: 'scores', label: '成绩查询' },
    { name: 'profile', label: '个人信息' }
  ]
}

const ROLE_LABELS = { admin: '管理员', teacher: '教师', student: '学生' }

const menus = computed(() => MENUS[auth.role] || [])
const roleLabel = computed(() => ROLE_LABELS[auth.role] || '未知角色')

function onLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 200px;
  background: #001529;
  color: #fff;
  padding: 18px 0;
  flex-shrink: 0;
}

.brand {
  padding: 0 20px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.brand-title {
  font-size: 16px;
  font-weight: 600;
}

.brand-sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
}

nav {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
}

.nav-item {
  padding: 11px 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.nav-item.active {
  background: var(--primary);
  color: #fff;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 20px;
}

.role-tag {
  background: #eef2ff;
  color: var(--primary);
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 12px;
}

.user {
  margin-left: auto;
  font-size: 14px;
}

.content {
  flex: 1;
  overflow: auto;
}
</style>
