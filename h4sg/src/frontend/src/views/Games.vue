<template>
  <div class="min-h-screen flex flex-col px-5 pb-10">

    <!-- ── HUB: pick a game ───────────────────────────────────────── -->
    <div v-if="screen === 'hub'" class="flex-1 flex flex-col gap-6 pt-4">
      <div>
        <FitTitle style="color: #E87D4A;">{{ t('gamesHub.title') }}</FitTitle>
        <p class="text-gray-600 font-medium mt-1">{{ t('gamesHub.subtitle') }}</p>
      </div>

      <!-- Game card: Find the Forgotten Books -->
      <div class="bg-white/60 rounded-2xl p-5 flex flex-col gap-3 shadow-sm">
        <div>
          <h2 class="font-black uppercase tracking-wider text-gray-900 text-lg">
            {{ t('gamesHub.findForgotten') }}
          </h2>
          <p class="text-gray-600 text-sm mt-1">{{ t('gamesHub.findForgottenDesc') }}</p>
        </div>
        <div class="flex items-center gap-3">
          <div class="flex gap-1">
            <span v-for="n in 3" :key="n" class="w-2 h-2 rounded-full bg-orange-400"></span>
          </div>
          <span class="text-xs text-gray-400 uppercase tracking-wider">Medium</span>
        </div>
        <button @click="startBriefing" class="btn-orange btn-action w-full mt-1">
          {{ t('gamesHub.play') }}
        </button>
      </div>

      <!-- Placeholder cards for future games -->
      <div
        v-for="game in upcomingGames" :key="game"
        class="bg-white/30 rounded-2xl p-5 flex items-center justify-between opacity-50"
      >
        <span class="font-bold uppercase tracking-wider text-gray-700 text-sm">{{ game }}</span>
        <span class="text-xs text-gray-400 uppercase tracking-wider border border-gray-300 rounded-full px-2 py-0.5">
          {{ t('gamesHub.comingSoon') }}
        </span>
      </div>
    </div>

    <!-- ── BRIEFING: show the list before starting ────────────────── -->
    <div v-else-if="screen === 'briefing'" class="flex-1 flex flex-col gap-5 pt-4">
      <div>
        <FitTitle style="color: #E87D4A;">{{ t('findForgotten.briefingTitle') }}</FitTitle>
        <p class="text-gray-700 mt-2 font-medium">{{ t('findForgotten.briefingDesc') }}</p>
      </div>

      <!-- Book checklist preview -->
      <ul class="flex flex-col gap-2">
        <li
          v-for="book in targetBooks" :key="book.isbn"
          class="bg-white/60 rounded-xl px-4 py-3 flex items-center gap-3"
        >
          <span class="w-6 h-6 rounded-full border-2 border-gray-300 flex-shrink-0"></span>
          <div class="min-w-0">
            <p class="font-bold text-gray-900 truncate">{{ book.title }}</p>
            <p class="text-xs text-gray-500">
              {{ book.author }} &middot;
              <span class="text-red-500">{{ t('findForgotten.lastSeen') }}: {{ book.lastSeen }}</span>
            </p>
          </div>
        </li>
      </ul>

      <button @click="startGame" class="btn-confirm w-full mt-auto">
        {{ t('findForgotten.startGame') }}
      </button>
    </div>

    <!-- ── PLAYING: scanner + live checklist ─────────────────────── -->
    <div v-else-if="screen === 'playing'" class="flex-1 flex flex-col gap-4 pt-4">

      <!-- Progress bar + timer -->
      <div class="flex items-center justify-between">
        <span class="font-black text-gray-800 text-lg">
          {{ foundCount }} / {{ targetBooks.length }}
          <span class="text-sm font-medium text-gray-500">{{ t('findForgotten.found') }}</span>
        </span>
        <span class="font-mono font-bold text-gray-700 text-lg">{{ formattedTime }}</span>
      </div>
      <div class="w-full h-2 rounded-full bg-white/40">
        <div
          class="h-2 rounded-full transition-all duration-500"
          style="background-color: #2a7a6e;"
          :style="{ width: `${(foundCount / targetBooks.length) * 100}%` }"
        ></div>
      </div>

      <!-- Scanner -->
      <div class="relative rounded-xl overflow-hidden bg-black" style="aspect-ratio: 4/3; max-height: 220px;">
        <video ref="videoEl" class="w-full h-full object-cover" autoplay muted playsinline />
        <div class="absolute inset-0 pointer-events-none">
          <span class="scanner-bracket top-3 left-3 border-t-4 border-l-4"></span>
          <span class="scanner-bracket top-3 right-3 border-t-4 border-r-4"></span>
          <span class="scanner-bracket bottom-3 left-3 border-b-4 border-l-4"></span>
          <span class="scanner-bracket bottom-3 right-3 border-b-4 border-r-4"></span>
          <div class="scanner-line"></div>
        </div>
      </div>

      <!-- Scan feedback flash -->
      <div
        v-if="scanFeedback"
        class="rounded-xl px-4 py-3 text-center font-bold text-sm transition-all"
        :class="scanFeedback.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-700'"
      >
        {{ scanFeedback.message }}
      </div>

      <!-- Live checklist -->
      <ul class="flex flex-col gap-2 overflow-y-auto" style="max-height: 280px;">
        <li
          v-for="book in targetBooks" :key="book.isbn"
          class="rounded-xl px-4 py-3 flex items-center gap-3 transition-all"
          :class="book.found ? 'bg-green-100' : 'bg-white/60'"
        >
          <!-- Checkmark or empty circle -->
          <div
            class="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center"
            :class="book.found ? 'bg-green-500' : 'border-2 border-gray-300'"
          >
            <svg v-if="book.found" class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div class="min-w-0 flex-1">
            <p class="font-bold text-sm truncate" :class="book.found ? 'line-through text-gray-400' : 'text-gray-900'">
              {{ book.title }}
            </p>
            <p class="text-xs text-gray-400 truncate">{{ book.author }}</p>
          </div>
        </li>
      </ul>

      <button @click="giveUp" class="btn-outline w-full text-sm">
        {{ t('findForgotten.giveUp') }}
      </button>
    </div>

    <!-- ── FINISHED: results ──────────────────────────────────────── -->
    <div v-else-if="screen === 'finished'" class="flex-1 flex flex-col items-center justify-center gap-6 py-8">
      <div class="text-center">
        <FitTitle style="color: #E87D4A;">{{ t('findForgotten.finishedTitle') }}</FitTitle>
        <p class="text-gray-700 mt-2 font-medium text-lg">
          {{ t('findForgotten.finishedDesc').replace('{found}', foundCount).replace('{total}', targetBooks.length) }}
        </p>
      </div>

      <!-- Stats card -->
      <div class="bg-white/60 rounded-2xl p-6 w-full max-w-xs flex flex-col gap-4 shadow-sm">
        <div class="flex justify-between items-center">
          <span class="text-gray-500 font-medium">{{ t('findForgotten.timeTaken') }}</span>
          <span class="font-black text-gray-900 text-xl font-mono">{{ formattedTime }}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-gray-500 font-medium">{{ t('findForgotten.found') }}</span>
          <span class="font-black text-xl" style="color: #2a7a6e;">
            {{ foundCount }} / {{ targetBooks.length }}
          </span>
        </div>
        <!-- Score bar -->
        <div class="w-full h-3 rounded-full bg-gray-200">
          <div
            class="h-3 rounded-full"
            style="background-color: #2a7a6e; transition: width 1s ease;"
            :style="{ width: `${(foundCount / targetBooks.length) * 100}%` }"
          ></div>
        </div>
      </div>

      <div class="flex flex-col gap-3 w-full max-w-xs">
        <button @click="startBriefing" class="btn-confirm w-full">
          {{ t('findForgotten.playAgain') }}
        </button>
        <button @click="screen = 'hub'; stopScanner()" class="btn-outline w-full">
          {{ t('gamesHub.title') }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { BrowserMultiFormatReader } from '@zxing/browser'
import { BarcodeFormat, DecodeHintType } from '@zxing/library'
import { useLocale } from '../composables/useLocale.js'
import FitTitle from '../components/FitTitle.vue'

const route = useRoute()
const boxId = route.params.id
const { t } = useLocale()

// ── Screen state ───────────────────────────────────────────────────
// 'hub' | 'briefing' | 'playing' | 'finished'
const screen = ref('hub')

// target books with reactive `found` flag
const targetBooks = ref([])
const loadError = ref('')

async function loadOldestBooks() {
  loadError.value = ''
  try {
    const res = await fetch(`/api/shelves/${boxId}/books`)
    if (!res.ok) throw new Error()
    const all = await res.json()
    // API returns newest first — take last 10 (oldest)
    const oldest = all.slice(-10)
    targetBooks.value = oldest.map((b) => ({
      isbn: b.isbn,
      title: b.title,
      author: b.author ?? '',
      lastSeen: b.last_scanned ? new Date(b.last_scanned).toLocaleDateString() : '—',
      found: false,
    }))
  } catch {
    loadError.value = true
  }
}

const upcomingGames = ['Author Hunt', 'Count the Box']

// ── Timer ──────────────────────────────────────────────────────────
const elapsedSeconds = ref(0)
let timerInterval = null

const formattedTime = computed(() => {
  const m = Math.floor(elapsedSeconds.value / 60).toString().padStart(2, '0')
  const s = (elapsedSeconds.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

function startTimer() {
  elapsedSeconds.value = 0
  timerInterval = setInterval(() => elapsedSeconds.value++, 1000)
}

function stopTimer() {
  clearInterval(timerInterval)
  timerInterval = null
}

// ── Scanner ────────────────────────────────────────────────────────
const videoEl = ref(null)
let reader = null

const hints = new Map()
hints.set(DecodeHintType.POSSIBLE_FORMATS, [BarcodeFormat.EAN_13, BarcodeFormat.EAN_8])
hints.set(DecodeHintType.TRY_HARDER, true)

// Feedback flash shown briefly after each scan
const scanFeedback = ref(null)
let feedbackTimer = null

function showFeedback(message, type) {
  clearTimeout(feedbackTimer)
  scanFeedback.value = { message, type }
  feedbackTimer = setTimeout(() => { scanFeedback.value = null }, 2000)
}

async function startScanner() {
  try {
    reader = new BrowserMultiFormatReader(hints)
    await reader.decodeFromConstraints(
      { video: { facingMode: 'environment' } },
      videoEl.value,
      (result) => {
        if (result) handleScan(result.getText())
      },
    )
  } catch {
    // Camera unavailable — game still playable via the checklist (manual fallback omitted for games)
  }
}

function stopScanner() {
  if (reader) {
    BrowserMultiFormatReader.releaseAllStreams()
    reader = null
  }
}

// ── Game logic ─────────────────────────────────────────────────────
const foundCount = computed(() => targetBooks.value.filter((b) => b.found).length)

function handleScan(isbn) {
  const book = targetBooks.value.find((b) => b.isbn === isbn)
  if (!book) {
    showFeedback(t('findForgotten.notInList'), 'error')
    return
  }
  if (book.found) {
    showFeedback(t('findForgotten.alreadyFound'), 'error')
    return
  }
  book.found = true
  showFeedback(`✓ ${book.title}`, 'success')
  const normalized = isbn.replace(/[\s-]/g, '')
  await fetch(`/api/shelves/${boxId}/books/${normalized}`, { method: 'PUT' })

  if (foundCount.value === targetBooks.value.length) {
    finishGame()
  }
}

async function startBriefing() {
  stopScanner()
  stopTimer()
  await loadOldestBooks()
  screen.value = 'briefing'
}

function startGame() {
  screen.value = 'playing'
  startTimer()
  // Scanner starts after the DOM renders the <video> element
  setTimeout(startScanner, 100)
}

function giveUp() {
  stopScanner()
  stopTimer()
  screen.value = 'finished'
}

function finishGame() {
  stopScanner()
  stopTimer()
  screen.value = 'finished'
}

onUnmounted(() => {
  stopScanner()
  stopTimer()
})
</script>
