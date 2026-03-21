<script setup>
import { NConfigProvider, NMessageProvider, zhCN, dateZhCN } from 'naive-ui'
import { RouterView } from 'vue-router'
</script>

<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <RouterView />
    </n-message-provider>
  </n-config-provider>
</template>
