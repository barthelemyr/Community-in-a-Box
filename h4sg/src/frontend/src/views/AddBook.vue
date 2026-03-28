<template>
  <div class="min-h-screen flex flex-col">
    <div class="flex-1 flex flex-col lg:flex-row items-center lg:items-start gap-6 px-6 pb-10 lg:px-12">

      <!-- Left: page title -->
      <div class="lg:flex-1 flex items-center lg:items-start lg:pt-8">
        <h1
          class="text-white font-black uppercase leading-none"
          style="font-size: clamp(2.5rem, 12vw, 5rem); letter-spacing: 0.06em;"
        >
          ADD A<br>BOOK
        </h1>
      </div>

      <!-- Right: scanner area -->
      <div class="w-full lg:flex-1 flex flex-col items-center gap-4">

        <!-- Instruction text -->
        <p class="text-center text-gray-800 font-medium max-w-sm" style="font-family: monospace;">
          {{ t('addBookPage.instruction') }}
        </p>

        <!-- ── Scanner / result area ── -->
        <div class="w-full max-w-sm">

          <!-- State: scanning -->
          <div v-if="state === 'scanning'" class="relative">
            <!-- Corner-bracket overlay -->
            <div class="relative rounded-lg overflow-hidden" style="aspect-ratio: 4/3; background: #000;">
              <video ref="videoEl" class="w-full h-full object-cover" autoplay muted playsinline />
              <!-- Corner brackets (CSS only, no image needed) -->
              <div class="absolute inset-0 pointer-events-none">
                <span class="bracket top-3 left-3 border-t-4 border-l-4"></span>
                <span class="bracket top-3 right-3 border-t-4 border-r-4"></span>
                <span class="bracket bottom-3 left-3 border-b-4 border-l-4"></span>
                <span class="bracket bottom-3 right-3 border-b-4 border-r-4"></span>
                <!-- Scanning line animation -->
                <div class="scan-line"></div>
              </div>
            </div>
            <p class="text-center text-sm text-gray-700 mt-2">{{ t('addBookPage.scanning') }}</p>
          </div>

          <!-- State: ISBN found — confirm -->
          <div v-else-if="state === 'found'" class="flex flex-col items-center gap-4 py-4">
            <div class="bg-white/40 rounded-2xl p-5 w-full text-center">
              <p class="text-xs font-bold uppercase tracking-widest text-gray-600 mb-1">
                {{ t('addBookPage.isbnFound') }}
              </p>
              <p class="text-2xl font-black text-gray-900 tracking-widest">{{ scannedIsbn }}</p>
            </div>
            <p class="text-gray-800 font-semibold text-center">
              {{ t('addBookPage.confirmAdd') }} №{{ boxId }}
            </p>
            <div class="flex gap-3 w-full">
              <button
                @click="confirmAdd"
                class="flex-1 rounded-2xl py-4 font-bold uppercase tracking-wider text-white hover:opacity-90 active:scale-95 transition-all"
                style="background-color: #2a7a6e;"
              >{{ t('addBookPage.confirm') }}</button>
              <button
                @click="resetScanner"
                class="flex-1 rounded-2xl py-4 font-bold uppercase tracking-wider text-gray-800 border-2 border-gray-800 hover:bg-white/30 active:scale-95 transition-all"
              >{{ t('addBookPage.scanAgain') }}</button>
            </div>
          </div>

          <!-- State: camera error / permission denied -->
          <div v-else-if="state === 'error'" class="bg-white/30 rounded-2xl p-5 text-center">
            <p class="text-gray-800 font-semibold mb-2">{{ cameraError }}</p>
          </div>

          <!-- State: manual entry -->
          <div v-if="state === 'manual'" class="flex flex-col gap-3 w-full">
            <input
              v-model="manualIsbn"
              type="text"
              inputmode="numeric"
              :placeholder="t('addBookPage.manualPlaceholder')"
              class="w-full rounded-2xl px-4 py-3 text-gray-900 font-mono text-lg border-2 border-gray-700 bg-white/60 focus:outline-none focus:bg-white/80"
            />
            <div class="flex gap-3">
              <button
                @click="submitManual"
                :disabled="!manualIsbn.trim()"
                class="flex-1 rounded-2xl py-4 font-bold uppercase tracking-wider text-white hover:opacity-90 active:scale-95 transition-all disabled:opacity-40"
                style="background-color: #2a7a6e;"
              >{{ t('addBookPage.submitIsbn') }}</button>
              <button
                @click="cancelManual"
                class="flex-1 rounded-2xl py-4 font-bold uppercase tracking-wider text-gray-800 border-2 border-gray-800 hover:bg-white/30 active:scale-95 transition-all"
              >{{ t('addBookPage.cancel') }}</button>
            </div>
          </div>

        </div>

        <!-- Bottom action buttons: hidden when confirmed or in manual entry -->
        <div v-if="state === 'scanning' || state === 'error'" class="flex gap-3 w-full max-w-sm mt-2">
          <button
            @click="showManual"
            class="flex-1 rounded-2xl py-3 font-bold uppercase tracking-wider text-gray-800 border-2 border-gray-800 hover:bg-white/30 active:scale-95 transition-all text-sm"
            style="background-color: #F5F0E0;"
          >{{ t('addBookPage.enterManually') }}</button>
          <button
            class="flex-1 rounded-2xl py-3 font-bold uppercase tracking-wider text-gray-800 border-2 border-gray-800 hover:bg-white/30 active:scale-95 transition-all text-sm"
            style="background-color: #F5F0E0;"
          >{{ t('addBookPage.addReview') }}</button>
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

let reader = null

// ZXing hints: only look for EAN-13 and EAN-8 (ISBN formats)
const hints = new Map()
hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.EAN_13, BarcodeFormat.EAN_8])
hints.set(DecodeHintType.TRY_HARDER, true)

async function startScanner() {
  state.value = 'scanning'
  try {
    reader = new BrowserMultiFormatReader(hints)
    // Use the rear camera on phones (facingMode: environment)
    await reader.decodeFromConstraints(
      { video: { facingMode: 'environment' } },
      videoEl.value,
      (result, err) => {
        if (result) {
          scannedIsbn.value = result.getText()
          stopScanner()
          state.value = 'found'
        }
        // NotFoundException fires every frame when nothing is detected — ignore it
      },
    )
  } catch (err) {
    stopScanner()
    if (err?.name === 'NotAllowedError') {
      cameraError.value = t('addBookPage.permissionDenied')
    } else {
      cameraError.value = t('addBookPage.cameraError')
    }
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

function confirmAdd() {
  // TODO: POST to backend API /boxes/{boxId}/books with { isbn: scannedIsbn }
  console.log(`Adding ISBN ${scannedIsbn.value} to box ${boxId}`)
  goHome()
}

function goHome() {
  stopScanner()
  router.push({ name: 'home', params: { id: boxId } })
}

onMounted(() => startScanner())
onUnmounted(() => stopScanner())
</script>

<style scoped>
.bracket {
  position: absolute;
  width: 24px;
  height: 24px;
  border-color: white;
}

.scan-line {
  position: absolute;
  left: 10%;
  right: 10%;
  height: 2px;
  background: rgba(255, 255, 255, 0.7);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0%   { top: 15%; }
  50%  { top: 80%; }
  100% { top: 15%; }
}
</style>
