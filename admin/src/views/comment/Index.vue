<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NSpace, NButton, NTag, NSwitch, useMessage } from 'naive-ui'
import { getComments, updateCommentStatus } from '../../api'

const message = useMessage()
const loading = ref(false)
const data = ref([])
const total = ref(0)
const page = ref(1)

const columns = [
  { title: '用户', key: 'username', width: 100 },
  { title: '评论内容', key: 'content', ellipsis: { tooltip: true } },
  { title: '点赞', key: 'likeCount', width: 60 },
  { title: '时间', key: 'createdAt', width: 170, render: (row) => row.createdAt?.replace('T', ' ').substring(0, 16) || '-' },
  { title: '状态', key: 'status', width: 100, render: (row) =>
    h(NSwitch, { value: row.status === 1, size: 'small', checkedValue: '正常', uncheckedValue: '隐藏',
      onUpdateValue: (v) => toggleStatus(row.id, v ? 1 : 0) }, { checked: () => '显示', unchecked: () => '隐藏' })
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

onMounted(loadData)
</script>

<template>
  <n-card style="border-radius: 12px;">
    <n-data-table :columns="columns" :data="data" :loading="loading" :pagination="{ page, pageSize: 10, pageCount: Math.ceil(total / 10), onChange: p => { page = p; loadData() } }" :row-key="r => r.id" />
  </n-card>
</template>
