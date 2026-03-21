<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { login } from '../api'
import { useMessage, NCard, NForm, NFormItem, NInput, NButton, NSpace } from 'naive-ui'

const router = useRouter()
const userStore = useUserStore()
const message = useMessage()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) { message.warning('请输入账号和密码'); return }
  loading.value = true
  try {
    const res = await login(form.value)
    const { token, user } = res.data
    if (!['admin', 'operator'].includes(user.role)) { message.error('仅管理员/运营可登录管理端'); return }
    userStore.setLogin(token, user)
    message.success('登录成功')
    router.push('/dashboard')
  } catch (e) { message.error(e.message || '登录失败') }
  finally { loading.value = false }
}
</script>

<template>
  <div class="login-page">
    <div class="login-bg"></div>
    <n-card class="login-card" :bordered="false">
      <div style="text-align: center; margin-bottom: 32px;">
        <div style="font-size: 28px; margin-bottom: 8px;">🎵</div>
        <h2 style="font-size: 22px; color: #333; margin: 0;">音乐推荐与数据分析系统</h2>
        <p style="color: #999; margin-top: 8px;">管理员登录</p>
      </div>
      <n-form :model="form" @submit.prevent="handleLogin">
        <n-form-item label="用户名">
          <n-input v-model:value="form.username" placeholder="请输入用户名" size="large" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" placeholder="请输入密码" size="large" show-password-on="click" @keyup.enter="handleLogin" />
        </n-form-item>
        <n-button type="primary" block size="large" :loading="loading" @click="handleLogin" style="margin-top: 8px;">登 录</n-button>
      </n-form>
      <div style="text-align: center; margin-top: 20px; color: #bbb; font-size: 12px;">
        管理员: admin / admin123 &nbsp;|&nbsp; 运营: operator / oper123
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); position: relative; overflow: hidden; }
.login-bg { position: absolute; inset: 0; background: radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 115, 0.1) 0%, transparent 40%); }
.login-card { width: 400px; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); position: relative; z-index: 1; padding: 20px; }
</style>
