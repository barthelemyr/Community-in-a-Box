<template>
  <div :class="['app-layout', currentBgClass]">
    <main>
      <!-- Language switcher -->
      <div class="flex justify-between px-5 pt-4 pb-2">
        <div>
          <button
            @click="goHome"
            class="font-bold underline text-gray-800 hover:opacity-70 transition-opacity"
          >
            {{ t('Homepage') }}
          </button>
        </div>
        <nav class="flex items-center gap-1 font-bold text-sm text-gray-900">
          <template v-for="(lang, i) in languages" :key="lang.code">
            <button
              @click="setLang(lang.code)"
              :class="
                currentLang === lang.code
                  ? 'font-black underline'
                  : 'font-bold underline opacity-70 hover:opacity-100'
              "
              class="transition-opacity"
            >
              {{ lang.label }}
            </button>
            <span v-if="i < languages.length - 1" class="opacity-60 select-none">|</span>
          </template>
        </nav>
      </div>
    </main>
    <RouterView />
    <footer></footer>
  </div>
</template>

<script setup>
// 2. Imported useRoute and computed
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useLocale } from '@/composables/useLocale.js'

// 3. Setup the route and the computed property
const route = useRoute()
const router = useRouter()
const { currentLang, languages, setLang, t } = useLocale()

function goHome() {
  router.push({ name: 'home' })
}

const currentBgClass = computed(() => {
  // Returns the class from your router, or a default empty string/class if none is set
  return route.meta.bgClass || ''
})
</script>

<style>
/* Add a smooth transition so the color fades nicely when you click links */
.app-layout {
  min-height: 100vh;
  transition: background-color 0.3s ease;
}

/* Define your purple class somewhere in your CSS! */
.page-purple {
  background-color: #e6e6fa; /* Or whatever purple you like */
}
</style>
