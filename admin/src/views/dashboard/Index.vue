<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { NGrid, NGi, NCard, NSpace, NText, NIcon } from 'naive-ui'
import { PeopleOutline, MusicalNotesOutline, PersonOutline, StarOutline, PlayOutline, ChatbubblesOutline } from '@vicons/ionicons5'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, RadarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, RadarComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getOverview, getRatingDistribution, getGenreDistribution, getTopArtists, getLanguageDistribution } from '../../api'

use([CanvasRenderer, BarChart, PieChart, RadarChart, GridComponent, TooltipComponent, LegendComponent, RadarComponent])

const overview = ref({})
const ratingData = ref({})
const genreData = ref([])

const topArtists = ref([])
const langData = ref([])
const loaded = ref(false)

onMounted(async () => {
  try {
    const [o, r, g, a, l] = await Promise.all([
      getOverview(), getRatingDistribution(), getGenreDistribution(),
      getTopArtists(5), getLanguageDistribution()
    ])
    overview.value = o.data || {}
    ratingData.value = r.data || {}
    genreData.value = g.data || []
    topArtists.value = a.data || []
    langData.value = l.data || []
  } catch (e) { console.error(e) }
  await nextTick()
  loaded.value = true
})

const statCards = [
  { title: '用户总数', key: 'totalUsers', gradient: 'linear-gradient(135deg, #6C5CE7, #a29bfe)', icon: PeopleOutline },
  { title: '歌曲总数', key: 'totalSongs', gradient: 'linear-gradient(135deg, #00CEC9, #81ecec)', icon: MusicalNotesOutline },
  { title: '歌手数量', key: 'totalArtists', gradient: 'linear-gradient(135deg, #FD79A8, #fab1a0)', icon: PersonOutline },
  { title: '评分次数', key: 'totalRatings', gradient: 'linear-gradient(135deg, #D29922, #ffeaa7)', icon: StarOutline },
  { title: '播放总量', key: 'totalPlays', gradient: 'linear-gradient(135deg, #58A6FF, #74b9ff)', icon: PlayOutline },
  { title: '评论数量', key: 'totalComments', gradient: 'linear-gradient(135deg, #3FB950, #55efc4)', icon: ChatbubblesOutline },
]

// ECharts 通用暗色 tooltip
const darkTooltip = {
  backgroundColor: '#21262D',
  borderColor: 'rgba(255,255,255,0.08)',
  textStyle: { color: '#E6EDF3', fontSize: 13 },
  borderWidth: 1,
}

// 评分分布柱状图
const ratingOption = computed(() => {
  const labels = ['1星', '2星', '3星', '4星', '5星']
  const colors = ['#F85149', '#D29922', '#ffc53d', '#3FB950', '#6C5CE7']
  const vals = labels.map((_, i) => ratingData.value[String(i + 1)] || 0)
  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category', data: labels,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#8B949E' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
      axisLabel: { color: '#8B949E' },
    },
    series: [{
      type: 'bar', barWidth: '40%', data: vals.map((v, i) => ({
        value: v,
        itemStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: colors[i] },
              { offset: 1, color: colors[i] + '66' },
            ]
          },
          borderRadius: [6, 6, 0, 0],
        }
      })),
    }]
  }
})

// 流派分布水平条形图
const genreOption = computed(() => {
  const items = genreData.value.slice(0, 8).reverse()
  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 80, right: 30, top: 10, bottom: 20 },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
      axisLabel: { color: '#8B949E' },
    },
    yAxis: {
      type: 'category', data: items.map(g => g.name),
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#C9D1D9', fontSize: 12 },
    },
    series: [{
      type: 'bar', barWidth: '50%',
      data: items.map(g => g.value),
      itemStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: '#6C5CE7' },
            { offset: 1, color: '#00CEC9' },
          ]
        },
        borderRadius: [0, 4, 4, 0],
      }
    }]
  }
})

// 数据概览雷达图
const radarOption = computed(() => {
  const indicators = [
    { name: '用户', key: 'totalUsers' },
    { name: '歌曲', key: 'totalSongs' },
    { name: '歌手', key: 'totalArtists' },
    { name: '评分', key: 'totalRatings' },
    { name: '播放', key: 'totalPlays' },
    { name: '评论', key: 'totalComments' },
  ]
  const vals = indicators.map(i => overview.value[i.key] || 0)
  const maxVal = Math.max(...vals, 1)
  return {
    tooltip: { ...darkTooltip, trigger: 'item' },
    radar: {
      indicator: indicators.map(i => ({ name: i.name, max: maxVal })),
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: '#8B949E', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitArea: { areaStyle: { color: ['rgba(108,92,231,0.02)', 'rgba(108,92,231,0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: vals,
        name: '数据概览',
        areaStyle: {
          color: {
            type: 'radial', x: 0.5, y: 0.5, r: 0.5,
            colorStops: [
              { offset: 0, color: 'rgba(108, 92, 231, 0.5)' },
              { offset: 1, color: 'rgba(0, 206, 201, 0.15)' },
            ]
          }
        },
        lineStyle: { color: '#6C5CE7', width: 2 },
        itemStyle: { color: '#6C5CE7', borderColor: '#fff', borderWidth: 1 },
      }],
      symbol: 'circle', symbolSize: 6,
    }]
  }
})

// 语言分布环形图
const langOption = computed(() => {
  const colors = ['#6C5CE7', '#00CEC9', '#FD79A8', '#D29922', '#58A6FF', '#3FB950', '#F85149', '#a29bfe']
  return {
    tooltip: { ...darkTooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical', right: 10, top: 'center',
      textStyle: { color: '#8B949E', fontSize: 12 },
      itemWidth: 12, itemHeight: 12, itemGap: 10,
      icon: 'roundRect',
    },
    series: [{
      type: 'pie', radius: ['45%', '72%'], center: ['35%', '50%'],
      padAngle: 2, itemStyle: { borderRadius: 6 },
      label: { show: false },
      data: langData.value.map((d, i) => ({
        name: d.name, value: d.value,
        itemStyle: { color: colors[i % colors.length] }
      })),
      emphasis: {
        scaleSize: 8,
        itemStyle: { shadowBlur: 20, shadowColor: 'rgba(0,0,0,0.3)' }
      }
    }]
  }
})

const medalColors = [
  'linear-gradient(135deg, #ffd700, #ffaa00)',
  'linear-gradient(135deg, #c0c0c0, #e0e0e0)',
  'linear-gradient(135deg, #cd7f32, #daa06d)',
  'linear-gradient(135deg, #6C5CE7, #a29bfe)',
  'linear-gradient(135deg, #00CEC9, #81ecec)',
]
</script>

<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div v-for="(s, idx) in statCards" :key="s.key" class="stat-card"
        :style="{ animationDelay: idx * 0.08 + 's' }">
        <div class="stat-card-bar" :style="{ background: s.gradient }"></div>
        <div class="stat-card-body">
          <div class="stat-info">
            <div class="stat-label">{{ s.title }}</div>
            <div class="stat-value">{{ (overview[s.key] || 0).toLocaleString() }}</div>
          </div>
          <div class="stat-icon" :style="{ background: s.gradient }">
            <n-icon size="22" color="#fff"><component :is="s.icon" /></n-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区：第一行 -->
    <div class="chart-row">
      <n-card class="chart-card" title="评分分布" size="small" :style="{ animationDelay: '0.5s' }">
        <v-chart :option="ratingOption" autoresize style="height: 260px;" />
      </n-card>
      <n-card class="chart-card" title="流派分布 Top 8" size="small" :style="{ animationDelay: '0.6s' }">
        <v-chart :option="genreOption" autoresize style="height: 260px;" />
      </n-card>
    </div>

    <!-- 图表区：第二行 -->
    <div class="chart-row">
      <n-card class="chart-card" title="数据概览" size="small" :style="{ animationDelay: '0.7s' }">
        <v-chart :option="radarOption" autoresize style="height: 260px;" />
      </n-card>
      <n-card class="chart-card" title="语言分布" size="small" :style="{ animationDelay: '0.8s' }">
        <v-chart :option="langOption" autoresize style="height: 260px;" />
      </n-card>
    </div>

    <!-- 热门歌手 -->
    <n-card class="top-artists-card" title="热门歌手 Top 5" size="small" :style="{ animationDelay: '0.9s' }">
      <div class="artist-list">
        <div v-for="(a, idx) in topArtists" :key="a.id" class="artist-item">
          <div class="artist-rank" :style="{ background: medalColors[idx] }">{{ idx + 1 }}</div>
          <div class="artist-info">
            <n-text strong style="font-size: 14px;">{{ a.name }}</n-text>
            <n-text class="artist-plays">
              <n-icon size="13" style="vertical-align: -2px; margin-right: 4px;"><PlayOutline /></n-icon>
              {{ (a.totalPlays || 0).toLocaleString() }}
            </n-text>
          </div>
          <div class="artist-bar-wrap">
            <div class="artist-bar-fill"
              :style="{
                width: (topArtists.length && topArtists[0].totalPlays ? ((a.totalPlays || 0) / topArtists[0].totalPlays * 100) : 0) + '%',
                background: medalColors[idx]
              }">
            </div>
          </div>
        </div>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.dashboard {
  animation: fadeInUp 0.4s ease both;
}

/* =================== */
/* 统计卡片网格         */
/* =================== */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

@media (max-width: 1400px) {
  .stat-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 900px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  overflow: hidden;
  position: relative;
  transition: all var(--transition);
  animation: fadeInUp 0.5s ease both;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

.stat-card-bar {
  height: 3px;
  width: 100%;
}

.stat-card-body {
  padding: 18px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info { flex: 1; }

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  opacity: 0.85;
}

/* =================== */
/* 图表布局             */
/* =================== */
.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

@media (max-width: 900px) {
  .chart-row { grid-template-columns: 1fr; }
}

.chart-card {
  border-radius: var(--radius-md) !important;
  animation: fadeInUp 0.5s ease both;
}

/* =================== */
/* 热门歌手             */
/* =================== */
.top-artists-card {
  border-radius: var(--radius-md) !important;
  margin-bottom: 20px;
  animation: fadeInUp 0.5s ease both;
}

.artist-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.artist-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 8px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.artist-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.artist-rank {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  color: #fff;
  flex-shrink: 0;
}

.artist-info {
  flex-shrink: 0;
  width: 160px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.artist-plays {
  font-size: 12px;
  color: var(--text-secondary);
}

.artist-bar-wrap {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  overflow: hidden;
}

.artist-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
