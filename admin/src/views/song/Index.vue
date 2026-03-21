<script setup>
import { ref, onMounted } from 'vue'
import { NCard, NDataTable, NSpace, NButton, NInput, NModal, NForm, NFormItem, NSelect, NInputNumber, NTag, NPopconfirm, useMessage } from 'naive-ui'
import { getSongs, createSong, updateSong, deleteSong, getArtists, getGenres } from '../../api'

const message = useMessage()
const loading = ref(false)
const data = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const showModal = ref(false)
const isEdit = ref(false)
const form = ref({ title: '', artistId: null, albumId: null, duration: null, language: '中文', coverImage: '', audioUrl: '', lyrics: '', genreIds: [] })
const artistOptions = ref([])
const genreOptions = ref([])

const columns = [
  { title: '歌曲名', key: 'title', ellipsis: { tooltip: true } },
  { title: '歌手', key: 'artistName' },
  { title: '流派', key: 'genres', render: (row) => row.genres?.map(g => g.name || g).join(', ') || '-' },
  { title: '语言', key: 'language' },
  { title: '评分', key: 'avgRating', render: (row) => `${row.avgRating || 0} (${row.ratingCount || 0}人)` },
  { title: '播放', key: 'playCount', sorter: true, render: (row) => (row.playCount || 0).toLocaleString() },
  { title: '状态', key: 'status', render: (row) => row.status === 1 ? '上架' : '下架', width: 60 },
  { title: '操作', key: 'actions', width: 160, render: (row) => {
    return [
      h(NButton, { size: 'small', tertiary: true, type: 'primary', onClick: () => editSong(row) }, { default: () => '编辑' }),
      h(NPopconfirm, { onPositiveClick: () => handleDelete(row.id) }, { trigger: () => h(NButton, { size: 'small', tertiary: true, type: 'error', style: 'margin-left:8px' }, { default: () => '下架' }), default: () => '确定下架？' })
    ]
  }}
]

async function loadData() {
  loading.value = true
  try {
    const res = await getSongs({ page: page.value, pageSize: pageSize.value, keyword: keyword.value || undefined })
    data.value = res.data.records || []
    total.value = res.data.total || 0
  } catch (e) { message.error(e.message) }
  finally { loading.value = false }
}

async function loadOptions() {
  const [ar, gr] = await Promise.all([getArtists({ pageSize: 100 }), getGenres()])
  artistOptions.value = (ar.data.records || []).map(a => ({ label: a.name, value: a.id }))
  genreOptions.value = (gr.data || []).map(g => ({ label: g.name, value: g.id }))
}

function openCreate() { isEdit.value = false; form.value = { title: '', artistId: null, duration: null, language: '中文', coverImage: '', audioUrl: '', lyrics: '', genreIds: [] }; showModal.value = true }
function editSong(row) { isEdit.value = true; form.value = { ...row, genreIds: row.genres?.map(g => g.id) || [] }; showModal.value = true }

async function handleSave() {
  if (!form.value.title || !form.value.artistId) { message.warning('歌曲名和歌手不能为空'); return }
  try {
    if (isEdit.value) { await updateSong(form.value.id, form.value) } else { await createSong(form.value) }
    message.success(isEdit.value ? '更新成功' : '添加成功')
    showModal.value = false; loadData()
  } catch (e) { message.error(e.message) }
}

async function handleDelete(id) {
  try { await deleteSong(id); message.success('已下架'); loadData() }
  catch (e) { message.error(e.message) }
}

onMounted(() => { loadData(); loadOptions() })

import { h } from 'vue'
</script>

<template>
  <n-card style="border-radius: 12px;">
    <n-space justify="space-between" style="margin-bottom: 16px;">
      <n-space>
        <n-input v-model:value="keyword" placeholder="搜索歌曲名" clearable style="width: 200px;" @keyup.enter="loadData" />
        <n-button @click="loadData">搜索</n-button>
      </n-space>
      <n-button type="primary" @click="openCreate">添加歌曲</n-button>
    </n-space>
    <n-data-table :columns="columns" :data="data" :loading="loading" :pagination="{ page, pageSize, pageCount: Math.ceil(total / pageSize), onChange: p => { page = p; loadData() } }" :row-key="r => r.id" />
  </n-card>

  <n-modal v-model:show="showModal" preset="card" :title="isEdit ? '编辑歌曲' : '添加歌曲'" style="width: 600px;" :mask-closable="false">
    <n-form :model="form" label-placement="left" label-width="80">
      <n-form-item label="歌曲名"><n-input v-model:value="form.title" placeholder="请输入歌曲名" /></n-form-item>
      <n-form-item label="歌手"><n-select v-model:value="form.artistId" :options="artistOptions" filterable placeholder="选择歌手" /></n-form-item>
      <n-form-item label="流派"><n-select v-model:value="form.genreIds" :options="genreOptions" multiple placeholder="选择流派" /></n-form-item>
      <n-form-item label="语言"><n-select v-model:value="form.language" :options="['中文','英文','日文','韩文','其他'].map(l=>({label:l,value:l}))" /></n-form-item>
      <n-form-item label="时长(秒)"><n-input-number v-model:value="form.duration" :min="0" placeholder="秒" /></n-form-item>
      <n-form-item label="封面URL"><n-input v-model:value="form.coverImage" placeholder="图片URL" /></n-form-item>
      <n-form-item label="歌词"><n-input v-model:value="form.lyrics" type="textarea" placeholder="歌词内容" :rows="4" /></n-form-item>
    </n-form>
    <template #action><n-space justify="end"><n-button @click="showModal = false">取消</n-button><n-button type="primary" @click="handleSave">确定</n-button></n-space></template>
  </n-modal>
</template>
