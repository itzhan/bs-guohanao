<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpace, NEmpty } from 'naive-ui'
import { getHotSongs, getNewSongs, getTopRated, getGenres } from '../../api'

const router = useRouter()
const hotSongs = ref([])
const newSongs = ref([])
const topRated = ref([])
const genres = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [h, n, t, g] = await Promise.all([getHotSongs(8), getNewSongs(8), getTopRated(8), getGenres()])
    hotSongs.value = h.data || []
    newSongs.value = n.data || []
    topRated.value = t.data || []
    genres.value = (g.data || []).slice(0, 12)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

function goSong(id) { router.push(`/song/${id}`) }
</script>

<template>
  <div>
    <!-- Hero Banner -->
    <div class="hero">
      <!-- 装饰光晕 -->
      <div class="hero-orb hero-orb-1"></div>
      <div class="hero-orb hero-orb-2"></div>
      <div class="hero-orb hero-orb-3"></div>

      <!-- 音频波形装饰 -->
      <div class="wave-bars">
        <span v-for="i in 40" :key="i" :style="{ animationDelay: (i * 0.08) + 's', height: (10 + Math.random() * 40) + 'px' }"></span>
      </div>

      <div class="hero-inner">
        <div class="hero-badge">🎧 基于 Spark + ALS 协同过滤</div>
        <h1>发现你的下一首<br><span class="gradient-text">心动之歌</span></h1>
        <p class="hero-desc">大数据驱动的个性化音乐推荐引擎，精准匹配你的音乐品味</p>
        <div class="hero-actions">
          <button class="hero-btn-primary" @click="router.push('/recommend')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            开始探索
          </button>
          <button class="hero-btn-ghost" @click="router.push('/songs')">浏览音乐库</button>
        </div>

        <!-- 统计亮点 -->
        <div class="hero-stats">
          <div class="stat-item"><span class="stat-num">10K+</span><span class="stat-label">歌曲曲库</span></div>
          <div class="stat-divider"></div>
          <div class="stat-item"><span class="stat-num">ALS</span><span class="stat-label">推荐算法</span></div>
          <div class="stat-divider"></div>
          <div class="stat-item"><span class="stat-num">实时</span><span class="stat-label">数据分析</span></div>
        </div>
      </div>
    </div>

    <div class="page">
      <!-- 流派标签 -->
      <div class="genre-section">
        <div class="genre-tags">
          <button v-for="g in genres" :key="g.id" class="genre-tag" @click="router.push({ path: '/songs', query: { genreId: g.id } })">{{ g.name }}</button>
        </div>
      </div>

      <!-- 热门歌曲 -->
      <h2 class="section-title" style="margin-top: 36px;">热门歌曲</h2>
      <div class="grid-4">
        <div v-for="(s, idx) in hotSongs" :key="s.id" class="song-card" @click="goSong(s.id)" :style="{ animationDelay: (idx * 0.05) + 's' }">
          <div class="cover-wrap">
            <img :src="s.coverImage || 'https://picsum.photos/seed/song' + s.id + '/300'" :alt="s.title" loading="lazy" />
            <div class="play-icon"></div>
          </div>
          <div class="info">
            <div class="title">{{ s.title }}</div>
            <div class="artist">{{ s.artistName || '未知歌手' }}</div>
            <div class="meta">
              <span class="play-count">▶ {{ (s.playCount || 0).toLocaleString() }}</span>
              <span class="rating">★ {{ s.avgRating || '-' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 最新上架 -->
      <h2 class="section-title" style="margin-top: 48px;">最新上架</h2>
      <div class="grid-4">
        <div v-for="(s, idx) in newSongs" :key="s.id" class="song-card" @click="goSong(s.id)" :style="{ animationDelay: (idx * 0.05) + 's' }">
          <div class="cover-wrap">
            <img :src="s.coverImage || 'https://picsum.photos/seed/new' + s.id + '/300'" :alt="s.title" loading="lazy" />
            <div class="play-icon"></div>
          </div>
          <div class="info">
            <div class="title">{{ s.title }}</div>
            <div class="artist">{{ s.artistName || '未知歌手' }}</div>
          </div>
        </div>
      </div>

      <!-- 高评分 -->
      <h2 class="section-title" style="margin-top: 48px;">高评分推荐</h2>
      <div class="grid-4">
        <div v-for="(s, idx) in topRated" :key="s.id" class="song-card" @click="goSong(s.id)" :style="{ animationDelay: (idx * 0.05) + 's' }">
          <div class="cover-wrap">
            <img :src="s.coverImage || 'https://picsum.photos/seed/top' + s.id + '/300'" :alt="s.title" loading="lazy" />
            <div class="play-icon"></div>
          </div>
          <div class="info">
            <div class="title">{{ s.title }}</div>
            <div class="artist">{{ s.artistName || '未知歌手' }}</div>
            <div class="meta">
              <span class="rating">★ {{ s.avgRating || '-' }} ({{ s.ratingCount || 0 }}人)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ---- Hero ---- */
.hero {
  background: linear-gradient(180deg, #0D1117 0%, #111827 50%, #0D1117 100%);
  color: #fff;
  padding: 100px 24px 80px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
}
.hero-orb-1 {
  width: 500px; height: 500px;
  background: rgba(108, 92, 231, 0.12);
  top: -150px; left: 10%;
  animation: pulse-glow 8s ease-in-out infinite;
}
.hero-orb-2 {
  width: 400px; height: 400px;
  background: rgba(0, 206, 201, 0.08);
  bottom: -100px; right: 10%;
  animation: pulse-glow 10s ease-in-out infinite 3s;
}
.hero-orb-3 {
  width: 300px; height: 300px;
  background: rgba(253, 121, 168, 0.06);
  top: 50%; left: 60%;
  animation: pulse-glow 12s ease-in-out infinite 6s;
}

/* 波形装饰 */
.wave-bars {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: flex-end;
  gap: 3px;
  opacity: 0.08;
}
.wave-bars span {
  display: block;
  width: 3px;
  background: linear-gradient(to top, var(--primary), var(--accent));
  border-radius: 2px;
  animation: waveBar 1.5s ease-in-out infinite alternate;
}
@keyframes waveBar {
  0% { transform: scaleY(0.3); }
  100% { transform: scaleY(1); }
}

.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 640px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(108, 92, 231, 0.15);
  border: 1px solid rgba(108, 92, 231, 0.3);
  color: var(--primary-hover);
  font-size: 13px;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 20px;
  margin-bottom: 24px;
}

.hero h1 {
  font-size: 44px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 16px;
  letter-spacing: -1px;
}
.gradient-text {
  background: linear-gradient(135deg, #6C5CE7, #00CEC9, #FD79A8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 48px;
}
.hero-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--primary);
  color: #fff;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
}
.hero-btn-primary:hover {
  background: var(--primary-hover);
  box-shadow: 0 8px 32px var(--primary-glow);
  transform: translateY(-2px);
}
.hero-btn-ghost {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}
.hero-btn-ghost:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
}
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-num {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}
.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
}
.stat-divider {
  width: 1px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
}

/* ---- 流派标签 ---- */
.genre-section {
  padding: 16px 0;
}
.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.genre-tag {
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  padding: 6px 18px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition);
}
.genre-tag:hover {
  background: rgba(108, 92, 231, 0.15);
  border-color: rgba(108, 92, 231, 0.3);
  color: var(--primary);
  box-shadow: 0 0 16px rgba(108, 92, 231, 0.1);
}
</style>
