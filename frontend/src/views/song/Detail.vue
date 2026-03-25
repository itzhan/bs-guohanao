<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NSpace, NButton, NRate, NInput, NAvatar, NTag, NEmpty, useMessage } from 'naive-ui'
import { getSongDetail, getMyRating, rateSong, toggleFavorite, checkFavorite, addComment, getComments, recordPlay, getSimilarSongs } from '../../api'
import { useUserStore } from '../../stores/user'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const song = ref(null)
const myRating = ref(0)
const isFav = ref(false)
const comments = ref([])
const commentsTotal = ref(0)
const newComment = ref('')
const similar = ref([])

// 情感分析饼图配置
const sentimentChartOption = computed(() => {
  const pos = comments.value.filter(c => c.sentimentLabel === '正向').length
  const neu = comments.value.filter(c => c.sentimentLabel === '中性').length
  const neg = comments.value.filter(c => c.sentimentLabel === '负向').length
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: '#8B949E', fontSize: 12 } },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#0D1117', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{d}%', color: '#C9D1D9', fontSize: 12 },
      data: [
        { value: pos, name: '正向', itemStyle: { color: '#3FB950' } },
        { value: neu, name: '中性', itemStyle: { color: '#D29922' } },
        { value: neg, name: '负向', itemStyle: { color: '#F85149' } },
      ].filter(d => d.value > 0)
    }]
  }
})

async function loadSong(id) {
  song.value = null
  myRating.value = 0
  isFav.value = false
  similar.value = []
  try {
    const res = await getSongDetail(id)
    song.value = res.data
    const sim = await getSimilarSongs(id, 6)
    similar.value = sim.data || []

    if (userStore.isLoggedIn) {
      recordPlay({ songId: Number(id), duration: 0 }).catch(() => {})
      const r = await getMyRating(id).catch(() => null)
      if (r?.data) myRating.value = r.data.score
      const f = await checkFavorite(id).catch(() => null)
      if (f?.data) isFav.value = f.data.isFavorited
    }
    loadComments()
  } catch (e) { message.error('歌曲不存在') }
}

onMounted(() => loadSong(route.params.id))
watch(() => route.params.id, (newId) => { if (newId) loadSong(newId) })


async function loadComments() {
  const res = await getComments(route.params.id, { page: 1, pageSize: 20 })
  comments.value = res.data?.records || []
  commentsTotal.value = res.data?.total || 0
}

async function handleRate(score) {
  if (!userStore.isLoggedIn) { message.warning('请先登录'); return }
  try { await rateSong({ songId: Number(route.params.id), score }); myRating.value = score; message.success('评分成功') }
  catch (e) { message.error(e.message) }
}

async function handleFav() {
  if (!userStore.isLoggedIn) { message.warning('请先登录'); return }
  try { const res = await toggleFavorite(Number(route.params.id)); isFav.value = res.data.isFavorited; message.success(res.message) }
  catch (e) { message.error(e.message) }
}

async function submitComment() {
  if (!userStore.isLoggedIn) { message.warning('请先登录'); return }
  if (!newComment.value.trim()) return
  try { await addComment({ songId: Number(route.params.id), content: newComment.value.trim() }); newComment.value = ''; loadComments(); message.success('评论成功') }
  catch (e) { message.error(e.message) }
}
</script>

<template>
  <div class="page" v-if="song">
    <!-- 歌曲信息 -->
    <div class="detail-header">
      <div class="cover-container">
        <div class="cover-glow" :style="{ backgroundImage: `url(${song.coverImage || 'https://picsum.photos/seed/d' + song.id + '/400'})` }"></div>
        <img :src="song.coverImage || 'https://picsum.photos/seed/d' + song.id + '/400'" class="cover" />
      </div>
      <div class="detail-info">
        <h1>{{ song.title }}</h1>
        <p class="artist-name">{{ song.artistName || '未知歌手' }}</p>
        <div class="tags">
          <n-tag v-for="g in (song.genres || [])" :key="g.id || g" size="small" round :bordered="false" :color="{ color: 'rgba(108,92,231,0.15)', textColor: '#A29BFE' }">{{ g.name || g }}</n-tag>
          <n-tag v-if="song.language" size="small" round :bordered="false" :color="{ color: 'rgba(0,206,201,0.15)', textColor: '#00CEC9' }">{{ song.language }}</n-tag>
        </div>
        <div class="stats-row">
          <div class="stat-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            {{ (song.playCount || 0).toLocaleString() }}
          </div>
          <div class="stat-chip fav">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            {{ (song.favoriteCount || 0).toLocaleString() }}
          </div>
          <div class="stat-chip rate">
            ★ {{ song.avgRating || '-' }}
            <span class="rate-count">({{ song.ratingCount || 0 }}人)</span>
          </div>
        </div>
        <div class="interaction-row">
          <div class="rate-section">
            <span class="rate-label">我的评分</span>
            <n-rate :value="myRating" @update:value="handleRate" allow-half />
          </div>
          <button :class="['fav-btn', { active: isFav }]" @click="handleFav">
            <svg width="18" height="18" viewBox="0 0 24 24" :fill="isFav ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            {{ isFav ? '已收藏' : '收藏' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 歌词 -->
    <div v-if="song.lyrics" class="lyrics-card">
      <h3 class="card-title">歌词</h3>
      <pre class="lyrics-content">{{ song.lyrics }}</pre>
    </div>

    <!-- 评论 -->
    <div class="comments-section">
      <h3 class="card-title">评论 <span class="comment-count">{{ commentsTotal }}</span></h3>

      <!-- 情感分布 ECharts 饼图 -->
      <div class="sentiment-chart-wrap" v-if="comments.length">
        <v-chart :option="sentimentChartOption" style="height: 220px;" autoresize />
      </div>

      <div class="comment-input-row">
        <n-input v-model:value="newComment" placeholder="写下你的感受..." @keyup.enter="submitComment" />
        <n-button type="primary" @click="submitComment">发表</n-button>
      </div>
      <div class="comments-list">
        <div v-for="c in comments" :key="c.id" class="comment-item">
          <div class="comment-avatar">{{ (c.username || '?')[0] }}</div>
          <div class="comment-body">
            <div class="comment-meta">
              <span class="comment-user">{{ c.username || '匿名' }}</span>
              <span v-if="c.sentimentLabel" :class="['sentiment-tag', c.sentimentLabel === '正向' ? 'pos' : c.sentimentLabel === '负向' ? 'neg' : 'neu']">
                {{ c.sentimentLabel === '正向' ? '🟢' : c.sentimentLabel === '负向' ? '🔴' : '🟡' }} {{ c.sentimentLabel }}
              </span>
              <span class="comment-time">{{ c.createdAt?.replace('T', ' ').substring(0, 16) }}</span>
            </div>
            <div class="comment-text">{{ c.content }}</div>
          </div>
        </div>
        <n-empty v-if="!comments.length" description="还没有评论，快来抢沙发~" style="margin: 32px 0;" />
      </div>
    </div>

    <!-- 相似推荐 -->
    <div v-if="similar.length" class="similar-section">
      <h2 class="section-title">相似推荐</h2>
      <div class="grid-4">
        <div v-for="s in similar" :key="s.id" class="song-card" @click="router.push(`/song/${s.id}`)">
          <div class="cover-wrap">
            <img :src="s.coverImage || 'https://picsum.photos/seed/sim' + s.id + '/300'" :alt="s.title" loading="lazy" />
            <div class="play-icon"></div>
          </div>
          <div class="info"><div class="title">{{ s.title }}</div><div class="artist">{{ s.artistName || '' }}</div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ---- 详情头部 ---- */
.detail-header {
  display: flex;
  gap: 36px;
  align-items: flex-start;
  flex-wrap: wrap;
  animation: fadeInUp 0.5s ease both;
}

.cover-container {
  position: relative;
  flex-shrink: 0;
}
.cover-glow {
  position: absolute;
  inset: 20px;
  background-size: cover;
  background-position: center;
  filter: blur(40px) saturate(1.5);
  opacity: 0.4;
  border-radius: 20px;
}
.cover {
  width: 260px;
  height: 260px;
  border-radius: 16px;
  object-fit: cover;
  position: relative;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
}

.detail-info {
  flex: 1;
  min-width: 300px;
}
.detail-info h1 {
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}
.artist-name {
  font-size: 16px;
  color: var(--primary);
  margin: 6px 0 16px;
  font-weight: 500;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}
.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--accent);
  background: rgba(0, 206, 201, 0.1);
  padding: 4px 12px;
  border-radius: 16px;
}
.stat-chip.fav {
  color: var(--warm);
  background: rgba(253, 121, 168, 0.1);
}
.stat-chip.rate {
  color: #FDCB6E;
  background: rgba(253, 203, 110, 0.1);
}
.rate-count { font-size: 11px; color: var(--text-tertiary); }

.interaction-row {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}
.rate-section {
  display: flex;
  align-items: center;
  gap: 10px;
}
.rate-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.fav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition);
}
.fav-btn:hover {
  border-color: var(--warm);
  color: var(--warm);
}
.fav-btn.active {
  background: rgba(253, 121, 168, 0.15);
  border-color: var(--warm);
  color: var(--warm);
}

/* ---- 歌词 ---- */
.lyrics-card {
  margin-top: 32px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  animation: fadeInUp 0.5s ease 0.1s both;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.lyrics-content {
  white-space: pre-wrap;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 2;
  text-align: center;
  max-height: 400px;
  overflow-y: auto;
}

/* ---- 评论 ---- */
.comments-section {
  margin-top: 32px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  animation: fadeInUp 0.5s ease 0.2s both;
}
.comment-count {
  font-size: 14px;
  color: var(--text-tertiary);
  font-weight: 400;
}
.comment-input-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.comments-list {
  display: flex;
  flex-direction: column;
}
.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}
.comment-item:last-child { border-bottom: none; }
.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}
.comment-body { flex: 1; }
.comment-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}
.comment-user {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}
.comment-time {
  font-size: 12px;
  color: var(--text-tertiary);
}
.comment-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ---- 情感分析 ---- */
.sentiment-chart-wrap {
  margin-bottom: 16px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}
.sentiment-tag {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}
.sentiment-tag.pos {
  background: rgba(63, 185, 80, 0.12);
  color: #3FB950;
}
.sentiment-tag.neu {
  background: rgba(210, 153, 34, 0.12);
  color: #D29922;
}
.sentiment-tag.neg {
  background: rgba(248, 81, 73, 0.12);
  color: #F85149;
}

/* ---- 相似推荐 ---- */
.similar-section {
  margin-top: 40px;
  animation: fadeInUp 0.5s ease 0.3s both;
}
</style>
