<script setup>
import { ref, onMounted, computed } from 'vue'
import { NCard, NGrid, NGridItem, NButton, NEmpty, NSpin, NTag, NDescriptions, NDescriptionsItem, NAlert, useMessage } from 'naive-ui'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, RadarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, RadarComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getExperimentComparison, runExperiment, getHdfsStatus } from '../../api'

use([CanvasRenderer, BarChart, RadarChart, GridComponent, TooltipComponent, LegendComponent, RadarComponent])

const message = useMessage()
const loading = ref(false)
const running = ref(false)
const report = ref(null)
const hdfs = ref(null)
const error = ref('')

onMounted(() => { loadData() })

async function loadData() {
  loading.value = true
  try {
    const [compRes, hdfsRes] = await Promise.all([getExperimentComparison(), getHdfsStatus()])
    if (compRes.data?.results && Object.keys(compRes.data.results).length > 0) {
      report.value = compRes.data
      error.value = ''
    } else {
      report.value = null
      error.value = compRes.data?.error || compRes.data?.hint || '暂无实验数据'
    }
    hdfs.value = hdfsRes.data
  } catch (e) {
    error.value = '加载失败: ' + (e.message || '网络错误')
  }
  loading.value = false
}

async function handleRun() {
  running.value = true
  try {
    const res = await runExperiment()
    if (res.data?.status === 'success') {
      message.success('实验完成！')
      if (res.data.report?.results) {
        report.value = res.data.report
        error.value = ''
      } else {
        // 重新加载
        await loadData()
      }
    } else {
      message.error(res.data?.error || '实验失败')
    }
  } catch (e) {
    message.error('运行失败: ' + (e.message || ''))
  }
  running.value = false
}

const darkTooltip = {
  backgroundColor: '#21262D',
  borderColor: 'rgba(255,255,255,0.08)',
  textStyle: { color: '#E6EDF3', fontSize: 13 },
  borderWidth: 1,
}

// ECharts: 算法对比柱状图
const barOption = computed(() => {
  if (!report.value?.results) return {}
  const algos = Object.keys(report.value.results)
  const metrics = ['precision', 'recall', 'ndcg']
  const metricLabels = { precision: 'Precision@K', recall: 'Recall@K', ndcg: 'NDCG@K' }
  const colors = ['#6C5CE7', '#00CEC9', '#FD79A8']

  return {
    tooltip: { ...darkTooltip, trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: metrics.map(m => metricLabels[m]), top: 10, textStyle: { color: '#8B949E' } },
    grid: { left: 40, right: 20, bottom: 30, top: 50, containLabel: true },
    xAxis: { type: 'category', data: algos, axisLabel: { color: '#8B949E' }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
    yAxis: { type: 'value', name: '%', axisLabel: { color: '#8B949E' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
    series: metrics.map((m, i) => ({
      name: metricLabels[m],
      type: 'bar',
      barWidth: 24,
      data: algos.map(a => report.value.results[a][m]),
      itemStyle: { color: colors[i], borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', fontSize: 11, color: '#ccc', formatter: '{c}%' },
    })),
  }
})

// ECharts: 覆盖率对比
const coverageOption = computed(() => {
  if (!report.value?.results) return {}
  const algos = Object.keys(report.value.results)
  const coverages = algos.map(a => report.value.results[a].coverage)
  const colors = ['#6C5CE7', '#00CEC9', '#FD79A8']

  return {
    tooltip: { ...darkTooltip, trigger: 'axis' },
    grid: { left: 40, right: 20, bottom: 30, top: 40, containLabel: true },
    xAxis: { type: 'category', data: algos, axisLabel: { color: '#8B949E' }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } } },
    yAxis: { type: 'value', name: '%', max: 100, axisLabel: { color: '#8B949E' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
    series: [{
      type: 'bar',
      barWidth: 40,
      data: coverages.map((v, i) => ({ value: v, itemStyle: { color: colors[i], borderRadius: [4, 4, 0, 0] } })),
      label: { show: true, position: 'top', fontSize: 12, color: '#ccc', formatter: '{c}%' },
    }],
  }
})

// ECharts: 雷达图
const radarOption = computed(() => {
  if (!report.value?.results) return {}
  const algos = Object.keys(report.value.results)
  const indicators = [
    { name: 'Precision', max: 100 },
    { name: 'Recall', max: 100 },
    { name: 'NDCG', max: 100 },
    { name: 'Coverage', max: 100 },
  ]
  const colors = ['#6C5CE7', '#00CEC9', '#FD79A8']

  return {
    tooltip: darkTooltip,
    legend: { data: algos, top: 10, textStyle: { color: '#8B949E' } },
    radar: {
      indicator: indicators, radius: '60%',
      axisName: { color: '#8B949E' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.04)'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
    },
    series: [{
      type: 'radar',
      data: algos.map((a, i) => ({
        name: a,
        value: [
          report.value.results[a].precision,
          report.value.results[a].recall,
          report.value.results[a].ndcg,
          report.value.results[a].coverage,
        ],
        lineStyle: { color: colors[i], width: 2 },
        areaStyle: { color: colors[i], opacity: 0.15 },
        itemStyle: { color: colors[i] },
      })),
    }],
  }
})

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}
</script>

<template>
  <div class="page">
    <n-spin :show="loading">
      <!-- 顶部操作栏 -->
      <div class="top-bar">
        <div class="top-title">
          <h2>推荐算法对比实验</h2>
          <p>对比 UserCF（基于用户协同过滤）、Content-Based（基于内容）、ALS（矩阵分解）三种算法的推荐效果</p>
        </div>
        <n-button type="primary" :loading="running" @click="handleRun" size="large">
          {{ running ? '实验运行中...' : '🚀 运行实验' }}
        </n-button>
      </div>

      <!-- 无数据提示 -->
      <n-alert v-if="error && !report" type="info" style="margin-bottom: 20px;">
        {{ error }}。请点击"运行实验"按钮开始对比测试。
      </n-alert>

      <!-- 实验结果概览 -->
      <div v-if="report" class="result-section">
        <n-grid :cols="3" :x-gap="16" :y-gap="16" style="margin-bottom: 20px;">
          <n-grid-item v-for="(metrics, algo) in report.results" :key="algo">
            <n-card :class="['algo-card', algo === report.best_algorithm ? 'best' : '']" size="small">
              <div class="algo-header">
                <span class="algo-name">{{ algo }}</span>
                <n-tag v-if="algo === report.best_algorithm" type="success" size="small">最优</n-tag>
              </div>
              <div class="algo-metrics">
                <div class="metric"><span class="metric-value">{{ metrics.precision }}%</span><span class="metric-label">Precision@K</span></div>
                <div class="metric"><span class="metric-value">{{ metrics.recall }}%</span><span class="metric-label">Recall@K</span></div>
                <div class="metric"><span class="metric-value">{{ metrics.ndcg }}%</span><span class="metric-label">NDCG@K</span></div>
                <div class="metric"><span class="metric-value">{{ metrics.coverage }}%</span><span class="metric-label">覆盖率</span></div>
              </div>
            </n-card>
          </n-grid-item>
        </n-grid>

        <!-- 图表 -->
        <n-grid :cols="2" :x-gap="16" :y-gap="16">
          <n-grid-item>
            <n-card title="准确率 / 召回率 / NDCG 对比" size="small" class="chart-card">
              <v-chart :option="barOption" style="height: 320px;" autoresize />
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card title="综合性能雷达图" size="small" class="chart-card">
              <v-chart :option="radarOption" style="height: 320px;" autoresize />
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card title="推荐覆盖率对比" size="small" class="chart-card">
              <v-chart :option="coverageOption" style="height: 280px;" autoresize />
            </n-card>
          </n-grid-item>
          <n-grid-item>
            <n-card title="实验参数" size="small" class="chart-card">
              <n-descriptions bordered :column="1" size="small">
                <n-descriptions-item label="实验时间">{{ report.timestamp }}</n-descriptions-item>
                <n-descriptions-item label="Top-K">{{ report.k }}</n-descriptions-item>
                <n-descriptions-item label="训练集大小">{{ report.train_size }} 条</n-descriptions-item>
                <n-descriptions-item label="测试集大小">{{ report.test_size }} 条</n-descriptions-item>
                <n-descriptions-item label="用户数">{{ report.total_users }}</n-descriptions-item>
                <n-descriptions-item label="歌曲数">{{ report.total_songs }}</n-descriptions-item>
                <n-descriptions-item label="最佳算法">
                  <n-tag type="success">{{ report.best_algorithm }}</n-tag>
                </n-descriptions-item>
              </n-descriptions>
              <div class="conclusion" v-if="report.conclusion">
                <h4>📊 实验结论</h4>
                <p>{{ report.conclusion }}</p>
              </div>
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>

      <!-- HDFS 存储状态 -->
      <n-card title="HDFS 分布式存储状态" size="small" style="margin-top: 20px;" class="chart-card">
        <div v-if="hdfs?.connected" class="hdfs-info">
          <n-descriptions bordered :column="2" size="small">
            <n-descriptions-item label="连接状态"><n-tag type="success" size="small">已连接</n-tag></n-descriptions-item>
            <n-descriptions-item label="HDFS URL">{{ hdfs.hdfs_url }}</n-descriptions-item>
            <n-descriptions-item label="数据目录">{{ hdfs.base_path }}</n-descriptions-item>
            <n-descriptions-item label="文件数量">{{ hdfs.file_count }} 个</n-descriptions-item>
            <n-descriptions-item label="总大小">{{ hdfs.total_size_mb }} MB</n-descriptions-item>
          </n-descriptions>
          <div class="hdfs-files" v-if="hdfs.files?.length">
            <h4>存储文件列表</h4>
            <div class="file-item" v-for="f in hdfs.files" :key="f.name">
              <span class="file-name">📄 {{ f.name }}</span>
              <span class="file-size">{{ formatBytes(f.size) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="hdfs-offline">
          <n-tag type="warning" size="small">未连接</n-tag>
          <span style="margin-left: 8px; color: var(--text-secondary);">
            {{ hdfs?.error || 'HDFS 服务需要在 Docker 环境中运行' }}
          </span>
        </div>
      </n-card>
    </n-spin>
  </div>
</template>

<style scoped>
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  animation: fadeInUp 0.5s ease both;
}
.top-title h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
}
.top-title p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.chart-card {
  border-radius: var(--radius-md) !important;
  animation: fadeInUp 0.5s ease both;
}

.algo-card {
  border: 1px solid var(--border);
  border-radius: var(--radius-md) !important;
  transition: all 0.3s;
  animation: fadeInUp 0.5s ease both;
}
.algo-card.best {
  border-color: rgba(0, 206, 201, 0.4);
  box-shadow: 0 0 16px rgba(0, 206, 201, 0.1);
}
.algo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.algo-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}
.algo-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
}
.metric-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.conclusion {
  margin-top: 16px;
  padding: 12px;
  background: rgba(108, 92, 231, 0.08);
  border-radius: 8px;
  border: 1px solid rgba(108, 92, 231, 0.15);
}
.conclusion h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: var(--text-primary);
}
.conclusion p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hdfs-info {
  animation: fadeInUp 0.3s ease both;
}
.hdfs-files {
  margin-top: 16px;
}
.hdfs-files h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 8px;
}
.file-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
}
.file-name { color: var(--text-primary); }
.file-size { color: var(--text-tertiary); }
.hdfs-offline {
  display: flex;
  align-items: center;
  padding: 8px 0;
}
</style>
