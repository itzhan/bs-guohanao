<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NSpace, NButton, NInput, NPopconfirm, NModal, NForm, NFormItem, useMessage } from 'naive-ui'
import { getGenres, createGenre, deleteGenre } from '../../api'

const message = useMessage()
const data = ref([])
const showModal = ref(false)
const form = ref({ name: '', description: '' })

const columns = [
  { title: '流派名称', key: 'name' },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '操作', key: 'actions', width: 100, render: (row) =>
    h(NPopconfirm, { onPositiveClick: () => handleDelete(row.id) }, {
      trigger: () => h(NButton, { size: 'small', tertiary: true, type: 'error' }, { default: () => '删除' }),
      default: () => '确定删除该流派？'
    })
  }
]

async function loadData() { try { const res = await getGenres(); data.value = res.data || [] } catch (e) { message.error(e.message) } }
async function handleSave() {
  if (!form.value.name) { message.warning('流派名不能为空'); return }
  try { await createGenre(form.value); message.success('添加成功'); showModal.value = false; loadData() } catch (e) { message.error(e.message) }
}
async function handleDelete(id) { try { await deleteGenre(id); message.success('已删除'); loadData() } catch (e) { message.error(e.message) } }

onMounted(loadData)
</script>

<template>
  <n-card style="border-radius: 12px;">
    <n-space justify="end" style="margin-bottom: 16px;"><n-button type="primary" @click="form = { name: '', description: '' }; showModal = true">添加流派</n-button></n-space>
    <n-data-table :columns="columns" :data="data" :row-key="r => r.id" />
  </n-card>
  <n-modal v-model:show="showModal" preset="card" title="添加流派" style="width: 400px;">
    <n-form :model="form" label-placement="left" label-width="60">
      <n-form-item label="名称"><n-input v-model:value="form.name" /></n-form-item>
      <n-form-item label="描述"><n-input v-model:value="form.description" type="textarea" :rows="2" /></n-form-item>
    </n-form>
    <template #action><n-space justify="end"><n-button @click="showModal = false">取消</n-button><n-button type="primary" @click="handleSave">确定</n-button></n-space></template>
  </n-modal>
</template>
