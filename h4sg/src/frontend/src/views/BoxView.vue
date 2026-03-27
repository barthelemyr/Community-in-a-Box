<template>
  <div class="box-wrapper">
    <header>
      <div class="p-5">
        <button
          v-if="route.name !== 'boxHome'"
          @click="backToBox"
          class="font-bold underline text-gray-800 hover:opacity-70 transition-opacity"
        >
          {{ t('Back to box') }}
        </button>
      </div>
    </header>
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView, useRouter, useRoute } from 'vue-router'
import { useLocale } from '@/composables/useLocale.js'

const router = useRouter()
const route = useRoute()
const boxId = route.params.id
const { t } = useLocale()

function backToBox() {
  router.push({ name: 'boxHome', params: { id: boxId } })
}
</script>
