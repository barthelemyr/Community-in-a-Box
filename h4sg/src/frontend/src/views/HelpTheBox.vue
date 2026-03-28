<template>
  <div class="min-h-screen flex flex-col px-5 pb-10 pt-4">

    <!-- ── SCANNING ──────────────────────────────────────────────── -->
    <div v-if="mode === 'scanning'" class="flex-1 flex flex-col gap-4">

      <!-- Title + count row -->
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <FitTitle tag="h2" :max="36" style="color: #E87D4A;">{{ t('helpPage.title') }}</FitTitle>
          <p class="text-xs text-gray-500 mt-1">{{ t('helpPage.thankYou') }}</p>
        </div>
        <div class="text-right flex-shrink-0 pt-1">
          <span class="font-black text-3xl" style="color: #2a7a6e;">{{ scannedList.length }}</span>
          <p class="text-xs font-medium text-gray-500 leading-tight">{{ t('helpPage.scannedSoFar') }}</p>
        </div>
      </div>

      <!-- Scanner -->
      <div class="relative rounded-xl overflow-hidden bg-black" style="aspect-ratio: 4/3; max-height: 260px;">
        <video ref="videoEl" class="w-full h-full object-cover" autoplay muted playsinline />
        <div class="absolute inset-0 pointer-events-none">
          <span class="scanner-bracket top-3 left-3 border-t-4 border-l-4"></span>
          <span class="scanner-bracket top-3 right-3 border-t-4 border-r-4"></span>
          <span class="scanner-bracket bottom-3 left-3 border-b-4 border-l-4"></span>
          <span class="scanner-bracket bottom-3 right-3 border-b-4 border-r-4"></span>
          <div class="scanner-line"></div>
        </div>
      </div>
      <p class="text-center text-sm text-gray-500">{{ t('helpPage.scanning') }}</p>

      <!-- Scan feedback -->
      <div
        v-if="scanFeedback"
        class="rounded-xl px-4 py-3 text-center font-bold text-sm"
        :class="scanFeedback.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-700'"
      >
        {{ scanFeedback.message }}
      </div>

      <!-- Camera error -->
      <div v-if="cameraError" class="bg-red-50 rounded-xl p-4 text-center">
        <p class="text-red-700 font-semibold text-sm">{{ cameraError }}</p>
      </div>

      <!-- Running list of scanned books -->
      <ul v-if="scannedList.length" class="flex flex-col gap-2 overflow-y-auto" style="max-height: 220px;">
        <li
          v-for="(entry, i) in [...scannedList].reverse()" :key="entry.isbn"
          class="bg-white/60 rounded-xl px-4 py-2 flex items-center gap-3"
        >
          <span class="text-xs font-mono text-gray-400 w-5 text-right flex-shrink-0">
            {{ scannedList.length - i }}
          </span>
          <p class="font-bold text-gray-900 text-sm truncate min-w-0 flex-1">{{ entry.isbn }}</p>
          <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </li>
      </ul>

      <!-- Finish button -->
      <div class="mt-auto pt-2">
        <button @click="finish" class="btn-confirm w-full">
          {{ t('helpPage.finish') }}
        </button>
      </div>
    </div>

    <!-- ── DONE ───────────────────────────────────────────────────── -->
    <div v-else-if="mode === 'done'" class="flex-1 flex flex-col items-center justify-center gap-6">
      <div class="w-16 h-16 rounded-full flex items-center justify-center" style="background-color: #2a7a6e;">
        <svg class="w-9 h-9 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <div class="text-center">
        <p class="font-black text-gray-900 text-2xl">{{ t('helpPage.done') }}</p>
        <p class="text-gray-600 mt-1">
          {{ t('helpPage.countResult') }}: <span class="font-black text-gray-900">{{ doneCount }}</span>
        </p>
      </div>
      <button @click="restart" class="btn-outline w-full max-w-xs">
        {{ t('helpPage.scanAgain') }}
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { BrowserMultiFormatReader } from '@zxing/browser'
import { BarcodeFormat, DecodeHintType } from '@zxing/library'
import { useLocale } from '../composables/useLocale.js'
import FitTitle from '../components/FitTitle.vue'

const route = useRoute()
const boxId = route.params.id
const { t } = useLocale()

const mode = ref('scanning')
const scannedList = ref([])
const doneCount = ref(0)
const cameraError = ref(null)
const scanFeedback = ref(null)
let feedbackTimer = null

function showFeedback(message, type) {
  clearTimeout(feedbackTimer)
  scanFeedback.value = { message, type }
  feedbackTimer = setTimeout(() => { scanFeedback.value = null }, 2000)
}

// ── Scanner ────────────────────────────────────────────────────────
const videoEl = ref(null)
let reader = null

const hints = new Map()
hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.EAN_13, BarcodeFormat.EAN_8])
hints.set(DecodeHintType.TRY_HARDER, true)

async function startScanner() {
  cameraError.value = null
  try {
    reader = new BrowserMultiFormatReader(hints)
    await reader.decodeFromConstraints(
      { video: { facingMode: 'environment' } },
      videoEl.value,
      (result) => {
        if (result) handleScan(result.getText())
      },
    )
  } catch (err) {
    cameraError.value = err?.name === 'NotAllowedError'
      ? t('helpPage.permissionDenied')
      : t('helpPage.cameraError')
  }
}

function stopScanner() {
  if (reader) {
    BrowserMultiFormatReader.releaseAllStreams()
    reader = null
  }
}

function handleScan(isbn) {
  const alreadyScanned = scannedList.value.some((b) => b.isbn === isbn)
  if (alreadyScanned) {
    showFeedback(t('helpPage.alreadyScanned'), 'warn')
    return
  }
  scannedList.value.push({ isbn })
  // TODO: POST /boxes/{boxId}/books/{isbn}/seen
  showFeedback(`✓ ${isbn}`, 'success')
}

function finish() {
  stopScanner()
  doneCount.value = scannedList.value.length
  // TODO: POST /boxes/{boxId}/bookCount { count: doneCount }
  mode.value = 'done'
}

function restart() {
  scannedList.value = []
  doneCount.value = 0
  cameraError.value = null
  mode.value = 'scanning'
  setTimeout(startScanner, 100)
}

onMounted(() => setTimeout(startScanner, 100))
onUnmounted(() => stopScanner())
</script>
