<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useTemaStore } from '@/stores/tema'

const tema = useTemaStore()
onMounted(() => tema.init())
</script>

<template>
  <RouterView v-slot="{ Component }">
    <transition name="page" mode="out-in">
      <component :is="Component" />
    </transition>
  </RouterView>
</template>

<style>
@import '@/style/main.css';
</style>
