<script setup>
import { ref, onMounted, computed, nextTick, h } from 'vue'
import { NCard, NGrid, NGi, NText, NIcon, NInputNumber, NSelect, NTabs, NTabPane, NDataTable, NTag, NPagination, NEmpty } from 'naive-ui'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart, HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, CalendarComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { PeopleOutline, PersonOutline, TrendingUpOutline, MusicalNotesOutline } from '@vicons/ionicons5'
import { getPortraitOverview, getPortraitPreferences, getPortraitActivity, getBehaviorLogs, getBehaviorStats } from '../../api'

use([CanvasRenderer, PieChart, BarChart, LineChart, HeatmapChart, GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, CalendarComponent])

const overview = ref({})
const prefs = ref({})
const activity = ref({})
const loaded = ref(false)

onMounted(async () => {
  try {
    const [o, p, a] = await Promise.all([getPortraitOverview(), getPortraitPreferences(), getPortraitActivity()])
    overview.value = o.data || {}
    prefs.value = p.data || {}
    activity.value = a.data || {}
  } catch (e) { console.error(e) }
  await nextTick()
  loaded.value = true
})

const darkTooltip = { backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3', fontSize: 13 }, borderWidth: 1 }
const colors = ['#6C5CE7', '#00CEC9', '#FD79A8', '#D29922', '#58A6FF', '#3FB950', '#F85149', '#a29bfe', '#81ecec', '#fab1a0']

// 性别分布饼图
const genderOption = computed(() => ({
  tooltip: { ...darkTooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'pie', radius: ['40%', '70%'], center: ['50%', '50%'],
    padAngle: 2, itemStyle: { borderRadius: 6 },
    label: { color: '#8B949E', fontSize: 12 },
    data: (overview.value.genderDistribution || []).map((d, i) => ({
      name: d.name, value: d.value, itemStyle: { color: ['#6C5CE7', '#FD79A8', '#8B949E'][i] || colors[i] }
    })),
  }],
}))

// 年龄分布柱状图
const ageOption = computed(() => {
  const items = overview.value.ageDistribution || []
  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 80, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
    yAxis: { type: 'category', data: items.map(i => i.name), axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }, axisLabel: { color: '#C9D1D9' } },
    series: [{ type: 'bar', barWidth: '50%', data: items.map((d, i) => ({ value: d.value, itemStyle: { color: colors[i], borderRadius: [0, 4, 4, 0] } })) }],
  }
})

// 流派偏好分布
const genrePrefOption = computed(() => ({
  tooltip: { ...darkTooltip, trigger: 'item', formatter: '{b}: {c} 次' },
  series: [{
    type: 'pie', radius: ['20%', '70%'], roseType: 'area',
    itemStyle: { borderRadius: 6, borderColor: '#161B22', borderWidth: 2 },
    label: { color: '#8B949E', fontSize: 11 },
    data: (prefs.value.genrePreference || []).map((d, i) => ({
      name: d.name, value: d.value, itemStyle: { color: colors[i % colors.length] }
    })),
  }],
}))

// 活跃时段柱状图
const hourOption = computed(() => {
  const items = activity.value.hourDistribution || []
  const data = Array.from({ length: 24 }, (_, i) => {
    const found = items.find(h => h.hour === i)
    return found ? found.count : 0
  })
  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 40, right: 16, top: 16, bottom: 32 },
    xAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => `${i}时`), axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }, axisLabel: { color: '#8B949E', fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
    series: [{ type: 'bar', data: data.map((v, i) => ({ value: v, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#6C5CE7' }, { offset: 1, color: '#6C5CE766' }] }, borderRadius: [4, 4, 0, 0] } })) }],
  }
})

// 星期活跃度
const weekdayOption = computed(() => {
  const items = activity.value.weekdayDistribution || []
  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 60, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'category', data: items.map(d => d.name), axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }, axisLabel: { color: '#8B949E' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
    series: [{ type: 'bar', barWidth: '50%', data: items.map((d, i) => ({ value: d.value, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#00CEC9' }, { offset: 1, color: '#00CEC966' }] }, borderRadius: [4, 4, 0, 0] } })) }],
  }
})

// DAU 趋势
const dauOption = computed(() => {
  const items = activity.value.dailyActiveUsers || []
  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 40, right: 16, top: 16, bottom: 32 },
    xAxis: { type: 'category', data: items.map(d => d.date?.substring(5) || ''), boundaryGap: false, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }, axisLabel: { color: '#8B949E', fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
    series: [{ type: 'line', data: items.map(d => d.dau), smooth: true, symbol: 'none', lineStyle: { width: 3, color: '#6C5CE7' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(108,92,231,0.3)' }, { offset: 1, color: 'rgba(108,92,231,0.02)' }] } } }],
  }
})

// 注册趋势
const regOption = computed(() => {
  const items = overview.value.registrationTrend || []
  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 40, right: 16, top: 16, bottom: 32 },
    xAxis: { type: 'category', data: items.map(d => d.month?.substring(5) || ''), boundaryGap: false, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }, axisLabel: { color: '#8B949E', fontSize: 10 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#8B949E' } },
    series: [{ type: 'line', data: items.map(d => d.count), smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: { width: 3, color: '#00CEC9' }, itemStyle: { color: '#00CEC9' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,206,201,0.3)' }, { offset: 1, color: 'rgba(0,206,201,0.02)' }] } } }],
  }
})

const statCards = computed(() => [
  { title: '活跃用户', value: prefs.value.activeUsers || 0, gradient: 'linear-gradient(135deg, #6C5CE7, #a29bfe)', icon: PeopleOutline },
  { title: '平均评分', value: prefs.value.avgRating || 0, gradient: 'linear-gradient(135deg, #D29922, #ffeaa7)', icon: TrendingUpOutline },
])

// 行为日志
const behaviorLogs = ref([])
const behaviorTotal = ref(0)
const behaviorPage = ref(1)
const behaviorStats = ref({})
const behaviorLoading = ref(false)

const actionMap = { play: '播放', rate: '评分', favorite: '收藏', search: '搜索' }
const actionColors = {
  play: { color: 'rgba(108,92,231,0.12)', textColor: '#6C5CE7' },
  rate: { color: 'rgba(253,203,110,0.12)', textColor: '#D29922' },
  favorite: { color: 'rgba(253,121,168,0.12)', textColor: '#FD79A8' },
  search: { color: 'rgba(0,206,201,0.12)', textColor: '#00CEC9' },
}

const behaviorColumns = [
  { title: '用户ID', key: 'userId', width: 80 },
  { title: '行为', key: 'action', width: 90, render: (row) =>
    h(NTag, { size: 'small', round: true, bordered: false, color: actionColors[row.action] || {} },
      () => actionMap[row.action] || row.action)
  },
  { title: '歌id', key: 'songId', width: 80 },
  { title: '时长(s)', key: 'duration', width: 80 },
  { title: '时间', key: 'timestamp', width: 170, render: (row) => row.timestamp?.replace('T', ' ').substring(0, 19) || '-' },
]

async function loadBehaviorLogs() {
  behaviorLoading.value = true
  try {
    const [logsRes, statsRes] = await Promise.all([
      getBehaviorLogs({ page: behaviorPage.value, pageSize: 15 }),
      getBehaviorStats()
    ])
    behaviorLogs.value = logsRes.data?.records || []
    behaviorTotal.value = logsRes.data?.total || 0
    behaviorStats.value = statsRes.data || {}
  } catch (e) { console.error(e) }
  behaviorLoading.value = false
}
</script>

<template>
  <div class="dashboard">
    <n-tabs type="line" animated @update:value="(v) => { if (v === 'behavior') loadBehaviorLogs() }">
      <n-tab-pane name="portrait" tab="用户画像">
    <!-- 统计卡片 -->
    <div class="stat-grid-2">
      <div v-for="(s, idx) in statCards" :key="idx" class="stat-card" :style="{ animationDelay: idx * 0.08 + 's' }">
        <div class="stat-card-bar" :style="{ background: s.gradient }"></div>
        <div class="stat-card-body">
          <div class="stat-info">
            <div class="stat-label">{{ s.title }}</div>
            <div class="stat-value">{{ typeof s.value === 'number' && s.value % 1 !== 0 ? s.value.toFixed(2) : s.value.toLocaleString?.() || s.value }}</div>
          </div>
          <div class="stat-icon" :style="{ background: s.gradient }">
            <n-icon size="22" color="#fff"><component :is="s.icon" /></n-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 第一行 -->
    <div class="chart-row">
      <n-card class="chart-card" title="性别分布" size="small" :style="{ animationDelay: '0.2s' }">
        <v-chart v-if="loaded" :option="genderOption" autoresize style="height: 260px;" />
      </n-card>
      <n-card class="chart-card" title="年龄分布" size="small" :style="{ animationDelay: '0.3s' }">
        <v-chart v-if="loaded" :option="ageOption" autoresize style="height: 260px;" />
      </n-card>
    </div>

    <!-- 第二行 -->
    <div class="chart-row">
      <n-card class="chart-card" title="流派偏好" size="small" :style="{ animationDelay: '0.4s' }">
        <v-chart v-if="loaded" :option="genrePrefOption" autoresize style="height: 280px;" />
      </n-card>
      <n-card class="chart-card" title="用户注册趋势" size="small" :style="{ animationDelay: '0.5s' }">
        <v-chart v-if="loaded" :option="regOption" autoresize style="height: 280px;" />
      </n-card>
    </div>

    <!-- 第三行 -->
    <n-card class="chart-card" title="活跃时段分布（24小时）" size="small" :style="{ animationDelay: '0.6s', marginBottom: '16px' }">
      <v-chart v-if="loaded" :option="hourOption" autoresize style="height: 260px;" />
    </n-card>

    <!-- 第四行 -->
    <div class="chart-row">
      <n-card class="chart-card" title="星期活跃度" size="small" :style="{ animationDelay: '0.7s' }">
        <v-chart v-if="loaded" :option="weekdayOption" autoresize style="height: 260px;" />
      </n-card>
      <n-card class="chart-card" title="日活跃用户趋势（30天）" size="small" :style="{ animationDelay: '0.8s' }">
        <v-chart v-if="loaded" :option="dauOption" autoresize style="height: 260px;" />
      </n-card>
    </div>
      </n-tab-pane>

      <!-- 行为日志 Tab -->
      <n-tab-pane name="behavior" tab="行为日志 (MongoDB)">
        <div class="behavior-summary" v-if="behaviorStats.totalLogs">
          <span class="behavior-total">共 {{ behaviorStats.totalLogs }} 条行为记录</span>
          <span v-for="a in (behaviorStats.actionDistribution || [])" :key="a.action" class="behavior-action-tag">
            {{ actionMap[a.action] || a.action }}: {{ a.count }}
          </span>
        </div>
        <n-data-table :columns="behaviorColumns" :data="behaviorLogs" :loading="behaviorLoading" :row-key="r => r.id" size="small" style="margin-top: 12px;" />
        <div style="display:flex;justify-content:center;margin-top:16px;" v-if="behaviorTotal > 15">
          <n-pagination v-model:page="behaviorPage" :page-count="Math.ceil(behaviorTotal / 15)" @update:page="loadBehaviorLogs" />
        </div>
        <n-empty v-if="!behaviorLoading && !behaviorLogs.length" description="暂无行为日志数据" style="margin: 60px 0;" />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<style scoped>
.dashboard { animation: fadeInUp 0.4s ease both; }
.stat-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid var(--border); overflow: hidden; transition: all var(--transition); animation: fadeInUp 0.5s ease both; }
.stat-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); border-color: var(--border-hover); }
.stat-card-bar { height: 3px; width: 100%; }
.stat-card-body { padding: 18px 16px; display: flex; align-items: center; justify-content: space-between; }
.stat-info { flex: 1; }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
.stat-value { font-size: 26px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; opacity: 0.85; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
@media (max-width: 900px) { .chart-row { grid-template-columns: 1fr; } .stat-grid-2 { grid-template-columns: 1fr; } }
.chart-card { border-radius: var(--radius-md) !important; animation: fadeInUp 0.5s ease both; }
.behavior-summary { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; padding: 12px 0; }
.behavior-total { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.behavior-action-tag { font-size: 12px; color: var(--text-secondary); background: rgba(255,255,255,0.04); padding: 2px 10px; border-radius: 10px; }
</style>
