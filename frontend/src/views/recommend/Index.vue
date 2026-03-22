<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NEmpty, NButton, useMessage } from 'naive-ui'
import { getRecommendations } from '../../api'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()
const recs = ref([])
const loading = ref(true)

onMounted(async () => {
  try { const res = await getRecommendations(20); recs.value = res.data || [] }
  catch (e) { message.error(e.message || '加载推荐失败') }
  finally { loading.value = false }
})
</script>

<template>
  <div class="page">
    <!-- 推荐头部 -->
    <div class="rec-header">
      <div class="rec-glow"></div>
      <div class="rec-content">
        <h2 class="section-title" style="margin-bottom:6px;">为你精选</h2>
        <p class="rec-desc">基于 ALS 协同过滤算法，结合你的听歌偏好与评分行为生成的个性化推荐</p>
        <div class="rec-tags">
          <span class="rec-tag">🧠 协同过滤</span>
          <span class="rec-tag">📊 行为分析</span>
          <span class="rec-tag">🎯 精准匹配</span>
        </div>
      </div>
    </div>

    <!-- 推荐列表 -->
    <div v-if="recs.length" class="grid-4" style="margin-top: 28px;">
      <div v-for="(s, idx) in recs" :key="s.id || s.songId" class="song-card" @click="router.push(`/song/${s.id || s.songId}`)" :style="{ animationDelay: (idx * 0.04) + 's' }">
        <div class="cover-wrap">
          <img :src="s.coverImage || 'https://picsum.photos/seed/rec' + (s.id || s.songId) + '/300'" :alt="s.title" loading="lazy" />
          <div class="play-icon"></div>
        </div>
        <div class="info">
          <div class="title">{{ s.title || '推荐歌曲' }}</div>
          <div class="artist">{{ s.artistName || '' }}</div>
          <div v-if="s.reason" class="rec-reason">{{ s.reason }}</div>
        </div>
      </div>
    </div>

    <n-empty v-else-if="!loading" description="暂无推荐结果，多听歌后推荐会更精准~" style="margin-top: 80px;">
      <template #extra>
        <n-button type="primary" round @click="router.push('/songs')">去浏览音乐库</n-button>
      </template>
    </n-empty>
  </div>
</template>

<style scoped>
.rec-header {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.5s ease both;
}
.rec-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(108, 92, 231, 0.15), transparent 60%);
  animation: pulse-glow 6s ease-in-out infinite;
}
.rec-content {
  position: relative;
  z-index: 1;
}
.rec-desc {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}
.rec-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.rec-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--accent);
  background: rgba(0, 206, 201, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid rgba(0, 206, 201, 0.2);
}

.rec-reason {
  font-size: 11px;
  color: var(--accent);
  margin-top: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: rgba(0, 206, 201, 0.08);
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
