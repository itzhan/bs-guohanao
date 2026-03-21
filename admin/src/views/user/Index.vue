<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NSpace, NButton, NInput, NModal, NForm, NFormItem, NSelect, NTag, NPopconfirm, NSwitch, useMessage } from 'naive-ui'
import { getUsers, updateUserStatus, updateUserRole } from '../../api'

const message = useMessage()
const loading = ref(false)
const data = ref([])
const total = ref(0)
const page = ref(1)
const keyword = ref('')

const columns = [
  { title: '用户名', key: 'username' },
  { title: '昵称', key: 'nickname' },
  { title: '邮箱', key: 'email', ellipsis: { tooltip: true } },
  { title: '角色', key: 'role', width: 100, render: (row) => h(NTag, { type: row.role === 'admin' ? 'error' : row.role === 'operator' ? 'warning' : 'info', size: 'small' }, { default: () => ({ admin: '管理员', operator: '运营', user: '用户' }[row.role] || row.role) }) },
  { title: '状态', key: 'status', width: 80, render: (row) => h(NSwitch, { value: row.status === 1, onUpdateValue: (v) => toggleStatus(row.id, v ? 1 : 0), size: 'small' }) },
  { title: '注册时间', key: 'createdAt', width: 170, render: (row) => row.createdAt?.replace('T', ' ').substring(0, 16) || '-' },
  { title: '操作', key: 'actions', width: 140, render: (row) => {
    return h(NSelect, { size: 'small', value: row.role, options: [{ label: '用户', value: 'user' }, { label: '运营', value: 'operator' }, { label: '管理员', value: 'admin' }], onUpdateValue: v => changeRole(row.id, v), style: 'width: 120px' })
  }}
]

async function loadData() {
  loading.value = true
  try {
    const res = await getUsers({ page: page.value, pageSize: 10, keyword: keyword.value || undefined })
    data.value = res.data.records || []
    total.value = res.data.total || 0
  } catch (e) { message.error(e.message) }
  finally { loading.value = false }
}

async function toggleStatus(id, status) { try { await updateUserStatus(id, status); message.success('操作成功'); loadData() } catch (e) { message.error(e.message) } }
async function changeRole(id, role) { try { await updateUserRole(id, role); message.success('角色修改成功'); loadData() } catch (e) { message.error(e.message) } }

onMounted(loadData)
</script>

<template>
  <n-card style="border-radius: 12px;">
    <n-space style="margin-bottom: 16px;">
      <n-input v-model:value="keyword" placeholder="搜索用户名/昵称" clearable style="width: 220px;" @keyup.enter="loadData" />
      <n-button @click="loadData">搜索</n-button>
    </n-space>
    <n-data-table :columns="columns" :data="data" :loading="loading" :pagination="{ page, pageSize: 10, pageCount: Math.ceil(total / 10), onChange: p => { page = p; loadData() } }" :row-key="r => r.id" />
  </n-card>
</template>
