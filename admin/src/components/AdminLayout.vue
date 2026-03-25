<script setup>
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { NLayout, NLayoutSider, NLayoutHeader, NLayoutContent, NMenu, NIcon, NDropdown, NAvatar, NSpace, NText } from 'naive-ui'
import { MusicalNotesOutline, PeopleOutline, GridOutline, ChatbubblesOutline, ReaderOutline, HomeOutline, LogOutOutline, PersonOutline, ColorPaletteOutline, AnalyticsOutline, SettingsOutline, WarningOutline, FingerPrintOutline, FlaskOutline } from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const collapsed = ref(false)

const menuOptions = [
  { label: '仪表盘', key: '/dashboard', icon: () => h(NIcon, null, { default: () => h(HomeOutline) }) },
  { label: '歌曲管理', key: '/songs', icon: () => h(NIcon, null, { default: () => h(MusicalNotesOutline) }) },
  { label: '歌手管理', key: '/artists', icon: () => h(NIcon, null, { default: () => h(PersonOutline) }) },
  { label: '流派管理', key: '/genres', icon: () => h(NIcon, null, { default: () => h(ColorPaletteOutline) }) },
  { label: '用户管理', key: '/users', icon: () => h(NIcon, null, { default: () => h(PeopleOutline) }) },
  { label: '用户画像', key: '/portrait', icon: () => h(NIcon, null, { default: () => h(FingerPrintOutline) }) },
  { label: '评论管理', key: '/comments', icon: () => h(NIcon, null, { default: () => h(ChatbubblesOutline) }) },
  { label: '推荐策略', key: '/strategy', icon: () => h(NIcon, null, { default: () => h(SettingsOutline) }) },
  { label: '算法对比', key: '/experiment', icon: () => h(NIcon, null, { default: () => h(FlaskOutline) }) },
  { label: '操作日志', key: '/logs', icon: () => h(NIcon, null, { default: () => h(ReaderOutline) }) },
]

const activeKey = computed(() => route.path)

const dropdownOptions = [
  { label: '退出登录', key: 'logout', icon: () => h(NIcon, null, { default: () => h(LogOutOutline) }) }
]

function handleMenuUpdate(key) { router.push(key) }
function handleDropdown(key) {
  if (key === 'logout') { userStore.logout(); router.push('/login') }
}
</script>

<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider bordered collapse-mode="width" :collapsed-width="64" :width="220" :collapsed="collapsed"
      show-trigger @collapse="collapsed = true" @expand="collapsed = false"
      :native-scrollbar="false" class="admin-sider">
      <!-- 品牌 Logo 区 -->
      <div class="sider-logo">
        <div class="logo-icon">
          <n-icon size="22" color="#fff"><MusicalNotesOutline /></n-icon>
        </div>
        <transition name="fade">
          <span v-if="!collapsed" class="logo-text">音乐推荐管理端</span>
        </transition>
      </div>
      <n-menu :collapsed="collapsed" :collapsed-width="64" :collapsed-icon-size="22" :options="menuOptions"
        :value="activeKey" @update:value="handleMenuUpdate" :indent="24" inverted />
    </n-layout-sider>
    <n-layout>
      <n-layout-header bordered class="admin-header">
        <div class="header-title">
          <div class="header-title-dot"></div>
          <n-text strong style="font-size: 16px;">{{ route.meta.title || '管理端' }}</n-text>
        </div>
        <n-dropdown :options="dropdownOptions" @select="handleDropdown" trigger="click">
          <n-space align="center" style="cursor: pointer; gap: 10px;">
            <n-avatar round size="small" class="header-avatar">{{ userStore.userInfo?.nickname?.[0] || 'A' }}</n-avatar>
            <n-text style="color: var(--text-secondary);">{{ userStore.userInfo?.nickname || '管理员' }}</n-text>
          </n-space>
        </n-dropdown>
      </n-layout-header>
      <n-layout-content class="admin-content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.admin-sider {
  background: var(--bg-card) !important;
  border-right: 1px solid var(--border) !important;
}

.sider-logo {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px var(--primary-glow);
}

.logo-text {
  font-weight: 700;
  font-size: 15px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
}

.admin-header {
  height: 56px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-card) !important;
  border-bottom: 1px solid var(--border) !important;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 8px var(--primary-glow);
}

.header-avatar {
  background: linear-gradient(135deg, var(--primary), var(--warm)) !important;
  font-weight: 600;
}

.admin-content {
  padding: 24px;
  background: var(--bg-primary) !important;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
