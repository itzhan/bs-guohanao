<script setup>
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { NLayout, NLayoutSider, NLayoutHeader, NLayoutContent, NMenu, NIcon, NDropdown, NAvatar, NSpace, NText, NBadge } from 'naive-ui'
import { MusicalNotesOutline, PeopleOutline, DiscOutline, GridOutline, ChatbubblesOutline, ReaderOutline, HomeOutline, LogOutOutline, PersonOutline, ColorPaletteOutline } from '@vicons/ionicons5'

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
  { label: '评论管理', key: '/comments', icon: () => h(NIcon, null, { default: () => h(ChatbubblesOutline) }) },
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
      :native-scrollbar="false" style="background: #001529">
      <div style="padding: 20px; text-align: center; color: #fff; font-weight: 700; font-size: 16px; white-space: nowrap; overflow: hidden;">
        {{ collapsed ? '🎵' : '🎵 音乐推荐管理端' }}
      </div>
      <n-menu :collapsed="collapsed" :collapsed-width="64" :collapsed-icon-size="22" :options="menuOptions"
        :value="activeKey" @update:value="handleMenuUpdate" :indent="24"
        inverted style="--n-item-text-color: rgba(255,255,255,0.65); --n-item-text-color-active: #fff;" />
    </n-layout-sider>
    <n-layout>
      <n-layout-header bordered style="height: 56px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; background: #fff;">
        <n-text strong style="font-size: 16px; color: #333;">{{ route.meta.title || '管理端' }}</n-text>
        <n-dropdown :options="dropdownOptions" @select="handleDropdown" trigger="click">
          <n-space align="center" style="cursor: pointer;">
            <n-avatar round size="small" style="background: #7265e6">{{ userStore.userInfo?.nickname?.[0] || 'A' }}</n-avatar>
            <n-text>{{ userStore.userInfo?.nickname || '管理员' }}</n-text>
          </n-space>
        </n-dropdown>
      </n-layout-header>
      <n-layout-content style="padding: 20px; background: #f0f2f5;">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>
