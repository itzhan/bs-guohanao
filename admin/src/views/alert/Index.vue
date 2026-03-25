<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { NCard, NDataTable, NTag, NSpace, NText, NIcon, NSelect } from 'naive-ui'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { WarningOutline, AlertCircleOutline, InformationCircleOutline, ShieldCheckmarkOutline } from '@vicons/ionicons5'
import { getAlertList, getAlertStats } from '../../api'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const stats = ref({})
const alerts = ref([])
const loaded = ref(false)
const days = ref(7)

async function loadData() {
  loaded.value = false
  try {
    const [s, a] = await Promise.all([getAlertStats(), getAlertList(days.value)])
    stats.value = s.data || {}
    alerts.value = a.data || []
  } catch (e) { console.error(e) }
  await nextTick()
  loaded.value = true
}

onMounted(loadData)

const daysOptions = [
  { label: '最近7天', value: 7 },
  { label: '最近14天', value: 14 },
  { label: '最近30天', value: 30 },
]

function handleDaysChange(val) {
  days.value = val
  loadData()
}

const darkTooltip = { backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3', fontSize: 13 }, borderWidth: 1 }

// 预警类型分布
const typeOption = computed(() => ({
  tooltip: { ...darkTooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'pie', radius: ['40%', '70%'], center: ['50%', '50%'],
    padAngle: 2, itemStyle: { borderRadius: 6 },
    label: { color: '#8B949E', fontSize: 12 },
    data: (stats.value.typeDistribution || []).map((d, i) => ({
      name: d.name, value: d.value,
      itemStyle: { color: ['#F85149', '#D29922', '#58A6FF', '#3FB950'][i] || '#8B949E' }
    })),
  }],
}))

const severityMap = { high: { text: '高危', type: 'error' }, medium: { text: '中危', type: 'warning' }, low: { text: '低危', type: 'info' } }

const columns = [
  { title: '预警类型', key: 'type', width: 120, render: (row) => {
    return row.type
  }},
  { title: '严重程度', key: 'severity', width: 100, render: (row) => {
    const s = severityMap[row.severity] || { text: row.severity, type: 'default' }
    return h(NTag, { type: s.type, size: 'small', round: true }, { default: () => s.text })
  }},
  { title: '用户', key: 'username', width: 120 },
  { title: '描述', key: 'description' },
  { title: '数量', key: 'count', width: 80 },
  { title: '检测时间', key: 'detectedAt', width: 160, render: (row) => row.detectedAt?.replace('T', ' ')?.substring(0, 19) || '' },
]

import { h } from 'vue'

const statCards = computed(() => [
  { title: '预警总数', value: stats.value.totalAlerts || 0, gradient: 'linear-gradient(135deg, #58A6FF, #74b9ff)', icon: ShieldCheckmarkOutline },
  { title: '高危预警', value: stats.value.highCount || 0, gradient: 'linear-gradient(135deg, #F85149, #ff7675)', icon: AlertCircleOutline },
  { title: '中危预警', value: stats.value.mediumCount || 0, gradient: 'linear-gradient(135deg, #D29922, #ffeaa7)', icon: WarningOutline },
  { title: '低危提示', value: stats.value.lowCount || 0, gradient: 'linear-gradient(135deg, #3FB950, #55efc4)', icon: InformationCircleOutline },
])
</script>

<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div v-for="(s, idx) in statCards" :key="idx" class="stat-card" :style="{ animationDelay: idx * 0.08 + 's' }">
        <div class="stat-card-bar" :style="{ background: s.gradient }"></div>
        <div class="stat-card-body">
          <div class="stat-info">
            <div class="stat-label">{{ s.title }}</div>
            <div class="stat-value">{{ s.value }}</div>
          </div>
          <div class="stat-icon" :style="{ background: s.gradient }">
            <n-icon size="22" color="#fff"><component :is="s.icon" /></n-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 类型分布 + 筛选 -->
    <div class="chart-row">
      <n-card class="chart-card" title="预警类型分布" size="small">
        <v-chart v-if="loaded" :option="typeOption" autoresize style="height: 260px;" />
      </n-card>
      <n-card class="chart-card" size="small">
        <template #header>
          <n-space justify="space-between" align="center" style="width: 100%;">
            <span>预警时间范围</span>
            <n-select :value="days" :options="daysOptions" @update:value="handleDaysChange" style="width: 140px;" size="small" />
          </n-space>
        </template>
        <div class="alert-summary">
          <p v-if="alerts.length === 0" style="color: var(--text-tertiary); text-align: center; padding: 60px 0;">
            🎉 所选时间范围内无异常预警
          </p>
          <div v-else>
            <div v-for="type in ['刷分行为', '刷量行为', '异常登录', '用户不活跃']" :key="type">
              <div class="alert-type-row" v-if="alerts.filter(a => a.type === type).length">
                <n-text strong>{{ type }}</n-text>
                <n-tag size="small" round>{{ alerts.filter(a => a.type === type).length }}</n-tag>
              </div>
            </div>
          </div>
        </div>
      </n-card>
    </div>

    <!-- 预警列表 -->
    <n-card class="alert-table-card" title="预警详情列表" size="small">
      <n-data-table :columns="columns" :data="alerts" :row-key="(r) => r.id" :bordered="false"
        :pagination="{ pageSize: 15 }" size="small" />
    </n-card>
  </div>
</template>

<style scoped>
.dashboard { animation: fadeInUp 0.4s ease both; }
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
@media (max-width: 1200px) { .stat-grid { grid-template-columns: repeat(2, 1fr); } }
.stat-card { background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid var(--border); overflow: hidden; transition: all var(--transition); animation: fadeInUp 0.5s ease both; }
.stat-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); border-color: var(--border-hover); }
.stat-card-bar { height: 3px; width: 100%; }
.stat-card-body { padding: 18px 16px; display: flex; align-items: center; justify-content: space-between; }
.stat-info { flex: 1; }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
.stat-value { font-size: 26px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; opacity: 0.85; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
@media (max-width: 900px) { .chart-row { grid-template-columns: 1fr; } }
.chart-card { border-radius: var(--radius-md) !important; animation: fadeInUp 0.5s ease both; }
.alert-table-card { border-radius: var(--radius-md) !important; animation: fadeInUp 0.5s ease 0.4s both; }
.alert-summary { padding: 8px 0; }
.alert-type-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 4px; border-bottom: 1px solid var(--border); }
.alert-type-row:last-child { border-bottom: none; }
</style>
