<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NTabs, NTabPane, NButton, NInput, NForm, NFormItem, NEmpty, NPagination, NSelect, NSpace, NCheckboxGroup, NCheckbox, useMessage } from 'naive-ui'
import { getUserInfo, updateUserInfo, changePassword, getFavorites, getHistory, getPreference, savePreference, getGenres, getArtists } from '../../api'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const user = ref({})
const profileForm = ref({ nickname: '', email: '', phone: '' })
const passwordForm = ref({ oldPassword: '', newPassword: '' })
const favorites = ref([])
const favTotal = ref(0)
const favPage = ref(1)
const history = ref([])
const histTotal = ref(0)
const histPage = ref(1)

// 偏好问卷
const preference = ref({
  favoriteGenres: [],
  favoriteArtists: [],
  listeningScenarios: [],
  preferredLanguage: null,
  moodPreference: null,
})
const genreOptions = ref([])
const artistOptions = ref([])
const scenarioOptions = [
  { label: '运动健身', value: '运动健身' },
  { label: '学习工作', value: '学习工作' },
  { label: '睡前放松', value: '睡前放松' },
  { label: '通勤路上', value: '通勤路上' },
  { label: '聚会社交', value: '聚会社交' },
  { label: '独处思考', value: '独处思考' },
  { label: '做饭家务', value: '做饭家务' },
]
const langOptions = [
  { label: '华语', value: '华语' },
  { label: '欧美', value: '欧美' },
  { label: '日语', value: '日语' },
  { label: '韩语', value: '韩语' },
  { label: '粤语', value: '粤语' },
  { label: '不限', value: '不限' },
]
const moodOptions = [
  { label: '开心愉悦', value: '开心愉悦' },
  { label: '安静舒缓', value: '安静舒缓' },
  { label: '激昂热血', value: '激昂热血' },
  { label: '伤感治愈', value: '伤感治愈' },
  { label: '浪漫抒情', value: '浪漫抒情' },
  { label: '随心所欲', value: '随心所欲' },
]

onMounted(async () => {
  try {
    const res = await getUserInfo()
    user.value = res.data
    profileForm.value = { nickname: res.data.nickname || '', email: res.data.email || '', phone: res.data.phone || '' }
  } catch (e) { console.error(e) }
  loadFavorites(); loadHistory(); loadPreference()
})

async function loadPreference() {
  try {
    const [pRes, gRes, aRes] = await Promise.all([getPreference(), getGenres(), getArtists({ limit: 50 })])
    if (pRes.data) {
      preference.value.favoriteGenres = pRes.data.favoriteGenres ? JSON.parse(pRes.data.favoriteGenres) : []
      preference.value.favoriteArtists = pRes.data.favoriteArtists ? JSON.parse(pRes.data.favoriteArtists) : []
      preference.value.listeningScenarios = pRes.data.listeningScenarios ? JSON.parse(pRes.data.listeningScenarios) : []
      preference.value.preferredLanguage = pRes.data.preferredLanguage || null
      preference.value.moodPreference = pRes.data.moodPreference || null
    }
    genreOptions.value = (gRes.data || []).map(g => ({ label: g.name, value: g.name }))
    artistOptions.value = (aRes.data?.records || aRes.data || []).map(a => ({ label: a.name, value: a.name }))
  } catch (e) { console.error(e) }
}

async function savePref() {
  try {
    await savePreference(preference.value)
    message.success('偏好已保存，推荐会更加精准！')
  } catch (e) { message.error(e.message || '保存失败') }
}

async function loadFavorites() { try { const res = await getFavorites({ page: favPage.value, pageSize: 8 }); favorites.value = res.data?.records || []; favTotal.value = res.data?.total || 0 } catch (e) {} }
async function loadHistory() { try { const res = await getHistory({ page: histPage.value, pageSize: 10 }); history.value = res.data?.records || []; histTotal.value = res.data?.total || 0 } catch (e) {} }

async function saveProfile() {
  try { const res = await updateUserInfo(profileForm.value); userStore.updateUser(res.data); message.success('信息已更新') } catch (e) { message.error(e.message) }
}
async function savePassword() {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) { message.warning('请填写密码'); return }
  try { await changePassword(passwordForm.value); passwordForm.value = { oldPassword: '', newPassword: '' }; message.success('密码修改成功') } catch (e) { message.error(e.message) }
}
</script>

<template>
  <div class="page">
    <!-- 用户卡片 -->
    <div class="user-hero">
      <div class="user-hero-bg"></div>
      <div class="user-hero-content">
        <div class="user-avatar-large">{{ user.nickname?.[0] || user.username?.[0] || 'U' }}</div>
        <div class="user-meta">
          <h2>{{ user.nickname || user.username || '用户' }}</h2>
          <p>@{{ user.username || '' }}</p>
          <div class="user-badges">
            <span class="badge">{{ user.role === 'admin' ? '管理员' : user.role === 'operator' ? '运营' : '普通用户' }}</span>
          </div>
        </div>
        <div class="user-quick-stats">
          <div class="qs-item"><span class="qs-num">{{ favTotal }}</span><span class="qs-label">收藏</span></div>
          <div class="qs-divider"></div>
          <div class="qs-item"><span class="qs-num">{{ histTotal }}</span><span class="qs-label">播放记录</span></div>
        </div>
      </div>
    </div>

    <!-- Tab 面板 -->
    <div class="user-panel">
      <n-tabs type="line" animated>
        <!-- 基本信息 -->
        <n-tab-pane name="profile" tab="个人信息">
          <div class="form-section">
            <n-form :model="profileForm" label-placement="left" label-width="80">
              <n-form-item label="用户名"><n-input :value="user.username" disabled /></n-form-item>
              <n-form-item label="角色"><n-input :value="user.role === 'admin' ? '管理员' : user.role === 'operator' ? '运营' : '普通用户'" disabled /></n-form-item>
              <n-form-item label="昵称"><n-input v-model:value="profileForm.nickname" /></n-form-item>
              <n-form-item label="邮箱"><n-input v-model:value="profileForm.email" /></n-form-item>
              <n-form-item label="手机"><n-input v-model:value="profileForm.phone" /></n-form-item>
              <n-button type="primary" @click="saveProfile">保存修改</n-button>
            </n-form>
          </div>
        </n-tab-pane>

        <!-- 修改密码 -->
        <n-tab-pane name="password" tab="修改密码">
          <div class="form-section">
            <n-form :model="passwordForm" label-placement="left" label-width="80">
              <n-form-item label="旧密码"><n-input v-model:value="passwordForm.oldPassword" type="password" show-password-on="click" /></n-form-item>
              <n-form-item label="新密码"><n-input v-model:value="passwordForm.newPassword" type="password" show-password-on="click" /></n-form-item>
              <n-button type="primary" @click="savePassword">确认修改</n-button>
            </n-form>
          </div>
        </n-tab-pane>

        <!-- 我的收藏 -->
        <n-tab-pane name="favorites" tab="我的收藏">
          <div v-if="favorites.length" class="grid-4">
            <div v-for="f in favorites" :key="f.id" class="song-card" @click="router.push(`/song/${f.songId || f.id}`)">
              <div class="cover-wrap">
                <img :src="f.coverImage || 'https://picsum.photos/seed/fav' + f.id + '/300'" loading="lazy" />
                <div class="play-icon"></div>
              </div>
              <div class="info"><div class="title">{{ f.songTitle || f.title || '歌曲' }}</div><div class="artist">{{ f.artistName || '' }}</div></div>
            </div>
          </div>
          <n-empty v-else description="还没有收藏歌曲" style="margin: 40px 0;" />
          <div class="pagination-wrap" v-if="favTotal > 8"><n-pagination v-model:page="favPage" :page-count="Math.ceil(favTotal/8)" @update:page="loadFavorites" /></div>
        </n-tab-pane>

        <!-- 音乐偏好 -->
        <n-tab-pane name="preference" tab="音乐偏好">
          <div class="pref-section">
            <h3 class="pref-title">🎵 喜爱流派</h3>
            <n-checkbox-group v-model:value="preference.favoriteGenres">
              <n-space>
                <n-checkbox v-for="g in genreOptions" :key="g.value" :value="g.value" :label="g.label" />
              </n-space>
            </n-checkbox-group>
          </div>
          <div class="pref-section">
            <h3 class="pref-title">🎤 喜爱歌手</h3>
            <n-select v-model:value="preference.favoriteArtists" :options="artistOptions" multiple filterable
              placeholder="搜索并选择喜爱的歌手" max-tag-count="responsive" />
          </div>
          <div class="pref-section">
            <h3 class="pref-title">🎧 听歌场景</h3>
            <n-checkbox-group v-model:value="preference.listeningScenarios">
              <n-space>
                <n-checkbox v-for="s in scenarioOptions" :key="s.value" :value="s.value" :label="s.label" />
              </n-space>
            </n-checkbox-group>
          </div>
          <div class="pref-section">
            <h3 class="pref-title">🌍 偏好语言</h3>
            <n-select v-model:value="preference.preferredLanguage" :options="langOptions" placeholder="选择偏好语言" style="max-width: 300px;" />
          </div>
          <div class="pref-section">
            <h3 class="pref-title">💭 情绪偏好</h3>
            <n-select v-model:value="preference.moodPreference" :options="moodOptions" placeholder="选择情绪偏好" style="max-width: 300px;" />
          </div>
          <n-button type="primary" style="margin-top: 16px;" @click="savePref">保存偏好设置</n-button>
        </n-tab-pane>

        <!-- 播放历史 -->
        <n-tab-pane name="history" tab="播放历史">
          <div v-if="history.length" class="history-list">
            <div v-for="h in history" :key="h.id" class="history-item" @click="router.push(`/song/${h.songId || h.id}`)">
              <div class="history-cover">
                <img :src="h.coverImage || 'https://picsum.photos/seed/hist' + h.id + '/80'" />
              </div>
              <div class="history-info">
                <div class="history-title">{{ h.songTitle || h.title || '歌曲' }}</div>
                <div class="history-artist">{{ h.artistName || '' }} · 播放 {{ h.playCount || 1 }} 次</div>
              </div>
              <div class="history-time">{{ h.updatedAt?.replace('T', ' ').substring(0, 16) || '' }}</div>
            </div>
          </div>
          <n-empty v-else description="还没有播放记录" style="margin: 40px 0;" />
          <div class="pagination-wrap" v-if="histTotal > 10"><n-pagination v-model:page="histPage" :page-count="Math.ceil(histTotal/10)" @update:page="loadHistory" /></div>
        </n-tab-pane>
      </n-tabs>
    </div>
  </div>
</template>

<style scoped>
/* 用户卡片 */
.user-hero {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 24px;
  animation: fadeInUp 0.5s ease both;
}
.user-hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(108,92,231,0.2), rgba(0,206,201,0.15), rgba(253,121,168,0.1));
  filter: blur(0);
}
.user-hero-content {
  position: relative;
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
  background: rgba(22, 27, 34, 0.6);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.user-avatar-large {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 8px 24px var(--primary-glow);
}
.user-meta { flex: 1; min-width: 180px; }
.user-meta h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.user-meta p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 2px;
}
.user-badges {
  margin-top: 8px;
}
.badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  background: rgba(0, 206, 201, 0.12);
  border: 1px solid rgba(0, 206, 201, 0.2);
  padding: 2px 10px;
  border-radius: 12px;
}
.user-quick-stats {
  display: flex;
  align-items: center;
  gap: 24px;
}
.qs-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.qs-num {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}
.qs-label {
  font-size: 12px;
  color: var(--text-tertiary);
}
.qs-divider {
  width: 1px;
  height: 32px;
  background: var(--border);
}

/* Tab 面板 */
.user-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  animation: fadeInUp 0.5s ease 0.1s both;
}

.form-section {
  max-width: 440px;
  padding: 16px 0;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 播放历史 */
.history-list {
  display: flex;
  flex-direction: column;
}
.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background var(--transition);
  border-radius: var(--radius-sm);
  padding-left: 8px;
  padding-right: 8px;
}
.history-item:hover {
  background: rgba(255, 255, 255, 0.02);
}
.history-item:last-child { border-bottom: none; }
.history-cover {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}
.history-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.history-info { flex: 1; min-width: 0; }
.history-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.history-artist {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}
.history-time {
  font-size: 12px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

/* 偏好问卷 */
.pref-section {
  margin-bottom: 24px;
  max-width: 600px;
}
.pref-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}
</style>
