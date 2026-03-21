<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { NInput, NAvatar, NDropdown, NIcon } from 'naive-ui'
import { SearchOutline } from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const searchKeyword = ref('')

const navItems = [
  { label: '首页', path: '/' },
  { label: '音乐库', path: '/songs' },
  { label: '个性化推荐', path: '/recommend' },
  { label: '数据分析', path: '/stats' },
]

const dropdownOptions = [
  { label: '个人中心', key: 'user' },
  { type: 'divider' },
  { label: '退出登录', key: 'logout' },
]

function handleDropdown(key) {
  if (key === 'user') router.push('/user')
  if (key === 'logout') { userStore.logout(); router.push('/') }
}

function handleSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/songs', query: { keyword: searchKeyword.value.trim() } })
  }
}
</script>

<template>
  <div class="layout">
    <!-- 顶部导航 -->
    <header class="navbar">
      <div class="navbar-inner">
        <div class="logo" @click="router.push('/')">
          <div class="logo-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="url(#logoGrad)" stroke-width="2"/>
              <circle cx="12" cy="12" r="3" fill="url(#logoGrad)"/>
              <path d="M12 2C12 2 12 8 12 12" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round"/>
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="24" y2="24">
                  <stop stop-color="#6C5CE7"/>
                  <stop offset="1" stop-color="#00CEC9"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span class="logo-text">MusicRec</span>
        </div>

        <nav class="nav-links">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            :class="{ active: item.path === '/' ? route.path === '/' : route.path.startsWith(item.path) }"
          >
            {{ item.label }}
            <span class="nav-glow"></span>
          </router-link>
        </nav>

        <div class="nav-right">
          <div class="search-box">
            <n-input
              v-model:value="searchKeyword"
              placeholder="搜索歌曲、歌手..."
              size="small"
              round
              clearable
              @keyup.enter="handleSearch"
            >
              <template #suffix>
                <n-icon :component="SearchOutline" style="cursor:pointer;color:var(--text-secondary);" @click="handleSearch" />
              </template>
            </n-input>
          </div>

          <template v-if="userStore.isLoggedIn">
            <n-dropdown :options="dropdownOptions" @select="handleDropdown" trigger="click">
              <div class="avatar-ring">
                <n-avatar round size="small">{{ userStore.userInfo?.nickname?.[0] || 'U' }}</n-avatar>
              </div>
            </n-dropdown>
          </template>
          <template v-else>
            <button class="btn-ghost" @click="router.push('/login')">登录</button>
            <button class="btn-primary" @click="router.push('/register')">注册</button>
          </template>
        </div>
      </div>
    </header>

    <!-- 内容区 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 底部 -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="footer-logo">MusicRec</div>
          <p>基于大数据的音乐推荐与数据分析系统</p>
        </div>
        <div class="footer-links">
          <div class="footer-col">
            <h4>浏览</h4>
            <router-link to="/">首页</router-link>
            <router-link to="/songs">音乐库</router-link>
            <router-link to="/stats">数据分析</router-link>
          </div>
          <div class="footer-col">
            <h4>功能</h4>
            <router-link to="/recommend">个性化推荐</router-link>
            <router-link to="/user">个人中心</router-link>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2026 郭含奥 毕业设计 · 基于大数据的音乐推荐与数据分析系统</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ---- 导航栏 ---- */
.navbar {
  background: rgba(13, 17, 23, 0.85);
  backdrop-filter: blur(20px) saturate(1.5);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: opacity var(--transition);
}
.logo:hover { opacity: 0.8; }
.logo-icon { display: flex; }
.logo-text {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #6C5CE7, #00CEC9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

/* 导航链接 */
.nav-links {
  display: flex;
  gap: 4px;
}
.nav-links a {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all var(--transition);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  position: relative;
  overflow: hidden;
}
.nav-links a:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.04);
}
.nav-links a.active {
  color: var(--primary);
}
.nav-links a .nav-glow {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: var(--primary);
  border-radius: 1px;
  transition: all var(--transition);
  box-shadow: 0 0 8px var(--primary-glow);
}
.nav-links a.active .nav-glow,
.nav-links a:hover .nav-glow {
  width: 60%;
}

/* 右侧 */
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.search-box {
  width: 200px;
}

/* 头像光环 */
.avatar-ring {
  padding: 2px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  cursor: pointer;
  transition: box-shadow var(--transition);
}
.avatar-ring:hover {
  box-shadow: 0 0 16px var(--primary-glow);
}

/* 按钮 */
.btn-ghost {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}
.btn-ghost:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.04);
}
.btn-primary {
  background: var(--primary);
  border: none;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 6px 18px;
  border-radius: 20px;
  transition: all var(--transition);
}
.btn-primary:hover {
  background: var(--primary-hover);
  box-shadow: 0 4px 16px var(--primary-glow);
}

/* ---- 内容区 ---- */
.main-content {
  flex: 1;
  min-height: calc(100vh - 64px);
}

/* ---- 页脚 ---- */
.footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  margin-top: auto;
}
.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px 32px;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 32px;
}
.footer-brand {
  max-width: 300px;
}
.footer-logo {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #6C5CE7, #00CEC9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}
.footer-brand p {
  font-size: 13px;
  color: var(--text-tertiary);
  line-height: 1.6;
}
.footer-links {
  display: flex;
  gap: 56px;
}
.footer-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.footer-col h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
.footer-col a {
  font-size: 13px;
  color: var(--text-tertiary);
  transition: color var(--transition);
}
.footer-col a:hover {
  color: var(--text-primary);
}
.footer-bottom {
  border-top: 1px solid var(--border);
  padding: 20px 24px;
  text-align: center;
}
.footer-bottom p {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
