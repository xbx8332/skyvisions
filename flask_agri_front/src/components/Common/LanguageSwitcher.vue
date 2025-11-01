<template>
    <div>
      <button @click="setLanguage('zh')">中文</button>
      <button @click="setLanguage('en')">English</button>
    </div>
  </template>
  
  <script setup lang="ts">
  import { useI18n } from 'vue-i18n'
  
  const { locale } = useI18n()
  
  const setLanguage = (lang: string) => {
    locale.value = lang
  }
  </script>