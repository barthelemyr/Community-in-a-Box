<template>
  <div class="page-orange">

    <!-- Home page link -->
    <div class="p-4">
      <button @click="goHome" class="home-link">
        {{ t('homePage') }}
      </button>
    </div>

    <div class="flex-1 flex flex-col lg:flex-row items-center lg:items-start gap-6 px-6 pb-10 lg:px-12">

      <!-- Left: page title -->
      <div class="lg:flex-1 flex items-center lg:items-start lg:pt-8">
        <h1 class="page-title-sub text-white">
          INFO<br>ABOUT<br>BOOK
        </h1>
      </div>

      <!-- Right: scanner + result -->
      <div class="w-full lg:flex-1 flex flex-col items-center gap-4">

        <!-- Instruction (only while scanning or on error) -->
        <p v-if="state === 'scanning' || state === 'error'" class="text-center text-gray-900 font-medium max-w-sm font-mono">
          {{ t('infoPage.instruction') }}
        </p>

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
            <p class="text-center text-sm text-gray-800 mt-2">{{ t('infoPage.scanning') }}</p>
          </div>

          <!-- State: loading book data from API -->
          <div v-else-if="state === 'loading'" class="flex flex-col items-center gap-3 py-8">
            <div class="w-10 h-10 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
            <p class="text-white font-semibold">{{ t('infoPage.loading') }}</p>
          </div>

          <!-- State: book info found -->
          <div v-else-if="state === 'found'" class="flex flex-col gap-4">
            <div class="bg-white/20 rounded-2xl p-4 flex gap-4 items-start">
              <!-- Cover image -->
              <img
                v-if="book.cover"
                :src="book.cover"
                :alt="book.title"
                class="w-20 rounded-lg shadow-md flex-shrink-0 object-cover"
                style="min-height: 100px;"
                onerror="this.style.display='none'"
              />
              <!-- Book details -->
              <div class="flex flex-col gap-1 min-w-0">
                <p class="text-xs font-bold uppercase tracking-widest text-white/70">
                  {{ t('infoPage.isbnFound') }}: {{ scannedIsbn }}
                </p>
                <h2 class="text-white font-black text-lg leading-tight">{{ book.title }}</h2>
                <p v-if="book.authors" class="text-white/90 text-sm">
                  <span class="font-semibold">{{ t('infoPage.author') }}:</span> {{ book.authors }}
                </p>
                <p v-if="book.publisher" class="text-white/90 text-sm">
                  <span class="font-semibold">{{ t('infoPage.publisher') }}:</span> {{ book.publisher }}
                </p>
                <p v-if="book.year" class="text-white/90 text-sm">
                  <span class="font-semibold">{{ t('infoPage.published') }}:</span> {{ book.year }}
                </p>
              </div>
            </div>
            <button @click="resetScanner" class="btn-outline w-full">
              {{ t('infoPage.scanAgain') }}
            </button>
          </div>

          <!-- State: ISBN not found in Open Library -->
          <div v-else-if="state === 'not-found'" class="flex flex-col gap-4">
            <div class="bg-white/20 rounded-2xl p-5 text-center">
              <p class="text-xs font-bold uppercase tracking-widest text-white/70 mb-1">
                {{ t('infoPage.isbnFound') }}: {{ scannedIsbn }}
              </p>
              <p class="text-white font-semibold">{{ t('infoPage.notFound') }}</p>
            </div>
            <button @click="resetScanner" class="btn-outline w-full">
              {{ t('infoPage.scanAgain') }}
            </button>
          </div>

          <!-- State: camera error -->
          <div v-else-if="state === 'error'" class="bg-white/20 rounded-2xl p-5 text-center">
            <p class="text-white font-semibold">{{ cameraError }}</p>
          </div>

          <!-- State: manual entry -->
          <div v-if="state === 'manual'" class="flex flex-col gap-3 w-full">
            <input
              v-model="manualIsbn"
              type="text"
              inputmode="numeric"
              :placeholder="t('infoPage.manualPlaceholder')"
              class="w-full rounded-2xl px-4 py-3 text-gray-900 font-mono text-lg border-2 border-gray-700 bg-white/60 focus:outline-none focus:bg-white/80"
            />
            <div class="flex gap-3">
              <button
                @click="submitManual"
                :disabled="!manualIsbn.trim()"
                class="btn-confirm flex-1"
              >{{ t('infoPage.submitIsbn') }}</button>
              <button
                @click="state = 'scanning'; startScanner()"
                class="btn-outline flex-1"
              >{{ t('infoPage.cancel') }}</button>
            </div>
          </div>

        </div>

        <!-- Enter manually button (shown while scanning or on error) -->
        <div v-if="state === 'scanning' || state === 'error'" class="w-full max-w-sm">
          <button @click="showManual" class="btn-outline w-full">
            {{ t('infoPage.enterManually') }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BrowserMultiFormatReader } from '@zxing/browser'
import { BarcodeFormat, DecodeHintType } from '@zxing/library'
import { useLocale } from '../composables/useLocale.js'

const route = useRoute()
const router = useRouter()
const { t } = useLocale()

const boxId = route.params.id
const videoEl = ref(null)

// state: 'scanning' | 'loading' | 'found' | 'not-found' | 'manual' | 'error'
const state = ref('scanning')
const scannedIsbn = ref('')
const manualIsbn = ref('')
const cameraError = ref('')
const book = ref({ title: '', authors: '', publisher: '', year: '', cover: '' })

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
          const isbn = result.getText()
          stopScanner()
          lookupIsbn(isbn)
        }
      },
    )
  } catch (err) {
    stopScanner()
    cameraError.value = err?.name === 'NotAllowedError'
      ? t('infoPage.permissionDenied')
      : t('infoPage.cameraError')
    state.value = 'error'
  }
}

function stopScanner() {
  if (reader) {
    BrowserMultiFormatReader.releaseAllStreams()
    reader = null
  }
}

async function lookupIsbn(isbn) {
  scannedIsbn.value = isbn
  state.value = 'loading'

  try {
    // Open Library Books API — free, no key required
    const url = `https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&format=json&jscmd=data`
    const res = await fetch(url)
    const data = await res.json()
    const entry = data[`ISBN:${isbn}`]

    if (!entry) {
      state.value = 'not-found'
      return
    }

    book.value = {
      title:     entry.title ?? '',
      authors:   entry.authors?.map((a) => a.name).join(', ') ?? '',
      publisher: entry.publishers?.map((p) => p.name).join(', ') ?? '',
      year:      entry.publish_date ?? '',
      cover:     entry.cover?.medium ?? `https://covers.openlibrary.org/b/isbn/${isbn}-M.jpg`,
    }
    state.value = 'found'
  } catch {
    state.value = 'not-found'
  }
}

function resetScanner() {
  scannedIsbn.value = ''
  book.value = { title: '', authors: '', publisher: '', year: '', cover: '' }
  startScanner()
}

function showManual() {
  stopScanner()
  state.value = 'manual'
}

function submitManual() {
  const isbn = manualIsbn.value.trim()
  if (!isbn) return
  stopScanner()
  manualIsbn.value = ''
  lookupIsbn(isbn)
}

function goHome() {
  stopScanner()
  router.push({ name: 'home', params: { id: boxId } })
}

onMounted(() => startScanner())
onUnmounted(() => stopScanner())
</script>
