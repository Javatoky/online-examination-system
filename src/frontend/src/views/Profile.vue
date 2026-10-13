<template>
  <div class="page">
    <h2 class="page-title">个人信息</h2>

    <div class="panel">
      <p class="muted">角色：{{ auth.user?.role }} ｜ 当前用户名：{{ auth.user?.username }}</p>
      <p class="muted">
        除用户名和登录密码外，其他个人信息（学号/工号、姓名、班级等）仅可查询，需由管理员维护。
      </p>
    </div>

    <form class="panel form" @submit.prevent="onSubmit">
      <h3>修改用户名与密码</h3>
      <label>
        新用户名（留空则不修改）
        <input v-model.trim="form.username" placeholder="请输入新用户名" />
      </label>
      <label>
        原密码
        <input v-model="form.oldPassword" type="password" placeholder="修改密码时必填" />
      </label>
      <label>
        新密码
        <input v-model="form.newPassword" type="password" placeholder="不修改密码可留空" />
      </label>

      <p v-if="message" :class="isError ? 'error' : 'success'">{{ message }}</p>

      <button type="submit" :disabled="loading">{{ loading ? '提交中…' : '保存修改' }}</button>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const form = reactive({ username: '', oldPassword: '', newPassword: '' })
const loading = ref(false)
const message = ref('')
const isError = ref(false)

async function onSubmit() {
  message.value = ''
  isError.value = false
  if (!form.username && !form.newPassword) {
    isError.value = true
    message.value = '请填写要修改的内容'
    return
  }
  loading.value = true
  try {
    await api.put('/me', {
      username: form.username || undefined,
      old_password: form.oldPassword || undefined,
      new_password: form.newPassword || undefined
    })
    if (form.username) {
      auth.user.username = form.username
      localStorage.setItem('user', JSON.stringify(auth.user))
    }
    message.value = '保存成功'
    form.oldPassword = ''
    form.newPassword = ''
  } catch (e) {
    isError.value = true
    message.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 420px;
}

h3 {
  margin: 0;
  font-size: 15px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--text-light);
}

.success {
  color: #67c23a;
  font-size: 13px;
}
</style>
