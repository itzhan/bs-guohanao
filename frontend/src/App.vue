<script setup>
import { NConfigProvider, NMessageProvider, darkTheme, zhCN, dateZhCN } from 'naive-ui'
import { RouterView } from 'vue-router'

const themeOverrides = {
  common: {
    primaryColor: '#6C5CE7',
    primaryColorHover: '#7C6FF0',
    primaryColorPressed: '#5A4BD6',
    primaryColorSuppl: '#6C5CE7',
    bodyColor: '#0D1117',
    cardColor: '#161B22',
    modalColor: '#21262D',
    popoverColor: '#21262D',
    tableColor: '#161B22',
    inputColor: 'rgba(255,255,255,0.04)',
    actionColor: '#21262D',
    borderColor: 'rgba(255,255,255,0.08)',
    dividerColor: 'rgba(255,255,255,0.08)',
    hoverColor: 'rgba(255,255,255,0.06)',
    textColorBase: '#E6EDF3',
    textColor1: '#E6EDF3',
    textColor2: '#C9D1D9',
    textColor3: '#8B949E',
    textColorDisabled: '#484F58',
    placeholderColor: '#484F58',
    iconColor: '#8B949E',
    borderRadius: '8px',
    borderRadiusSmall: '6px',
    fontSize: '14px',
    successColor: '#3FB950',
    warningColor: '#D29922',
    errorColor: '#F85149',
    infoColor: '#58A6FF',
  },
  Button: {
    borderRadiusMedium: '8px',
    borderRadiusLarge: '12px',
  },
  Card: {
    borderRadius: '12px',
    borderColor: 'rgba(255,255,255,0.08)',
    color: '#161B22',
    colorEmbedded: '#0D1117',
    titleTextColor: '#E6EDF3',
    textColor: '#C9D1D9',
  },
  Input: {
    borderRadius: '8px',
    color: 'rgba(255,255,255,0.04)',
    colorFocus: 'rgba(255,255,255,0.06)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderHover: '1px solid rgba(108,92,231,0.5)',
    borderFocus: '1px solid #6C5CE7',
    boxShadowFocus: '0 0 0 2px rgba(108,92,231,0.2)',
    textColor: '#E6EDF3',
    placeholderColor: '#484F58',
    caretColor: '#6C5CE7',
  },
  Tag: {
    borderRadius: '20px',
  },
  Tabs: {
    tabTextColorLine: '#8B949E',
    tabTextColorActiveLine: '#E6EDF3',
    tabTextColorHoverLine: '#C9D1D9',
    barColor: '#6C5CE7',
    tabBorderColor: 'rgba(255,255,255,0.08)',
  },
  Pagination: {
    itemBorderColor: 'rgba(255,255,255,0.08)',
    itemTextColor: '#8B949E',
    itemTextColorActive: '#6C5CE7',
    itemBorderActive: '#6C5CE7',
    itemColorActiveHover: 'rgba(108,92,231,0.1)',
  },
  Select: {
    peers: {
      InternalSelection: {
        border: '1px solid rgba(255,255,255,0.08)',
        borderHover: '1px solid rgba(108,92,231,0.5)',
        borderFocus: '1px solid #6C5CE7',
        borderActive: '1px solid #6C5CE7',
        color: 'rgba(255,255,255,0.04)',
        textColor: '#E6EDF3',
        placeholderColor: '#484F58',
        boxShadowFocus: '0 0 0 2px rgba(108,92,231,0.2)',
      }
    }
  },
  Rate: {
    itemColor: '#484F58',
    itemColorActive: '#FD79A8',
  },
  Form: {
    labelTextColor: '#8B949E',
  },
}
</script>

<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <RouterView />
    </n-message-provider>
  </n-config-provider>
</template>
