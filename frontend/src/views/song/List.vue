<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NSelect, NPagination, NEmpty } from 'naive-ui'
import { getSongs, getGenres } from '../../api'

const router = useRouter()
const route = useRoute()
const songs = ref([])
const total = ref(0)
const page = ref(1)
const genres = ref([])
const filters = ref({ genreId: null, language: null, sortBy: 'play_count' })

const langOptions = [{ label: '全部', value: null }, { label: '中文', value: '中文' }, { label: '英文', value: '英文' }, { label: '日文', value: '日文' }]
const sortOptions = [{ label: '播放最多', value: 'play_count' }, { label: '评分最高', value: 'avg_rating' }, { label: '最新上架', value: 'created_at' }]

async function loadData() {
  try {
    const res = await getSongs({ page: page.value, pageSize: 12, keyword: route.query.keyword || undefined, genreId: filters.value.genreId || undefined, language: filters.value.language || undefined, sortBy: filters.value.sortBy })
    songs.value = res.data.records || []; total.value = res.data.total || 0
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  const gr = await getGenres()
  genres.value = [{ label: '全部流派', value: null }, ...(gr.data || []).map(g => ({ label: g.name, value: g.id }))]
  if (route.query.genreId) filters.value.genreId = Number(route.query.genreId)
  loadData()
})

watch([() => filters.value.genreId, () => filters.value.language, () => filters.value.sortBy], () => { page.value = 1; loadData() })
watch(() => route.query.keyword, () => { page.value = 1; loadData() })
</script>

<template>
  <div class="page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="section-title">{{ route.query.keyword ? `搜索: "${route.query.keyword}"` : '音乐库' }}</h2>
      <p class="page-desc" v-if="!route.query.keyword">探索海量音乐，找到属于你的旋律</p>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <n-select v-model:value="filters.genreId" :options="genres" style="width:140px;" size="small" />
      <n-select v-model:value="filters.language" :options="langOptions" style="width:120px;" size="small" />
      <n-select v-model:value="filters.sortBy" :options="sortOptions" style="width:140px;" size="small" />
      <span class="result-count" v-if="total > 0">共 {{ total }} 首</span>
    </div>

    <!-- 歌曲网格 -->
    <div v-if="songs.length" class="grid-4">
      <div v-for="(s, idx) in songs" :key="s.id" class="song-card" @click="router.push(`/song/${s.id}`)" :style="{ animationDelay: (idx * 0.04) + 's' }">
        <div class="cover-wrap">
          <img :src="s.coverImage || 'https://picsum.photos/seed/s' + s.id + '/300'" :alt="s.title" loading="lazy" />
          <div class="play-icon"></div>
        </div>
        <div class="info">
          <div class="title">{{ s.title }}</div>
          <div class="artist">{{ s.artistName || '未知歌手' }}</div>
          <div class="meta">
            <span class="play-count">▶ {{ (s.playCount || 0).toLocaleString() }}</span>
            <span class="rating">★ {{ s.avgRating || '-' }}</span>
            <span v-if="s.commentCount" class="comment-count">💬 {{ s.commentCount }}</span>
          </div>
          <div class="card-tags" v-if="s.language || s.genreName">
            <span v-if="s.language" class="card-tag">{{ s.language }}</span>
            <span v-if="s.genreName" class="card-tag genre">{{ s.genreName }}</span>
          </div>
        </div>
      </div>
    </div>
    <n-empty v-else description="暂无歌曲" style="margin-top: 80px;" />

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > 12">
      <n-pagination v-model:page="page" :page-count="Math.ceil(total / 12)" @update:page="loadData" />
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 8px;
}
.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: -12px;
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.result-count {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-left: auto;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-bottom: 16px;
}

.comment-count {
  color: var(--text-tertiary);
}

.card-tags {
  display: flex;
  gap: 6px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.card-tag {
  font-size: 10px;
  padding: 1px 8px;
  border-radius: 10px;
  background: rgba(0, 206, 201, 0.12);
  color: #00CEC9;
  border: 1px solid rgba(0, 206, 201, 0.2);
}
.card-tag.genre {
  background: rgba(108, 92, 231, 0.12);
  color: #A29BFE;
  border-color: rgba(108, 92, 231, 0.2);
}
</style>
