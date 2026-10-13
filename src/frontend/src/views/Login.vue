<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="onSubmit">
      <h1>在线考试系统</h1>
      <p class="subtitle">《数据库原理实践》课程设计</p>

      <label>
        用户名
        <input v-model.trim="username" placeholder="请输入用户名" autocomplete="username" />
      </label>
      <label>
        密码
        <input
          v-model="password"
          type="password"
          placeholder="请输入密码"
          autocomplete="current-password"
        />
      </label>

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit" :disabled="loading">{{ loading ? '登录中…' : '登 录' }}</button>

      <p class="hint">演示账号：admin / teacher1 / stu0001（密码均为 123456）</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1d39c4, #2f54eb 60%, #597ef7);
}

.login-card {
  width: 360px;
  background: #fff;
  border-radius: 12px;
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
}

h1 {
  margin: 0;
  font-size: 22px;
  text-align: center;
}

.subtitle {
  margin: 0 0 8px;
  text-align: center;
  color: var(--text-light);
  font-size: 13px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--text-light);
}

button {
  margin-top: 6px;
  padding: 10px;
  font-size: 15px;
}

.hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-light);
  text-align: center;
}
</style>
