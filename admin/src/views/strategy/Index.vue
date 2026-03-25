<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { NCard, NButton, NInputNumber, NSwitch, NSpace, NText, NIcon, NDescriptions, NDescriptionsItem, useMessage } from 'naive-ui'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, GaugeChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getStrategyMetrics, getStrategyConfig, updateStrategyConfig } from '../../api'

use([CanvasRenderer, PieChart, BarChart, GaugeChart, GridComponent, TooltipComponent, LegendComponent])

const message = useMessage()
const metrics = ref({})
const config = ref({})
const loaded = ref(false)
const saving = ref(false)

onMounted(async () => {
  try {
    const [m, c] = await Promise.all([getStrategyMetrics(), getStrategyConfig()])
    metrics.value = m.data || {}
    config.value = c.data || {}
  } catch (e) { console.error(e) }
  await nextTick()
  loaded.value = true
})

async function saveConfig() {
  saving.value = true
  try {
    const res = await updateStrategyConfig(config.value)
    config.value = res.data || config.value
    message.success('策略配置已保存')
  } catch (e) { message.error(e.message || '保存失败') }
  finally { saving.value = false }
}

const darkTooltip = { backgroundColor: '#21262D', borderColor: 'rgba(255,255,255,0.08)', textStyle: { color: '#E6EDF3', fontSize: 13 }, borderWidth: 1 }
const colors = ['#6C5CE7', '#00CEC9', '#FD79A8', '#D29922', '#58A6FF', '#3FB950', '#F85149', '#a29bfe']

// 推荐分数分布饼图
const scoreOption = computed(() => ({
  tooltip: { ...darkTooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'pie', radius: ['40%', '70%'], center: ['50%', '50%'],
    padAngle: 2, itemStyle: { borderRadius: 6 },
    label: { color: '#8B949E', fontSize: 11 },
    data: (metrics.value.scoreDistribution || []).map((d, i) => ({
      name: d.name, value: d.value, itemStyle: { color: colors[i] }
    })),
  }],
}))

// 算法分布饼图
const algoOption = computed(() => ({
  tooltip: { ...darkTooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'pie', radius: ['40%', '70%'], center: ['50%', '50%'],
    padAngle: 2, itemStyle: { borderRadius: 6 },
    label: { color: '#8B949E', fontSize: 12 },
    data: (metrics.value.algorithmDistribution || []).map((d, i) => ({
      name: d.name, value: d.value, itemStyle: { color: colors[i] }
    })),
  }],
}))

// 覆盖率仪表盘
const coverageOption = computed(() => ({
  series: [{
    type: 'gauge', startAngle: 200, endAngle: -20,
    min: 0, max: 100,
    progress: { show: true, width: 16, itemStyle: { color: '#6C5CE7' } },
    axisLine: { lineStyle: { width: 16, color: [[1, 'rgba(255,255,255,0.08)']] } },
    axisTick: { show: false }, splitLine: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    title: { show: true, offsetCenter: [0, '70%'], fontSize: 14, color: '#8B949E' },
    detail: { valueAnimation: true, fontSize: 32, fontWeight: 700, color: '#E6EDF3', offsetCenter: [0, '30%'], formatter: '{value}%' },
    data: [{ value: metrics.value.coverageRate || 0, name: '歌曲覆盖率' }],
  }],
}))

// 点击率仪表盘
const readRateOption = computed(() => ({
  series: [{
    type: 'gauge', startAngle: 200, endAngle: -20,
    min: 0, max: 100,
    progress: { show: true, width: 16, itemStyle: { color: '#00CEC9' } },
    axisLine: { lineStyle: { width: 16, color: [[1, 'rgba(255,255,255,0.08)']] } },
    axisTick: { show: false }, splitLine: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    title: { show: true, offsetCenter: [0, '70%'], fontSize: 14, color: '#8B949E' },
    detail: { valueAnimation: true, fontSize: 32, fontWeight: 700, color: '#E6EDF3', offsetCenter: [0, '30%'], formatter: '{value}%' },
    data: [{ value: metrics.value.readRate || 0, name: '推荐查看率' }],
  }],
}))

const metricCards = computed(() => [
  { title: '推荐总量', value: metrics.value.totalRecommendations || 0, gradient: 'linear-gradient(135deg, #6C5CE7, #a29bfe)' },
  { title: '覆盖用户数', value: metrics.value.coveredUsers || 0, gradient: 'linear-gradient(135deg, #00CEC9, #81ecec)' },
  { title: '覆盖歌曲数', value: metrics.value.coveredSongs || 0, gradient: 'linear-gradient(135deg, #FD79A8, #fab1a0)' },
  { title: '已查看', value: metrics.value.readRecommendations || 0, gradient: 'linear-gradient(135deg, #D29922, #ffeaa7)' },
])
</script>

<template>
  <div class="dashboard">
    <!-- 指标卡片 -->
    <div class="stat-grid">
      <div v-for="(s, idx) in metricCards" :key="idx" class="stat-card" :style="{ animationDelay: idx * 0.08 + 's' }">
        <div class="stat-card-bar" :style="{ background: s.gradient }"></div>
        <div class="stat-card-body">
          <div class="stat-label">{{ s.title }}</div>
          <div class="stat-value">{{ s.value.toLocaleString() }}</div>
        </div>
      </div>
    </div>

    <!-- 仪表盘 -->
    <div class="chart-row">
      <n-card class="chart-card" title="歌曲覆盖率" size="small">
        <v-chart v-if="loaded" :option="coverageOption" autoresize style="height: 240px;" />
      </n-card>
      <n-card class="chart-card" title="推荐查看率" size="small">
        <v-chart v-if="loaded" :option="readRateOption" autoresize style="height: 240px;" />
      </n-card>
    </div>

    <!-- 分布图 -->
    <div class="chart-row">
      <n-card class="chart-card" title="推荐分数分布" size="small">
        <v-chart v-if="loaded" :option="scoreOption" autoresize style="height: 260px;" />
      </n-card>
      <n-card class="chart-card" title="算法分布" size="small">
        <v-chart v-if="loaded" :option="algoOption" autoresize style="height: 260px;" />
      </n-card>
    </div>

    <!-- 参数配置 -->
    <n-card class="config-card" title="推荐算法参数配置" size="small" style="margin-top: 4px;">
      <div class="config-grid">
        <div class="config-item">
          <span class="config-label">ALS 迭代次数</span>
          <n-input-number v-model:value="config.alsMaxIter" :min="5" :max="50" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">ALS 隐因子数</span>
          <n-input-number v-model:value="config.alsRank" :min="5" :max="100" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">正则化参数</span>
          <n-input-number v-model:value="config.alsRegParam" :min="0.01" :max="1" :step="0.01" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">时间衰减基数</span>
          <n-input-number v-model:value="config.timeDecayBase" :min="0.5" :max="1" :step="0.05" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">衰减周期(天)</span>
          <n-input-number v-model:value="config.timeDecayUnit" :min="7" :max="90" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">播放权重</span>
          <n-input-number v-model:value="config.playWeight" :min="0" :max="1" :step="0.1" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">时长权重</span>
          <n-input-number v-model:value="config.durationWeight" :min="0" :max="1" :step="0.1" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">收藏加分</span>
          <n-input-number v-model:value="config.favoriteBonus" :min="0" :max="2" :step="0.1" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">推荐数量</span>
          <n-input-number v-model:value="config.recommendLimit" :min="5" :max="50" size="small" style="width: 120px;" />
        </div>
        <div class="config-item">
          <span class="config-label">冷启动问卷</span>
          <n-switch v-model:value="config.coldStartEnabled" />
        </div>
        <div class="config-item">
          <span class="config-label">热门兜底</span>
          <n-switch v-model:value="config.hotFallbackEnabled" />
        </div>
      </div>
      <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
        <n-button type="primary" :loading="saving" @click="saveConfig">保存配置</n-button>
      </div>
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
.stat-card-body { padding: 18px 16px; }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
@media (max-width: 900px) { .chart-row { grid-template-columns: 1fr; } }
.chart-card { border-radius: var(--radius-md) !important; animation: fadeInUp 0.5s ease both; }
.config-card { border-radius: var(--radius-md) !important; animation: fadeInUp 0.5s ease both; }
.config-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 900px) { .config-grid { grid-template-columns: 1fr 1fr; } }
.config-item { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: var(--radius-sm); border: 1px solid var(--border); }
.config-label { font-size: 13px; color: var(--text-secondary); flex-shrink: 0; }
</style>
