<script setup>
import { ref, onMounted } from 'vue'
import { NCard, NDataTable, NTag, useMessage } from 'naive-ui'
import { getLogs } from '../../api'

const message = useMessage()
const loading = ref(false)
const data = ref([])
const total = ref(0)
const page = ref(1)

const columns = [
  { title: '操作用户', key: 'username', width: 100 },
  { title: '操作类型', key: 'action', width: 120 },
  { title: '模块', key: 'module', width: 100 },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '方法', key: 'requestMethod', width: 60 },
  { title: 'IP', key: 'ipAddress', width: 120 },
  { title: '状态', key: 'status', width: 60, render: (row) => row.status === 1 ? '成功' : '失败' },
  { title: '时间', key: 'createdAt', width: 170, render: (row) => row.createdAt?.replace('T', ' ').substring(0, 16) || '-' },
]

async function loadData() {
  loading.value = true
  try { const res = await getLogs({ page: page.value, pageSize: 20 }); data.value = res.data.records || []; total.value = res.data.total || 0 }
  catch (e) { message.error(e.message) } finally { loading.value = false }
}

onMounted(loadData)
</script>

<template>
  <n-card style="border-radius: 12px;">
    <n-data-table :columns="columns" :data="data" :loading="loading" :pagination="{ page, pageSize: 20, pageCount: Math.ceil(total / 20), onChange: p => { page = p; loadData() } }" :row-key="r => r.id" />
  </n-card>
</template>
