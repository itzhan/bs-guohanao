<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NSpace, NButton, NInput, NModal, NForm, NFormItem, NSelect, NPopconfirm, useMessage } from 'naive-ui'
import { getArtists, createArtist, updateArtist, deleteArtist } from '../../api'

const message = useMessage()
const loading = ref(false)
const data = ref([])
const total = ref(0)
const page = ref(1)
const showModal = ref(false)
const isEdit = ref(false)
const form = ref({ name: '', region: '华语', avatar: '', description: '' })

const columns = [
  { title: '歌手名', key: 'name' },
  { title: '地区', key: 'region', width: 80 },
  { title: '粉丝数', key: 'fansCount', render: (row) => (row.fansCount || 0).toLocaleString() },
  { title: '简介', key: 'description', ellipsis: { tooltip: true } },
  { title: '操作', key: 'actions', width: 160, render: (row) => [
    h(NButton, { size: 'small', tertiary: true, type: 'primary', onClick: () => { isEdit.value = true; form.value = { ...row }; showModal.value = true } }, { default: () => '编辑' }),
    h(NPopconfirm, { onPositiveClick: () => handleDelete(row.id) }, { trigger: () => h(NButton, { size: 'small', tertiary: true, type: 'error', style: 'margin-left:8px' }, { default: () => '删除' }), default: () => '确定删除？' })
  ]}
]

async function loadData() {
  loading.value = true
  try { const res = await getArtists({ page: page.value, pageSize: 10 }); data.value = res.data.records || []; total.value = res.data.total || 0 }
  catch (e) { message.error(e.message) } finally { loading.value = false }
}

async function handleSave() {
  if (!form.value.name) { message.warning('歌手名不能为空'); return }
  try {
    if (isEdit.value) { await updateArtist(form.value.id, form.value) } else { await createArtist(form.value) }
    message.success(isEdit.value ? '更新成功' : '添加成功'); showModal.value = false; loadData()
  } catch (e) { message.error(e.message) }
}
async function handleDelete(id) { try { await deleteArtist(id); message.success('已删除'); loadData() } catch (e) { message.error(e.message) } }

onMounted(loadData)
</script>

<template>
  <n-card style="border-radius: 12px;">
    <n-space justify="end" style="margin-bottom: 16px;"><n-button type="primary" @click="isEdit = false; form = { name: '', region: '华语', avatar: '', description: '' }; showModal = true">添加歌手</n-button></n-space>
    <n-data-table :columns="columns" :data="data" :loading="loading" :pagination="{ page, pageSize: 10, pageCount: Math.ceil(total / 10), onChange: p => { page = p; loadData() } }" :row-key="r => r.id" />
  </n-card>
  <n-modal v-model:show="showModal" preset="card" :title="isEdit ? '编辑歌手' : '添加歌手'" style="width: 500px;">
    <n-form :model="form" label-placement="left" label-width="70">
      <n-form-item label="歌手名"><n-input v-model:value="form.name" /></n-form-item>
      <n-form-item label="地区"><n-select v-model:value="form.region" :options="['华语','欧美','日韩','其他'].map(v=>({label:v,value:v}))" /></n-form-item>
      <n-form-item label="头像URL"><n-input v-model:value="form.avatar" placeholder="图片链接" /></n-form-item>
      <n-form-item label="简介"><n-input v-model:value="form.description" type="textarea" :rows="3" /></n-form-item>
    </n-form>
    <template #action><n-space justify="end"><n-button @click="showModal = false">取消</n-button><n-button type="primary" @click="handleSave">确定</n-button></n-space></template>
  </n-modal>
</template>
