<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NButton, NTag, NSwitch, NSpace, useMessage } from 'naive-ui'
import { getComments, updateCommentStatus } from '../../api'
import request from '../../utils/request'

const message = useMessage()
const loading = ref(false)
const data = ref([])
const total = ref(0)
const page = ref(1)
const backfilling = ref(false)

const sentimentColors = {
  '正向': { color: 'rgba(63,185,80,0.12)', textColor: '#3FB950' },
  '中性': { color: 'rgba(210,153,34,0.12)', textColor: '#D29922' },
  '负向': { color: 'rgba(248,81,73,0.12)', textColor: '#F85149' },
}

const columns = [
  { title: '用户', key: 'username', width: 100 },
  { title: '评论内容', key: 'content', ellipsis: { tooltip: true } },
  { title: '情感', key: 'sentimentLabel', width: 90, render: (row) =>
    row.sentimentLabel
      ? h(NTag, { size: 'small', round: true, bordered: false, color: sentimentColors[row.sentimentLabel] || {} },
          () => `${row.sentimentLabel === '正向' ? '🟢' : row.sentimentLabel === '负向' ? '🔴' : '🟡'} ${row.sentimentLabel}`)
      : '-'
  },
  { title: '得分', key: 'sentimentScore', width: 70, render: (row) => row.sentimentScore != null ? row.sentimentScore.toFixed(2) : '-' },
  { title: '时间', key: 'createdAt', width: 170, render: (row) => row.createdAt?.replace('T', ' ').substring(0, 16) || '-' },
  { title: '状态', key: 'status', width: 100, render: (row) =>
    h(NSwitch, {
      value: row.status === 1,
      size: 'small',
      'onUpdate:value': (v) => toggleStatus(row.id, v ? 1 : 0)
    }, { checked: () => '显示', unchecked: () => '隐藏' })
  }
]

async function loadData() {
  loading.value = true
  try { const res = await getComments({ page: page.value, pageSize: 10 }); data.value = res.data.records || []; total.value = res.data.total || 0 }
  catch (e) { message.error(e.message) } finally { loading.value = false }
}

async function toggleStatus(id, status) {
  try { await updateCommentStatus(id, status); message.success('状态已更新'); loadData() } catch (e) { message.error(e.message) }
}

async function backfillSentiment() {
  backfilling.value = true
  try {
    const res = await request.post('/admin/comments/backfill-sentiment')
    message.success(res.message || `已回填 ${res.data?.updated || 0} 条`)
    loadData()
  } catch (e) { message.error(e.message || '回填失败') }
  finally { backfilling.value = false }
}

onMounted(loadData)
</script>

<template>
  <n-card style="border-radius: 12px;">
    <template #header-extra>
      <n-button size="small" type="primary" ghost :loading="backfilling" @click="backfillSentiment">
        🔄 一键回填情感数据
      </n-button>
    </template>
    <n-data-table :columns="columns" :data="data" :loading="loading" :pagination="{ page, pageSize: 10, pageCount: Math.ceil(total / 10), onChange: p => { page = p; loadData() } }" :row-key="r => r.id" />
  </n-card>
</template>
