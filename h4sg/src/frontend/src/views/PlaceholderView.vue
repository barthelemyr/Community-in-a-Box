<template>
  <div class="min-h-screen flex flex-col" style="background-color: #F0EDE0;">
    <!-- Home page link -->
    <div class="p-4">
      <button
        @click="goHome"
        class="font-bold underline text-gray-800 hover:opacity-70 transition-opacity"
      >
        Home page
      </button>
    </div>

    <!-- Page content -->
    <div class="flex-1 flex flex-col md:flex-row items-center justify-center gap-8 px-8 pb-12">
      <h1
        class="font-black uppercase tracking-widest text-left leading-none"
        :style="{ color: titleColor, fontSize: 'clamp(2.5rem, 10vw, 5rem)' }"
      >
        {{ pageTitle }}
      </h1>

      <p class="text-gray-600 text-lg">Coming soon…</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const pageTitles = {
  'add':    { title: 'Add A\nBook',      color: '#ffffff', bg: '#B8B0E8' },
  'borrow': { title: 'Borrow\nA Book',   color: '#ffffff', bg: '#B8B0E8' },
  'books':  { title: 'Book List',        color: '#E87D4A', bg: '#F0EDE0' },
  'info':   { title: 'Info About\nBook', color: '#ffffff', bg: '#E87D4A' },
  'games':  { title: 'Games',            color: '#E87D4A', bg: '#F0EDE0' },
  'help':   { title: 'Help The\nLibrary', color: '#E87D4A', bg: '#F0EDE0' },
}

const pageConfig = computed(() => pageTitles[route.name] ?? { title: route.name, color: '#E87D4A', bg: '#F0EDE0' })
const pageTitle = computed(() => pageConfig.value.title)
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