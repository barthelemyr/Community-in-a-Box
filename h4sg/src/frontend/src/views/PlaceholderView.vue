<template>
  <div class="min-h-screen flex flex-col" style="background-color: #F0EDE0;">
    <!-- Home page link -->
    <div class="p-4">
      <button
        @click="goHome"
        class="font-bold underline text-gray-800 hover:opacity-70 transition-opacity"
      >
        {{ t('homePage') }}
      </button>
    </div>

    <!-- Page content -->
    <div class="flex-1 flex flex-col md:flex-row items-center justify-center gap-8 px-8 pb-12">
      <h1
        class="font-black uppercase tracking-widest text-left leading-none whitespace-pre-line"
        :style="{ color: titleColor, fontSize: 'clamp(2.5rem, 10vw, 5rem)' }"
      >
        {{ t(`pages.${route.name}`) }}
      </h1>

      <p class="text-gray-600 text-lg">{{ t('comingSoon') }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLocale } from '../composables/useLocale.js'

const route = useRoute()
const router = useRouter()
const { t } = useLocale()

const pageColors = {
  add:    { color: '#ffffff', bg: '#B8B0E8' },
  borrow: { color: '#ffffff', bg: '#B8B0E8' },
  books:  { color: '#E87D4A', bg: '#F0EDE0' },
  info:   { color: '#ffffff', bg: '#E87D4A' },
  games:  { color: '#E87D4A', bg: '#F0EDE0' },
  help:   { color: '#E87D4A', bg: '#F0EDE0' },
}

const pageConfig = computed(() => pageColors[route.name] ?? { color: '#E87D4A', bg: '#F0EDE0' })
const titleColor = computed(() => pageConfig.value.color)
const bgColor = computed(() => pageConfig.value.bg)

function goHome() {
  router.push({ name: 'home', params: { id: route.params.id } })
}
</script>

<style scoped>
div.min-h-screen {
  background-color: v-bind(bgColor);
}
</style>