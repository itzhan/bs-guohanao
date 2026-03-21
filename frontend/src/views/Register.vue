<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register as registerApi } from '../api'
import { NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'

const router = useRouter()
const message = useMessage()
const loading = ref(false)
const form = ref({ username: '', password: '', nickname: '', email: '' })

async function handleRegister() {
  if (!form.value.username || !form.value.password) { message.warning('用户名和密码不能为空'); return }
  if (form.value.password.length < 6) { message.warning('密码至少6位'); return }
  loading.value = true
  try {
    await registerApi(form.value)
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (e) { message.error(e.message || '注册失败') }
  finally { loading.value = false }
}
</script>

<template>
  <div class="auth-page">
    <!-- 浮动音符装饰 -->
    <div class="floating-notes">
      <span v-for="i in 12" :key="i" class="note" :style="{ left: (i * 8.3) + '%', animationDelay: (i * 0.8) + 's', animationDuration: (12 + i * 1.5) + 's' }">♪</span>
    </div>

    <!-- 背景光晕 -->
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>

    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="url(#regGrad)" stroke-width="1.5"/>
            <circle cx="12" cy="12" r="3" fill="url(#regGrad)"/>
            <path d="M12 2C12 2 12 8 12 12" stroke="url(#regGrad)" stroke-width="1.5" stroke-linecap="round"/>
            <defs>
              <linearGradient id="regGrad" x1="0" y1="0" x2="24" y2="24">
                <stop stop-color="#6C5CE7"/>
                <stop offset="1" stop-color="#00CEC9"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h2>创建账号</h2>
        <p>加入音乐推荐系统，发现你的专属歌单</p>
      </div>

      <n-form :model="form" @submit.prevent="handleRegister">
        <n-form-item><n-input v-model:value="form.username" placeholder="用户名 (3-50字符)" size="large" /></n-form-item>
        <n-form-item><n-input v-model:value="form.nickname" placeholder="昵称 (可选)" size="large" /></n-form-item>
        <n-form-item><n-input v-model:value="form.email" placeholder="邮箱 (可选)" size="large" /></n-form-item>
        <n-form-item><n-input v-model:value="form.password" type="password" placeholder="密码 (至少6位)" size="large" show-password-on="click" /></n-form-item>
        <n-button type="primary" block size="large" :loading="loading" @click="handleRegister" class="register-btn">
          注 册
        </n-button>
      </n-form>

      <div class="auth-footer">
        <span>已有账号？</span>
        <router-link to="/login">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}
.bg-orb-1 {
  width: 400px; height: 400px;
  background: rgba(108, 92, 231, 0.15);
  top: -100px; right: -100px;
  animation: pulse-glow 8s ease-in-out infinite;
}
.bg-orb-2 {
  width: 350px; height: 350px;
  background: rgba(0, 206, 201, 0.1);
  bottom: -80px; left: -80px;
  animation: pulse-glow 10s ease-in-out infinite 2s;
}
.bg-orb-3 {
  width: 250px; height: 250px;
  background: rgba(253, 121, 168, 0.08);
  top: 30%; left: 15%;
  animation: pulse-glow 12s ease-in-out infinite 4s;
}

.floating-notes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.note {
  position: absolute;
  bottom: -40px;
  font-size: 20px;
  color: rgba(108, 92, 231, 0.15);
  animation: float-note 20s linear infinite;
}
.note:nth-child(even) { color: rgba(0, 206, 201, 0.12); font-size: 16px; }
.note:nth-child(3n) { color: rgba(253, 121, 168, 0.1); font-size: 24px; }

.auth-card {
  width: 420px;
  padding: 36px;
  border-radius: 20px;
  background: rgba(22, 27, 34, 0.8);
  backdrop-filter: blur(24px) saturate(1.8);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.4);
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}
.auth-logo {
  display: inline-flex;
  margin-bottom: 16px;
  animation: pulse-glow 3s ease-in-out infinite;
}
.auth-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}
.auth-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.register-btn {
  margin-top: 8px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
}
.auth-footer span {
  color: var(--text-tertiary);
}
.auth-footer a {
  color: var(--primary);
  font-weight: 500;
  margin-left: 4px;
  transition: color var(--transition);
}
.auth-footer a:hover {
  color: var(--primary-hover);
}
</style>
