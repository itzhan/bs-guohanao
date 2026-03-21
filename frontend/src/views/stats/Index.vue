<script setup>
import { ref, onMounted, computed, shallowRef } from 'vue'
import { NCard, NGrid, NGi, NText, NSpace } from 'naive-ui'
import VChart from 'vue-echarts'
import { getOverview, getRatingDistribution, getGenreDistribution, getPlayTrend, getTopArtists, getLanguageDistribution } from '../../api'

const overview = ref({})
const ratingData = ref({})
const genreData = ref([])
const trendData = ref([])
const topArtists = ref([])
const langData = ref([])

onMounted(async () => {
  try {
    const [o, r, g, t, a, l] = await Promise.all([
      getOverview(), getRatingDistribution(), getGenreDistribution(), getPlayTrend(30), getTopArtists(10), getLanguageDistribution()
    ])
    overview.value = o.data || {}
    ratingData.value = r.data || {}
    genreData.value = g.data || []
    trendData.value = t.data || []
    topArtists.value = a.data || []
    langData.value = l.data || []
  } catch (e) { console.error(e) }
})

const overviewCards = computed(() => [
  { label: '歌曲总数', key: 'totalSongs', icon: '🎵', gradient: 'linear-gradient(135deg, #6C5CE7, #A29BFE)' },
  { label: '用户总数', key: 'totalUsers', icon: '👥', gradient: 'linear-gradient(135deg, #00CEC9, #81ECEC)' },
  { label: '播放总量', key: 'totalPlays', icon: '▶', gradient: 'linear-gradient(135deg, #FD79A8, #FDCB6E)' },
  { label: '评论数', key: 'totalComments', icon: '💬', gradient: 'linear-gradient(135deg, #E17055, #FAB1A0)' },
])

// ---- ECharts 配置 ----
const chartColors = ['#6C5CE7', '#00CEC9', '#FD79A8', '#FDCB6E', '#E17055', '#A29BFE', '#81ECEC', '#74B9FF', '#55EFC4', '#DFE6E9']
const textStyle = { color: '#8B949E', fontFamily: 'Inter, sans-serif' }

// 流派分布 - 玫瑰饼图
const genreChartOption = computed(() => ({
  tooltip: { trigger: 'item', backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3' }, formatter: '{b}: {c} 首 ({d}%)' },
  series: [{
    type: 'pie',
    radius: ['20%', '70%'],
    roseType: 'area',
    itemStyle: { borderRadius: 6, borderColor: '#161B22', borderWidth: 2 },
    label: { color: '#8B949E', fontSize: 12 },
    data: genreData.value.slice(0, 10).map((g, i) => ({
      value: g.value, name: g.name, itemStyle: { color: chartColors[i % chartColors.length] }
    })),
    animationType: 'scale',
    animationEasing: 'elasticOut',
    animationDelay: (idx) => idx * 100,
  }],
}))

// 评分分布 - 柱状图
const ratingChartOption = computed(() => {
  const barColors = ['#F85149', '#E17055', '#FDCB6E', '#55EFC4', '#3FB950']
  return {
    tooltip: { trigger: 'axis', backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3' } },
    xAxis: { type: 'category', data: ['1星', '2星', '3星', '4星', '5星'], axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }, axisLabel: { color: '#8B949E' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
    series: [{
      type: 'bar',
      barWidth: '50%',
      data: [1, 2, 3, 4, 5].map((i, idx) => ({
        value: ratingData.value[String(i)] || 0,
        itemStyle: { color: barColors[idx], borderRadius: [6, 6, 0, 0] }
      })),
      animationDelay: (idx) => idx * 150,
    }],
    grid: { left: 40, right: 16, top: 16, bottom: 32 },
  }
})

// 播放趋势 - 面积折线图
const trendChartOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3' } },
  xAxis: {
    type: 'category',
    data: trendData.value.map(d => d.date?.substring(5) || ''),
    axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
    axisLabel: { color: '#8B949E', fontSize: 10, interval: Math.floor(trendData.value.length / 7) },
    boundaryGap: false,
  },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
  series: [{
    type: 'line',
    data: trendData.value.map(d => d.count || 0),
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: '#6C5CE7' },
    areaStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: 'rgba(108,92,231,0.3)' }, { offset: 1, color: 'rgba(108,92,231,0.02)' }]
      }
    },
  }],
  grid: { left: 40, right: 16, top: 16, bottom: 32 },
}))

// 热门歌手 - 水平条形图
const artistChartOption = computed(() => {
  const sorted = [...topArtists.value].reverse()
  return {
    tooltip: { trigger: 'axis', backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3' } },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
    yAxis: {
      type: 'category',
      data: sorted.map(a => a.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#E6EDF3', fontSize: 12 },
    },
    series: [{
      type: 'bar',
      data: sorted.map((a, idx) => ({
        value: a.totalPlays || 0,
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [{ offset: 0, color: '#6C5CE7' }, { offset: 1, color: '#00CEC9' }]
          },
          borderRadius: [0, 4, 4, 0],
        }
      })),
      barWidth: '60%',
      animationDelay: (idx) => idx * 100,
    }],
    grid: { left: 80, right: 24, top: 8, bottom: 8 },
  }
})

// 语言分布 - 环形图
const langChartOption = computed(() => ({
  tooltip: { trigger: 'item', backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3' }, formatter: '{b}: {c} 首 ({d}%)' },
  legend: { bottom: 0, textStyle: { color: '#8B949E', fontSize: 12 } },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    center: ['50%', '45%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 8, borderColor: '#161B22', borderWidth: 2 },
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#E6EDF3' } },
    data: langData.value.map((l, i) => ({
      value: l.value, name: l.name, itemStyle: { color: chartColors[i % chartColors.length] }
    })),
  }],
}))
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2 class="section-title">数据分析看板</h2>
      <p class="page-desc">音乐推荐系统运营数据全景展示</p>
    </div>

    <!-- 概览卡片 -->
    <div class="overview-grid">
      <div v-for="(item, idx) in overviewCards" :key="idx" class="overview-card">
        <div class="overview-icon" :style="{ background: item.gradient }">{{ item.icon }}</div>
        <div class="overview-data">
          <div class="overview-label">{{ item.label }}</div>
          <div class="overview-value">{{ (overview[item.key] || 0).toLocaleString() }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="charts-grid">
      <!-- 流派分布 -->
      <div class="chart-card">
        <h3 class="chart-title">流派分布</h3>
        <v-chart :option="genreChartOption" autoresize style="height: 300px;" />
      </div>

      <!-- 评分分布 -->
      <div class="chart-card">
        <h3 class="chart-title">评分分布</h3>
        <v-chart :option="ratingChartOption" autoresize style="height: 300px;" />
      </div>

      <!-- 播放趋势 -->
      <div class="chart-card span-2">
        <h3 class="chart-title">播放趋势 <span class="chart-subtitle">近30天</span></h3>
        <v-chart :option="trendChartOption" autoresize style="height: 280px;" />
      </div>

      <!-- 热门歌手 -->
      <div class="chart-card">
        <h3 class="chart-title">热门歌手 Top 10</h3>
        <v-chart :option="artistChartOption" autoresize style="height: 320px;" />
      </div>

      <!-- 语言分布 -->
      <div class="chart-card">
        <h3 class="chart-title">语言分布</h3>
        <v-chart :option="langChartOption" autoresize style="height: 320px;" />
      </div>
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
  margin-bottom: 24px;
}

/* 概览卡片 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
@media (max-width: 768px) {
  .overview-grid { grid-template-columns: repeat(2, 1fr); }
}
.overview-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all var(--transition);
  animation: fadeInUp 0.5s ease both;
}
.overview-card:nth-child(1) { animation-delay: 0s; }
.overview-card:nth-child(2) { animation-delay: 0.05s; }
.overview-card:nth-child(3) { animation-delay: 0.1s; }
.overview-card:nth-child(4) { animation-delay: 0.15s; }
.overview-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
}
.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}
.overview-data {
  flex: 1;
}
.overview-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}
.overview-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -1px;
}

/* 图表卡片 */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 768px) {
  .charts-grid { grid-template-columns: 1fr; }
  .chart-card.span-2 { grid-column: 1; }
}
.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 24px;
  animation: fadeInUp 0.5s ease both;
}
.chart-card.span-2 {
  grid-column: 1 / -1;
}
.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.chart-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 400;
}
</style>
