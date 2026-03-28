<template>
  <div class="page-purple">
    <div class="flex-1 flex flex-col lg:flex-row items-center lg:items-start gap-6 px-6 pb-10 lg:px-12">

      <!-- Left: page title -->
      <div class="w-full lg:flex-1 flex items-center lg:items-start lg:pt-8">
        <FitTitle class="text-white">BORROW<br>A BOOK</FitTitle>
      </div>

      <!-- Right: scanner area -->
      <div class="w-full lg:flex-1 flex flex-col items-center gap-4">

        <!-- Instruction text -->
        <p class="text-center text-gray-800 font-medium max-w-sm font-mono">
          {{ t('borrowPage.instruction') }}
        </p>

        <!-- Scanner / result area -->
        <div class="w-full max-w-sm">

          <!-- State: scanning -->
          <div v-if="state === 'scanning'" class="relative">
            <div class="relative rounded-lg overflow-hidden bg-black" style="aspect-ratio: 4/3;">
              <video ref="videoEl" class="w-full h-full object-cover" autoplay muted playsinline />
              <div class="absolute inset-0 pointer-events-none">
                <span class="scanner-bracket top-3 left-3 border-t-4 border-l-4"></span>
                <span class="scanner-bracket top-3 right-3 border-t-4 border-r-4"></span>
                <span class="scanner-bracket bottom-3 left-3 border-b-4 border-l-4"></span>
                <span class="scanner-bracket bottom-3 right-3 border-b-4 border-r-4"></span>
                <div class="scanner-line"></div>
              </div>
            </div>
            <p class="text-center text-sm text-gray-700 mt-2">{{ t('borrowPage.scanning') }}</p>
          </div>

          <!-- State: ISBN found — confirm -->
          <div v-else-if="state === 'found'" class="flex flex-col items-center gap-4 py-4">
            <div class="bg-white/40 rounded-2xl p-5 w-full text-center">
              <p class="text-xs font-bold uppercase tracking-widest text-gray-600 mb-1">
                {{ t('borrowPage.isbnFound') }}
              </p>
              <p class="text-2xl font-black text-gray-900 tracking-widest">{{ scannedIsbn }}</p>
            </div>
            <p class="text-gray-800 font-semibold text-center">
              {{ t('borrowPage.confirmBorrow') }} №{{ boxId }}
            </p>
            <div class="flex gap-3 w-full">
              <button @click="confirmBorrow" :disabled="submitting" class="btn-confirm flex-1 disabled:opacity-50">
                {{ submitting ? '…' : t('borrowPage.confirm') }}
              </button>
              <button @click="resetScanner" :disabled="submitting" class="btn-outline flex-1 disabled:opacity-50">
                {{ t('borrowPage.scanAgain') }}
              </button>
            </div>
            <p v-if="submitError" class="text-red-800 font-semibold text-sm text-center">{{ submitError }}</p>
          </div>

          <!-- State: camera error -->
          <div v-else-if="state === 'error'" class="bg-white/30 rounded-2xl p-5 text-center">
            <p class="text-gray-800 font-semibold mb-2">{{ cameraError }}</p>
          </div>

          <!-- State: manual entry -->
          <div v-if="state === 'manual'" class="flex flex-col gap-3 w-full">
            <input
              v-model="manualIsbn"
              type="text"
              inputmode="numeric"
              :placeholder="t('borrowPage.manualPlaceholder')"
              class="w-full rounded-2xl px-4 py-3 text-gray-900 font-mono text-lg border-2 border-gray-700 bg-white/60 focus:outline-none focus:bg-white/80"
            />
            <div class="flex gap-3">
              <button
                @click="submitManual"
                :disabled="!manualIsbn.trim()"
                class="btn-confirm flex-1"
              >{{ t('borrowPage.submitIsbn') }}</button>
              <button
                @click="cancelManual"
                class="btn-outline flex-1"
              >{{ t('borrowPage.cancel') }}</button>
            </div>
          </div>

        </div>

        <!-- Bottom action buttons -->
        <div v-if="state === 'scanning' || state === 'error'" class="flex gap-3 w-full max-w-sm mt-2">
          <button @click="showManual" class="btn-outline flex-1">
            {{ t('borrowPage.enterManually') }}
          </button>
          <button class="btn-outline flex-1">
            {{ t('borrowPage.readReviews') }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BrowserMultiFormatReader } from '@zxing/browser'
import { BarcodeFormat, DecodeHintType } from '@zxing/library'
import { useLocale } from '../composables/useLocale.js'
import FitTitle from '../components/FitTitle.vue'

const route = useRoute()
const router = useRouter()
const { t } = useLocale()

const boxId = route.params.id
const videoEl = ref(null)

// state: 'scanning' | 'found' | 'manual' | 'error'
const state = ref('scanning')
const scannedIsbn = ref('')
const manualIsbn = ref('')
const cameraError = ref('')
const submitting = ref(false)
const submitError = ref('')

let reader = null

const hints = new Map()
hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.EAN_13, BarcodeFormat.EAN_8])
hints.set(DecodeHintType.TRY_HARDER, true)

async function startScanner() {
  state.value = 'scanning'
  try {
    reader = new BrowserMultiFormatReader(hints)
    await reader.decodeFromConstraints(
      { video: { facingMode: 'environment' } },
      videoEl.value,
      (result) => {
        if (result) {
          scannedIsbn.value = result.getText()
          stopScanner()
          state.value = 'found'
        }
      },
    )
  } catch (err) {
    stopScanner()
    cameraError.value = err?.name === 'NotAllowedError'
      ? t('borrowPage.permissionDenied')
      : t('borrowPage.cameraError')
    state.value = 'error'
  }
}

function stopScanner() {
  if (reader) {
    BrowserMultiFormatReader.releaseAllStreams()
    reader = null
  }
}

function resetScanner() {
  scannedIsbn.value = ''
  startScanner()
}

function showManual() {
  stopScanner()
  state.value = 'manual'
}

async function cancelManual() {
  manualIsbn.value = ''
  state.value = 'scanning'
  await nextTick()
  startScanner()
}

function submitManual() {
  const isbn = manualIsbn.value.trim()
  if (!isbn) return
  scannedIsbn.value = isbn
  state.value = 'found'
}

async function confirmBorrow() {
  submitting.value = true
  submitError.value = ''
  const isbn = scannedIsbn.value.replace(/[\s-]/g, '')
  try {
    const res = await fetch(`/api/shelves/${boxId}/books/${isbn}`, { method: 'DELETE' })
    if (!res.ok) throw new Error(res.status)
    goHome()
  } catch {
    submitError.value = t('borrowPage.submitError')
    submitting.value = false
  }
}

function goHome() {
  stopScanner()
  router.push({ name: 'boxHome', params: { id: boxId } })
}

onMounted(() => startScanner())
onUnmounted(() => stopScanner())
</script>
