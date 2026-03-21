<script setup>
import { ref, onMounted } from 'vue'
import { NGrid, NGi, NCard, NStatistic, NSpace, NText } from 'naive-ui'
import { getOverview, getRatingDistribution, getGenreDistribution, getPlayTrend, getTopArtists } from '../../api'

const overview = ref({})
const ratingData = ref({})
const genreData = ref([])
const trendData = ref([])
const topArtists = ref([])

onMounted(async () => {
  try {
    const [o, r, g, t, a] = await Promise.all([
      getOverview(), getRatingDistribution(), getGenreDistribution(),
      getPlayTrend(30), getTopArtists(5)
    ])
    overview.value = o.data || {}
    ratingData.value = r.data || {}
    genreData.value = g.data || []
    trendData.value = t.data || []
    topArtists.value = a.data || []
  } catch (e) { console.error(e) }
})

const statCards = [
  { title: '用户总数', key: 'totalUsers', color: '#7265e6', icon: '👥' },
  { title: '歌曲总数', key: 'totalSongs', color: '#36cfc9', icon: '🎵' },
  { title: '歌手数量', key: 'totalArtists', color: '#f7629e', icon: '🎤' },
  { title: '评分次数', key: 'totalRatings', color: '#ffc53d', icon: '⭐' },
  { title: '播放总量', key: 'totalPlays', color: '#597ef7', icon: '▶️' },
  { title: '评论数量', key: 'totalComments', color: '#73d13d', icon: '💬' },
]
</script>

<template>
  <div>
    <!-- 统计卡片 -->
    <n-grid :x-gap="16" :y-gap="16" :cols="6" responsive="screen" item-responsive>
      <n-gi v-for="s in statCards" :key="s.key" span="6 s:3 m:2 l:1">
        <n-card size="small" hoverable style="border-radius: 12px;">
          <n-space align="center" justify="space-between">
            <div>
              <n-text depth="3" style="font-size: 13px;">{{ s.title }}</n-text>
              <div style="font-size: 28px; font-weight: 700; margin-top: 4px;" :style="{ color: s.color }">
                {{ (overview[s.key] || 0).toLocaleString() }}
              </div>
            </div>
            <div style="font-size: 36px; opacity: 0.3;">{{ s.icon }}</div>
          </n-space>
        </n-card>
      </n-gi>
    </n-grid>

    <n-grid :x-gap="16" :y-gap="16" :cols="2" style="margin-top: 16px;" responsive="screen" item-responsive>
      <!-- 评分分布 -->
      <n-gi span="2 m:1">
        <n-card title="评分分布" size="small" style="border-radius: 12px; min-height: 280px;">
          <div class="chart-bars">
            <div v-for="i in 5" :key="i" class="bar-item">
              <div class="bar-label">{{ i }}星</div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: barWidth(i) + '%', background: barColor(i) }"></div>
              </div>
              <div class="bar-value">{{ ratingData[String(i)] || 0 }}</div>
            </div>
          </div>
        </n-card>
      </n-gi>

      <!-- 流派占比 -->
      <n-gi span="2 m:1">
        <n-card title="流派分布 Top 8" size="small" style="border-radius: 12px; min-height: 280px;">
          <div class="genre-list">
            <div v-for="(g, idx) in genreData.slice(0, 8)" :key="idx" class="genre-item">
              <n-space justify="space-between" align="center">
                <n-text>{{ g.name }}</n-text>
                <n-text depth="3">{{ g.value }} 首</n-text>
              </n-space>
              <div class="genre-bar-track">
                <div class="genre-bar-fill" :style="{ width: genreWidth(g.value) + '%', background: genreColors[idx % genreColors.length] }"></div>
              </div>
            </div>
          </div>
        </n-card>
      </n-gi>

      <!-- 热门歌手 -->
      <n-gi span="2 m:1">
        <n-card title="热门歌手 Top 5" size="small" style="border-radius: 12px;">
          <div v-for="(a, idx) in topArtists" :key="a.id" style="display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">
            <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #fff; font-size: 14px; margin-right: 12px;"
              :style="{ background: ['#ffd700', '#c0c0c0', '#cd7f32', '#7265e6', '#36cfc9'][idx] }">{{ idx + 1 }}</div>
            <div style="flex: 1;">
              <n-text strong>{{ a.name }}</n-text>
              <n-text depth="3" style="margin-left: 8px; font-size: 12px;">播放 {{ (a.totalPlays || 0).toLocaleString() }}</n-text>
            </div>
          </div>
        </n-card>
      </n-gi>

      <!-- 播放趋势 -->
      <n-gi span="2 m:1">
        <n-card title="近30天播放趋势" size="small" style="border-radius: 12px;">
          <div v-if="trendData.length" class="trend-mini">
            <div v-for="(d, i) in trendData.slice(-14)" :key="i" class="trend-bar"
              :style="{ height: trendHeight(d.count) + 'px' }" :title="d.date + ': ' + d.count + '次'">
            </div>
          </div>
          <n-text v-else depth="3">暂无数据</n-text>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script>
export default {
  methods: {
    barWidth(i) { const total = Object.values(this.ratingData).reduce((a, b) => a + b, 0); return total ? ((this.ratingData[String(i)] || 0) / total * 100) : 0 },
    barColor(i) { return ['#ff4d4f', '#fa8c16', '#fadb14', '#a0d911', '#52c41a'][i - 1] },
    genreWidth(v) { const max = Math.max(...this.genreData.map(g => g.value), 1); return (v / max) * 100 },
    trendHeight(c) { const max = Math.max(...this.trendData.map(d => d.count), 1); return Math.max((c / max) * 60, 4) },
  },
  data() { return { genreColors: ['#7265e6', '#36cfc9', '#f7629e', '#ffc53d', '#597ef7', '#73d13d', '#ff7875', '#40a9ff'] } }
}
</script>

<style scoped>
.chart-bars { padding: 8px 0; }
.bar-item { display: flex; align-items: center; margin-bottom: 12px; }
.bar-label { width: 40px; font-size: 13px; color: #666; }
.bar-track { flex: 1; height: 20px; background: #f5f5f5; border-radius: 10px; overflow: hidden; margin: 0 12px; }
.bar-fill { height: 100%; border-radius: 10px; transition: width 0.6s ease; }
.bar-value { width: 40px; text-align: right; font-size: 13px; font-weight: 600; }
.genre-list { padding: 4px 0; }
.genre-item { margin-bottom: 10px; }
.genre-bar-track { height: 8px; background: #f5f5f5; border-radius: 4px; overflow: hidden; margin-top: 4px; }
.genre-bar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
.trend-mini { display: flex; align-items: flex-end; gap: 4px; height: 80px; padding: 8px 0; }
.trend-bar { flex: 1; background: linear-gradient(to top, #597ef7, #b37feb); border-radius: 3px; min-width: 8px; transition: height 0.4s ease; }
</style>
